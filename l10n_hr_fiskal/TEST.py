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
from openerp.osv import fields,osv



class test_table(osv.Model):
    _name = 'testtable'
    _description ='Testing purposes table - to be removed'
    def dummy(self):
        pass   
    
    
    
    def promjena1 (self,cr,uid,id,fields,context=None):
        fields=['name','br1','br2']
        #učitam da odabrana polja 
        x_polja=self.read(cr,uid,id,fields,context=None)
        #uzmem prvu vrijenost
        xp=x_polja[0]
        x_naziv=xp['name']
        x_br1=xp['br1']
        x_br2=xp['br2']
        
        r_test1=x_br1*x_br1
        r_test2=x_naziv + '-' + str(x_br1)
        
        w_polja={'test1':r_test1,
                 'test2':r_test2}
        w_polja=self.write(cr,uid,id,w_polja)
        return w_polja
    def _neka_suma (self,cr,uid,id ,fields,arg,context=None):
        fields=['br1','br2']
        broj1=self.read(cr,uid,id,fields)[0]['br1']
        broj2=self.read(cr,uid,id,fields)[0]['br2']
        suma_br=broj1+broj2
        print suma_br
        pass
        vrati=self.write(cr,uid,id,{'suma':suma_br})
        return vrati
    
    _columns={
              'name':fields.char('name', size=25),
              'br1':fields.integer('BR1'),
              'br2':fields.integer('BR2'),
              'test1':fields.char('test1',size=25),
              'test2':fields.char('test2',size=125),
              'dane':fields.boolean('DaNe'),
              'suma':fields.function(_neka_suma,string='test sume',type='integer')
              }