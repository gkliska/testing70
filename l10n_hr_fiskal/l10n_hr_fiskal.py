# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_base
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#               http://www.slobodni-programi.hr
#    Contributions: 
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

from openerp.osv import fields, osv, orm
import datetime

class l10n_hr_fis_pprostor(osv.Model):
    
    _name = 'l10n_hr_fis_pprostor'
    _description = 'Podaci o poslovnim prostorima'
    _columns = {
        'name': fields.char('Naziv poslovnog prostora', size=128 ,readonly="0"),
        'oznaka_pp': fields.char('Oznaka poslovnog prostora', required="True", size=32),
        'slanje': fields.datetime('Datum i vrijeme slanja podataka'),
        'ulica': fields.char('Ulica', size=100),
        'kbr': fields.char('Kucni broj', size=4),
        'kbr_dodatak': fields.char('Dodatak kucnom broju', size=4),
        'posta': fields.char('Posta', size=12),
        'naselje': fields.char('Naselje', size=35),
        'opcina'   :fields.char('Naziv opcine ili grada', size=35),
        'radno_vrijeme' : fields.char('Radno Vrijeme', required="True", size=128),
        'spec':fields.char('OIB Informaticke tvrtke', required="True", size=64)
    }
    
    
l10n_hr_fis_pprostor()