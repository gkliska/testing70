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

from osv import fields, osv, orm


class res_company(osv.osv):
    _inherit = 'res.company'
    _columns = {
        'l10n_hr_base_nkd_id': fields.many2one('l10n_hr_base.nkd', 'NKD', help='Nacionalna klasifikacija djelatnosti') ,
        'porezna_uprava': fields.char('Porezna uprava', size=64),
        'porezna_ispostava': fields.char('Porezna ispostava', size=64),
        'br_obveze_mirovinsko': fields.char('Br. obveze mirovinsko', size=32, help='Broj obveze mirovinskog osiguranja'),
        'br_obveze_zdravstveno': fields.char('Br. obveze zdravstveno', size=32, help='Broj obveze zdravstvenog osiguranja'),
        'maticni_broj': fields.char('Maticni broj', size=16),
        'podnozje_ispisa': fields.char('Podnozje ispisa', size=256),
        'zaglavlje_ispisa': fields.char('Zaglavlje ispisa', size=512),
        'racun_obrazac'   :fields.char('Vrsta računa', size=32, help='Upišite "R-1" ili "R-2" ' ),
    }
    
    _defaults={ 
                'racun_obrazac':"Obrazac R-1",
                'podnozje_ispisa': "Društvo je upisano u sudski registar Trgovačkog suda u _____ pod brojem _____. Temeljni kapital društva iznosi _________kuna i uplaćen je u cijelosti. Članovi uprave:  "
              
              }
res_company()