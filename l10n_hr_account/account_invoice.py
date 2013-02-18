# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2012 Slobodni programi d.o.o. (<http://www.slobodni-programi.com>).
#    $Id$
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from osv import fields, osv
from tools.translate import _

import poziv_na_broj as pnbr

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def _get_reference_type(self, cursor, user, context=None):
        """Function used by the function field reference_type in order to initalise available Reference Types"""
        res = super(account_invoice, self)._get_reference_type(cursor, user, context=context)
        res.append(('pnbr', 'Poziv na br.'))
        return res

    def _get_default_reference_type(self, cr, uid, context=None):
        if context is None:
            context = {}
        type_inv = context.get('type', 'out_invoice')
        user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
        if user.company_id.country_id and user.company_id.country_id.code in('HR'):
            if type_inv in ('out_invoice'):
                return 'pnbr' 
        return 'none'


    def _convert_ref(self, cr, uid, ref):
        ref = super(account_invoice, self)._convert_ref(cr, uid, ref)
        res=''
        for ch in ref:
            res = res + (ch.isdigit() and ch or '') 
        return res

    _columns = {
                'reference_type': fields.selection(_get_reference_type, 'Reference Type',
                                  required=True, readonly=True, states={'draft':[('readonly',False)]}),
                'date_delivery': fields.date('Delivery Date', readonly=True,
                                 states={'draft':[('readonly',False)]}, select=True, help="Keep empty to use the current date"),
               }

    _defaults = {
                 'reference_type': _get_default_reference_type,
                 }

    def copy(self, cr, uid, id, default=None, context=None):
        default = default or {}
        if 'date_delivery' not in default:
            default.update({
                'date_delivery':False
            })
        return super(account_invoice, self).copy(cr, uid, id, default, context)

    def pnbr_get(self, cr, uid, inv_id, context=None):
        invoice = self.browse(cr, uid, inv_id, context=context)
        res = invoice.reference or ''
        def getP1_P4data(what):
            res =""
            if what == 'partner_code': 
                res = invoice.partner_id.code or invoice.partner_id.id
            if what == 'partner_id': 
                res = str(invoice.partner_id.id)
            if what == 'invoice_no': 
                res = invoice.number
            if what == 'invoice_ym': 
                res = invoice.date_invoice[2:4] + invoice.date_invoice[5:7]
            if what == 'delivery_ym': 
                res = invoice.date_delivery[2:4] + invoice.date_delivery[5:7]
            return self._convert_ref(cr, uid, res)

        if invoice.journal_id.model_pnbr and invoice.journal_id.model_pnbr > '0':
            model = invoice.journal_id.model_pnbr
            P1 = getP1_P4data(invoice.journal_id.P1_pnbr or '')
            P2 = getP1_P4data(invoice.journal_id.P2_pnbr or '')
            P3 = getP1_P4data(invoice.journal_id.P3_pnbr or '')
            P4 = getP1_P4data(invoice.journal_id.P4_pnbr or '')
            res = pnbr.reference_number_get( model, P1, P2, P3, P4)
        return model+' '+res

    #KGB Copy
    def action_number(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        #TODO: not correct fix but required a frech values before reading it.
        self.write(cr, uid, ids, {})

        for obj_inv in self.browse(cr, uid, ids, context=context):
            id = obj_inv.id
            invtype = obj_inv.type
            number = obj_inv.number
            move_id = obj_inv.move_id and obj_inv.move_id.id or False
            reference = obj_inv.reference or ''

            self.write(cr, uid, id, {'internal_number':number}) #kgb ids?

            if invtype in ('in_invoice', 'in_refund'):
                if not reference:
                    ref = self._convert_ref(cr, uid, number)
                else:
                    ref = self._convert_ref(cr, uid, number)
                    #ref = reference
            else:
                ref = self._convert_ref(cr, uid, number)
                #KGB - start
                if not obj_inv.date_invoice:
                    self.write(cr, uid, [id], {'date_invoice':time.strftime('%Y-%m-%d')}, context=context)
                    #TODO: need to? self.action_date_assign( cr, uid, [id])
                if not obj_inv.date_delivery: #mandatory in Croatia
                    self.write(cr, uid, [id], {'date_delivery':obj_inv.date_invoice}, context=context)
                ref = self.pnbr_get(cr, uid, id, context)
                self.write(cr, uid, id, {'reference':ref})
                #KGB - end

            cr.execute('UPDATE account_move SET ref=%s ' \
                    'WHERE id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_move_line SET ref=%s ' \
                    'WHERE move_id=%s AND (ref is null OR ref = \'\')',
                    (ref, move_id))
            cr.execute('UPDATE account_analytic_line SET ref=%s ' \
                    'FROM account_move_line ' \
                    'WHERE account_move_line.move_id = %s ' \
                        'AND account_analytic_line.move_id = account_move_line.id',
                        (ref, move_id))

            for inv_id, name in self.name_get(cr, uid, [id]):
                ctx = context.copy()
                if obj_inv.type in ('out_invoice', 'out_refund'):
                    ctx = self.get_log_context(cr, uid, context=ctx)
                message = _("Invoice  '%s' is validated.") % name
                self.log(cr, uid, inv_id, message, context=ctx)
        return True

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        types = {
                'out_invoice': 'IR: ', #KGB CI
                'in_invoice': 'UR: ',  #KGB SI
                'out_refund': 'IO: ',  #KGB OR
                'in_refund': 'UO: ',   #KGB SR 
                }
        return [(r['id'], (r['number']) or types[r['type']] + (r['name'] or '')) for r in self.read(cr, uid, ids, ['type', 'number', 'name'], context, load='_classic_write')]
    
    
    def button_change_fiscal_position(self, cr, uid, ids, context=None):
        if context is None:
            context = {}

        fpos_obj = self.pool.get('account.fiscal.position')
        inv_line_obj = self.pool.get('account.invoice.line')
        
        for inv in self.browse(cr,uid,ids):
            for line in inv.invoice_line:
                new_taxes = fpos_obj.map_tax(cr, uid, inv.fiscal_position, line.product_id.taxes_id)
                inv_line_obj.write(cr, uid, [line.id], {'invoice_line_tax_id': [(6,0,new_taxes)]})
        return True


account_invoice()