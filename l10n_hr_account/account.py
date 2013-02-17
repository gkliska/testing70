# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr....
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
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

import decimal_precision as dp
import time

from osv import fields, osv

from tools.translate import _
import pooler


#definiranje željenog poziva na broj
class account_journal(osv.osv):
    _inherit = "account.journal"
    
    def _P1_P4_selection():
        return ([(''  ,'Nothing'), 
                 ('partner_code','Partner code'),
                 ('partner_id'  ,'Partner ID'),
                 ('invoice_no'  ,'Invoice Number'),
                 ('delivery_ym' ,'Delivery year and month'),
                 ('invoice_ym'  ,'Invoice year and month'),
                ])
    
    _columns = {
        'model_pnbr': fields.selection([(''  ,'Bez modela'), 
                                   ('00','00 Bez kontrole'),
                                   ('01','01 P1-P2-P3[k(P1,P2,P3)]'),
                                   ('02','02 P1-P2[k(P2)]-P3[k(P3)]'),
                                   ('03','03 P1[k(P1)]-P2[k(P2)]-P3[k(P3)]'),
                                   ('06','06 P1-P2-P3[k(P2,P3)]'),
                                   ('99','99 Bez kontrole'),
                                  ], 
                                  'Model', 
                             help='Model poziva na broj'),
        'P1_pnbr': fields.selection(_P1_P4_selection(), 'P1', help='1. polje poziva na broj.'),
        'P2_pnbr': fields.selection(_P1_P4_selection(), 'P2', help='2. polje poziva na broj.'),
        'P3_pnbr': fields.selection(_P1_P4_selection(), 'P3', help='3. polje poziva na broj.'),
        'P4_pnbr': fields.selection(_P1_P4_selection(), 'P4', help='4. polje poziva na broj.'),
        
        # G - gotovina, K - kartice, C - cek,  T - transakcijski racun, O – ostal
        'nacin_placanja': fields.selection( [('G'  ,'Gotovina'), 
                                             ('K'  ,'Kartice'),
                                             ('C'  ,'Cek'),
                                             ('T'  ,'Transakcijski racun'),
                                             ('O'  ,'Ostalo'),
                                            ], "Nacin placanja", 
                                             help="G - gotovina, K - kartice, C - cek,  T - transakcijski racun, O – ostalo"
                                                  "U slucaju vise nacina placanja po jednom racunu, isto je potrebno prijaviti pod O - ostalo."
                                                  "Za sve nacine placanja koji nisu propisani koristiti ce se oznaka O – ostalo.",
                                            )
        }

    _defaults = {
                  'model_pnbr':'01',
                  'P1_pnbr':'partner_id',
                  'P2_pnbr':'invoice_no',
                  'P3_pnbr':'delivery_ym',
                  'P4_pnbr':False,
                 }

    def create_sequence(self, cr, uid, vals, context=None):
        """
        Create new entry sequence for every new Joural
        @param cr: cursor to database
        @param user: id of current user
        @param ids: list of record ids to be process
        @param context: context arguments, like lang, time zone
        @return: return a result
        """
        seq_pool = self.pool.get('ir.sequence')
        seq_typ_pool = self.pool.get('ir.sequence.type')

        name = vals['name']
        code = vals['code'].lower()

        types = {
            'name': name,
            'code': code
        }
        seq_typ_pool.create(cr, uid, types)

        seq = {
            'name': name,
            'code': code,
            'active': True,
            'prefix': "%(y)s-",
            'padding': 4,
            'number_increment': 1
        }
        return seq_pool.create(cr, uid, seq)

account_journal()

