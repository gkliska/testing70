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

import uuid
from fiskal import *

## ovo sluzi za naknadno generiranje ZKI na osnovu 
## prepisanih parametara sa računa ( na zahtjev ponovno generiranje!)

class check_zki(osv.Model):
    _name="l10n.hr.check.zki"
    _description="Provjera generiranja ZKI"
    _columns={
        'name':fields.char('TestName',size=128),
        'datum':fields.char('Datum i vrijeme', size=128),
        'broj_rac':fields.char('Broj Racuna',size=64),
        'oib':fields.char('OIB Operatera',size =32),
        'iznos':fields.char('iznos',size=32),
        # polja izvaditi na osnovu broja računa
        'r_broj':fields.char('r_br_rac', size=32),
        'r_pprostor':fields.char('r_ppr', size=32),
        'r_nap_ur':fields.char('r_nap_ur', size=32),
        ### izračunati :
        'zki':fields.char('ZKI',size=40)      
              }
    
#stage 1
    def obradi_brrac(self,cr, uid,fields,context=None):
        
        pass
#izračunati proj rac, pos jed, i br napl. uredj. iz racuna
#stage 2
# izračunaj ZKI

check_zki()