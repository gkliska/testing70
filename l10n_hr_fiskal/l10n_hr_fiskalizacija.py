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
import logging
from openerp.osv import fields, osv, orm
import datetime
##tmp iport fields
import uuid
from fiskal import *


class l10n_hr_fis_pprostor(osv.Model):
    
    _name = 'l10n_hr_fis_pprostor'
    _description = 'Podaci o poslovnim prostorima'
    
 #   def _get_log_list(self,cr,uid,ids,field_names=None, arg=False, context=None):
 #       model_pool=self.pool.get('l10n.hr.log')
 #       res=model_pool.read(cr,uid,['model','name'])
 #       return [(r['model'],r['name']) for r in res] + [('','')]
    
    _columns = {
        'name': fields.char('Naziv poslovnog prostora', size=128 ,readonly="0"),
        'oznaka_pp': fields.char('Oznaka poslovnog prostora', required="True", size=32),
        'datum_primjene': fields.datetime('Datum', help ="Datum od kojeg vrijede navedeni podaci"),
        'ulica': fields.char('Ulica', size=100),
        'kbr': fields.char('Kucni broj', size=4),
        'kbr_dodatak': fields.char('Dodatak kucnom broju', size=4),
        'posta': fields.char('Posta', size=12),
        'naselje': fields.char('Naselje', size=35),
        'opcina'   :fields.char('Naziv opcine ili grada', size=35),
        'sustav_pdv':fields.boolean('U sustavu PDV-a'),
        'radno_vrijeme' : fields.char('Radno Vrijeme', required="True", size=128),
        'sljed_racuna':fields.selection ((('N','Na nivou naplatnog uredjaja'),('P','Na nivou poslovnog prostora')),'Sljed racuna'),
        'spec':fields.char('OIB Informaticke tvrtke', required="True", size=64),
        'res_certificate_id':fields.many2one('res.certificate','res_certificate_id','Certificate',help="Select certificate for this action to complete"),
        #TODO: e sad bi ja jos ucitao podatke o certifikatu u neka function polja
        
        'res_certificate_server_id':fields.many2one('res.certificate.server', 'res_certificate_server_id','Server',help="Server na koji se pokusavamo spojiti"),
        # e tu bi dodao subform komunikacija i učitao tablicu komunikacije
        'log_ids':fields.one2many('l10n_hr_log','l10n_hr_fis_pprostor_id','Session')
                }
    
    
    
    
    _defaults = {
                 'sustav_pdv':"True"
                 }
    
    ##################################################
    ## ovo je samo test butonic, nije jos funkcionalan
    ##################################################
        
    def button_test(self,cr,uid,ids,fields,context=None):
        logs_obj=self.pool.get('l10n.hr.log')
        
        a = Fiskalizacija()
        tstamp = datetime.datetime.now()
        a.t = tstamp
        tmptime  = '%s.%s.%s %s:%s:%s' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        a.zaglavlje.DatumVrijeme = '%d.%02d.%02dT%02d:%02d:%02d' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        a.zaglavlje.IdPoruke = str(uuid.uuid4())
        a.racun.Oib = "57699704120" #ucitaj ! OIB korisnika
        a.racun.USustPdv = 'true'  ## sustav_pdv
        a.racun.DatVrijeme = a.zaglavlje.DatumVrijeme 
        a.racun.OznSlijed = 'P' ## sljed_racuna
        a.racun.BrRac.BrOznRac = '1'
        a.racun.BrRac.OznPosPr = 'TESTIRAMO' ## name !! pazi !! nesmije imati razmake u nazivu.. prije sljanaj replace ' '->'' !!!
        a.racun.BrRac.OznNapUr = '12'  ## oznaka_pp
        a.porez = a.client2.factory.create('tns:Porez')
        a.porez.Stopa = "25.00"
        a.porez.Osnovica = "100.00"
        a.porez.Iznos = "25.00"
        a.racun.Pdv.Porez.append(a.porez)

        a.racun.IznosUkupno = "125.00" # 
        a.racun.NacinPlac = "G" # Nacin placanja
        a.racun.OibOper = "57699704120"
        a.racun.NakDost = "false"  ##TODO rutina koja provjerava jel prvi puta ili ponovljeno sranje!

        a.izracunaj_zastitni_kod(tmptime)
        #odgovor_string = a.posalji()
        odgovor_string=a.posalji()
        
        odgovor_array = odgovor_string[1]
        # ... sad tu ima odgovor.Jir
        jir = odgovor_array.Jir
        
        #odgovor= odgovor_string  
        values={
                'name':'IdPoruke',
                'type':'prostor',
                'sadrzaj':jir, #odgovor,
                'timestamp':tstamp 
                }
        log_id=logs_obj.create(cr,uid,values,context=context)
        return log_id
l10n_hr_fis_pprostor()

class l10n_hr_log(osv.Model):
    _name='l10n.hr.log'
    _description='Official communicatins log'    
    def _get_log_type(self,cursor,user_id, context=None):
        return (('prostor','Prijava Prostora'),
                ('racun','Fiskalizacija racuna'),
                ('echo','Echo test message '),
                ('other','Other types ->TODO')
               )
    _columns ={
        'name': fields.char('Oznaka', size=128, help="Jedinstvena oznaka komunikacije "),
        'type': fields.selection (_get_log_type,'Log message Type'),
        'sadrzaj':fields.text('Message context'),
        'timestamp':fields.datetime('TimeStamp'),
        'l10n_hr_fis_pprostor_id':fields.many2one('l10n_hr_fis_pprostor','l10n_hr_fis_pprostor_log_id','Prostor'),
        'res_users_id':fields.many2one('res.users','res_users_id','User') ## ovo cak i netreba obzirom na create i write uide !! 
        }
l10n_hr_log()




### ovo čak i iz drugog modula moze ... ali zasad odavde..
#from fiskal import *

##tmp import

def idem_probat ():
    a = Fiskalizacija()
    a.t = time.localtime()
    tmptime  = '%d.%02d.%02d %02d:%02d:%02d' % (a.t.tm_mday, a.t.tm_mon, a.t.tm_year, a.t.tm_hour, a.t.tm_min, a.t.tm_sec)
    a.zaglavlje.DatumVrijeme = '%d.%02d.%02dT%02d:%02d:%02d' % (a.t.tm_mday, a.t.tm_mon, a.t.tm_year, a.t.tm_hour, a.t.tm_min, a.t.tm_sec)

    a.zaglavlje.IdPoruke = str(uuid.uuid4())  ## HELP NEDDED ... kak uzeti i koji uzeti.. molim primjer
  
    a.racun.Oib = "57699704120" #ucitaj ! OIB korisnika
    a.racun.USustPdv = 'true'  ## sustav_pdv
    a.racun.DatVrijeme = a.zaglavlje.DatumVrijeme 
    a.racun.OznSlijed = 'P' ## sljed_racuna
    a.racun.BrRac.BrOznRac = '1'
    a.racun.BrRac.OznPosPr = 'TESTIRAMO' ## name !! pazi !! nesmije imati razmake u nazivu.. prije sljanaj replace ' '->'' !!!
    a.racun.BrRac.OznNapUr = '12'  ## oznaka_pp

## ovo uzeti kasnije ... kad proradi echo     
    a.porez = a.client2.factory.create('tns:Porez')
    a.porez.Stopa = "25.00"
    a.porez.Osnovica = "100.00"
    a.porez.Iznos = "25.00"

    a.racun.Pdv.Porez.append(a.porez)

    a.racun.IznosUkupno = "125.00" # 
    a.racun.NacinPlac = "G" # Nacin placanja
    a.racun.OibOper = "57699704120"
    a.racun.NakDost = "false"  ##TODO rutina koja provjerava jel prvi puta ili ponovljeno sranje!

    a.izracunaj_zastitni_kod(tmptime)
    odgovor_string = a.posalji()
    odgovor_array = odgovor_string[1]

    # ... sad tu ima odgovor.Jir
    jir = odgovor_array.Jir
    return jir