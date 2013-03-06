# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_fiskal
#    Author: Davor Bojkić
#    mail:   bole@dajmi5.com
#    Copyright (C) 2012- Daj Mi 5, 
#                  http://www.dajmi5.com
#    Contributions: Hrvoje ThePython - Free Code!
#                   Goran Kliska (AT) Slobodni Programi
#                    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import fields, osv
from openerp.tools.translate import _
import uuid 
from fiskal import *
import pooler

class account_invoice(osv.Model):
    _inherit = "account.invoice"
    _columns = {
                'zki': fields.char('ZKI', size=64, readonly=True),
                'jir': fields.char('JIR',size=64 , readonly=True),
                'pprostor_id':fields.many2one('l10n.hr.pprostor','l10n_hr_pprostor_id','Pos. Prostor', help ="Pos. prostor u kojem se izdaje racun"),
                'nac_plac':fields.selection((
                                             ('G','GOTOVINA'),
                                             ('K','KARTICE'),
                                             ('C','CEKOVI'),
                                             ('T','TRANSAKCIJSKI RACUN'),
                                             ('O','OSTALO')
                                             ),
                                            'Nacin placanja', required=True)   
               }
    _defaults = {
                 'pprostor_id':'1',
                 'nac_plac':'T' # TODO : postaviti u bazi pitanje kaj da bude default!
                 }
       
    
    def button_fiscalize(self, cr, uid, id, context=None):
        if context is None:
            context = {}
            
        invoice= self.browse(cr,uid,id,context=context)[0]
        
        a = Fiskalizacija()
        start_time=a.time_formated()
        
        a.t = start_time['datum'] 
        a.zaglavlje.DatumVrijeme = start_time['datum_vrijeme']
        a.zaglavlje.IdPoruke = str(uuid.uuid4())
        
        poslao = "Račun :" + invoice.number +"\n"
        poslao=poslao +"StartTime : "+ start_time['datum_vrijeme']+ "\n"
        
        a.racun.Oib = "57699704120" #ucitaj ! OIB korisnika
        poslao=poslao + "OIB Organizacije : " +"\n"
        
        
        
        
        a.racun.DatVrijeme = start_time['datum_vrijeme']
        poslao=poslao + "Datum na računu :" + start_time['datum_racun'] + "\n"
        
        a.racun.OznSlijed = invoice.pprostor_id.sljed_racuna #'P' ## sljed_racuna
        poslao= poslao + "Sljed racuna oznaka : " + a.racun.OznSlijed + "\n"
        
        
        ## e ovoo je zajebani dio..
        ## lako je stavit sufiks na IRA broj krug., ali kad ima vise prostora 
        ## brojevi se moraju generirati shodno pos jed. i napl. uredj.
        
        
            
        a.racun.BrRac.BrOznRac = '1' #invoice.number #'1'
        a.racun.BrRac.OznPosPr = invoice.pprostor_id.oznaka_pp #'TESTIRAMO' ## name!pazi! nesmije imati razmake u nazivu.
        a.racun.BrRac.OznNapUr = '1'  ## nisam siguran odkud ovo da zvadim pa ostavim zasada 1!!!
        a.porez = a.client2.factory.create('tns:Porez')
        
        pdv="false"
        if invoice.pprostor_id.sustav_pdv:
            pdv="true"
                    
        a.racun.USustPdv = pdv #'true'  ## sustav_pdv
        poslao = poslao + "U sustavu PDV : " + pdv + "\n" 
        ### TODO : zbrojiti sve pojedine poreze i grupirati i kaj ako nije u sustavu pdv?
        
        
        poslao = poslao + "Stopa poreza : hardcode 25.00 \n" 
        a.porez.Stopa = "25.00" #"25.00"
        
        osnovica=str(invoice.amount_untaxed)
        if osnovica[-2]==".":
            osnovica=osnovica+"0"
        a.porez.Osnovica = osnovica #"100.00"
        poslao = poslao + "Osnovica : " + osnovica + "\n" 
        
        porez=str(invoice.amount_tax)
        if porez[-2]==".":
            porez=porez + "0"
        poslao = poslao + "Iznos poreza : " + porez + "\n" 
        a.porez.Iznos = porez #"25.00"
        a.racun.Pdv.Porez.append(a.porez)
        
        iznos=str(invoice.amount_total) 
        if iznos[-2]=='.':  # ovo sam dodao ako slučajno iznos završava na 0  da ne vrati gresku radi druge decimale!
                            # npr 75,00 prikze kao 75.0 ! pa dodam samo jednu nulu da prodje :)
            iznos=iznos+'0'
        a.racun.IznosUkupno = iznos # "125.00" #
        poslao = poslao + "Iznos ukupno : " + iznos + "\n" 
        
        a.racun.NacinPlac = invoice.nac_plac
        poslao = poslao + "Način Plaćanja : " + invoice.nac_plac + "\n"
        if not invoice.user_id.vat: 
            zk=self.write(cr,uid,id,{'zki':'Ovaj korisnik nema unešen OIB! izdavanje ZKI nije moguće'})
            return
        else:  a.racun.OibOper = invoice.user_id.vat[2:] #"57699704120"
        ## PAZI : ne dozvoliti dalje ako nije unešen OIB operatera!
        if not invoice.zki:
            a.racun.NakDost = "false"  ##TODO rutina koja provjerava jel prvi puta ili ponovljeno sranje!
            poslao="Slanje: 1.\n" + poslao + "\n"
        else :
            a.racun.NakDost ="true"
            poslao="Ponovljeno slanje \n" + poslao + "\n"
        
        a.izracunaj_zastitni_kod(start_time['datum_racun'])
        zk=self.write(cr,uid,id,{'zki':a.racun.ZastKod})
        
        
        odgovor_string=a.posalji_racun()
        odgovor_array = odgovor_string[0]
        # ... sad tu ima odgovor.Jir
        if odgovor_array==500 : 
            g = odgovor_string[1]
            odgovor= g.Greske.Greska
            zk=self.write(cr,uid,id,{'jir':'došlo je do greške!'})
            pass
        else :
            b=odgovor_string[1]
            jir=b.Jir
            odgovor = "JIR - " + jir
            zk=self.write(cr,uid,id,{'jir':jir})
        stop_time=a.time_formated()
        
        ##ovo sam dodao samo da vidim vrijeme odaziva...
        t_obrada=stop_time['time_stamp']-start_time['time_stamp']
        time_ob='%s.%s s'%(t_obrada.seconds, t_obrada.microseconds)
        ################################################
        
        values={
                'name':uuid.uuid4(),
                'type':'racun',
                'sadrzaj':poslao,
                'timestamp':stop_time['time_stamp'], 
                'time_obr':time_ob,
                'origin_id':invoice.id,
                'odgovor': odgovor
                }
        return self.pool.get('l10n.hr.log').create(cr,uid,values,context=context)
    
account_invoice()