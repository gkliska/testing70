# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: account_storno
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2013- Slobodni programi d.o.o., Zagreb
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
import time
from tools.translate import _ 

class account_invoice(osv.osv):
    _inherit = "account.invoice"

    def action_move_create(self, cr, uid, ids, context=None):
        """Creates invoice related analytics and financial move lines
           We have to go one by one to inject invoice to line_get_convert
        """
        if context is None:
            context = {}
        for inv in self.browse(cr, uid, ids, context=context):
            context.update({'brw_invoice': inv})
            super(account_invoice,self).action_move_create(cr, uid, [inv.id], context=context)
        return True
    

    def line_get_convert(self, cr, uid, x, part, date, context=None):
        res =super(account_invoice,self).line_get_convert(cr, uid, x, part, date, context=context)
        if context is None:
            context = {}
        invoice = context.get('brw_invoice',False)
        if invoice and invoice.journal_id.posting_policy=='storno':
            credit = debit = 0.0
            if invoice.type in ('out_invoice', 'out_refund'):
                if x.get('type','src') in ('dest'):
                    debit  = x['price']   # for OUT_invoice dest (tot. amount goes to debit)
                else: # in('src','tax')    
                    credit  = x['price'] * (-1)
            else: #in ('in_invoice', 'in_refund')
                if x.get('type','src') in ('dest'):
                    credit  = x['price']  * (-1) 
                else:    
                    debit  = x['price']
    
            res['debit']  = debit
            res['credit'] = credit
        return res

    def inv_line_characteristic_hashcode(self, invoice, invoice_line):
        """Overridable hashcode generation for invoice lines. Lines having the same hashcode
        will be grouped together if the journal has the 'group line' option. Of course a module
        can add fields to invoice lines that would need to be tested too before merging lines
        or not."""
        #return "%s-%s-%s-%s-%s"%(
        #   invoice_line['account_id'],
        #   invoice_line.get('tax_code_id',"False"),
        #   invoice_line.get('product_id',"False"),
        #   invoice_line.get('analytic_account_id',"False"),
        #   invoice_line.get('date_maturity',"False"))
        res = super(account_invoice,self).inv_line_characteristic_hashcode(invoice, invoice_line)
        

    def group_lines(self, cr, uid, iml, line, inv):
        """Merge account move lines (and hence analytic lines) if invoice line hashcodes are equals"""
        if inv.journal_id.group_invoice_lines:
            if inv.journal_id.posting_policy == 'contra':
                return super(account_invoice,self).group_lines(cr, uid, iml, line, inv)
            if inv.journal_id.posting_policy == 'storno':
                line2 = {}
                for x, y, l in line:
                    hash = self.inv_line_characteristic_hashcode(inv, l)
                    side = l['debit'] > 0 and 'debit' or 'credit'
                    tmp = '-'.join((hash,side))
                    if tmp in line2:
                        line2[tmp]['debit'] += l['debit'] or 0.0
                        line2[tmp]['credit'] += l['credit'] or 0.00
                        line2[tmp]['tax_amount'] += l['tax_amount']
                        line2[tmp]['analytic_lines'] += l['analytic_lines']
                        line2[tmp]['amount_currency'] += l['amount_currency']
                        line2[tmp]['quantity'] += l['quantity']
                    else:
                        line2[tmp] = l
                line = []
                for key, val in line2.items():
                    line.append((0,0,val))
        return line

    
"""
HISTORY
        #COPY of the original account.invoice.py
        #def action_move_create(self, cr, uid, ids, *args):
        ait_obj = self.pool.get('account.invoice.tax')
        cur_obj = self.pool.get('res.currency')
        period_obj = self.pool.get('account.period')
        context = {}
        for inv in self.browse(cr, uid, ids):
            if not inv.journal_id.sequence_id:
                raise osv.except_osv(_('Error !'), _('Please define sequence on invoice journal'))
            if not inv.invoice_line:
                raise osv.except_osv(_('No Invoice Lines !'), _('Please create some invoice lines.'))
            if inv.move_id:
                continue

            if not inv.date_invoice:
                self.write(cr, uid, [inv.id], {'date_invoice':time.strftime('%Y-%m-%d')})
            company_currency = inv.company_id.currency_id.id
            # create the analytical lines
            # one move line per invoice line
            iml = self._get_analytic_lines(cr, uid, inv.id)
            # check if taxes are all computed
            ctx = context.copy()
            ctx.update({'lang': inv.partner_id.lang})
            compute_taxes = ait_obj.compute(cr, uid, inv.id, context=ctx)
            self.check_tax_lines(cr, uid, inv, compute_taxes, ait_obj)

            if inv.type in ('in_invoice', 'in_refund') and abs(inv.check_total - inv.amount_total) >= (inv.currency_id.rounding/2.0):
                raise osv.except_osv(_('Bad total !'), _('Please verify the price of the invoice !\nThe real total does not match the computed total.'))

            if inv.payment_term:
                total_fixed = total_percent = 0
                for line in inv.payment_term.line_ids:
                    if line.value == 'fixed':
                        total_fixed += line.value_amount
                    if line.value == 'procent':
                        total_percent += line.value_amount
                total_fixed = (total_fixed * 100) / (inv.amount_total or 1.0)
                if (total_fixed + total_percent) > 100:
                    raise osv.except_osv(_('Error !'), _("Can not create the invoice !\nThe related payment term is probably misconfigured as it gives a computed amount greater than the total invoiced amount."))

            # one move line per tax line
            iml += ait_obj.move_line_get(cr, uid, inv.id)

            entry_type = ''
            if inv.type in ('in_invoice', 'in_refund'):
                ref = inv.reference
                entry_type = 'journal_pur_voucher'
                if inv.type == 'in_refund':
                    entry_type = 'cont_voucher'
            else:
                ref = self._convert_ref(cr, uid, inv.number)
                entry_type = 'journal_sale_vou'
                if inv.type == 'out_refund':
                    entry_type = 'cont_voucher'

            diff_currency_p = inv.currency_id.id <> company_currency
            # create one move line for the total and possibly adjust the other lines amount
            total = 0
            total_currency = 0
            total, total_currency, iml = self.compute_invoice_totals(cr, uid, inv, company_currency, ref, iml)
            acc_id = inv.account_id.id

            name = inv['name'] or '/'
            totlines = False
            if inv.payment_term:
                totlines = self.pool.get('account.payment.term').compute(cr,
                        uid, inv.payment_term.id, total, inv.date_invoice or False)
            if totlines:
                res_amount_currency = total_currency
                i = 0
                ctx.update({'date': inv.date_invoice})
                ctx.update({'force_currency_inv_rate': inv.ccurrency_rate})
                for t in totlines:
                    if inv.currency_id.id != company_currency:
                        amount_currency = cur_obj.compute(cr, uid, company_currency, inv.currency_id.id, t[1], context=ctx)
                    else:
                        amount_currency = False

                    # last line add the diff
                    res_amount_currency -= amount_currency or 0
                    i += 1
                    if i == len(totlines):
                        amount_currency += res_amount_currency

                    iml.append({
                        'type': 'dest',
                        'name': name,
                        'price': t[1],
                        'account_id': acc_id,
                        'date_maturity': t[0],
                        'amount_currency': diff_currency_p \
                                and amount_currency or False,
                        'currency_id': diff_currency_p \
                                and inv.currency_id.id or False,
                        'ref': ref,
                    })
            else:
                iml.append({
                    'type': 'dest',
                    'name': name,
                    'price': total,
                    'account_id': acc_id,
                    'date_maturity': inv.date_due or False,
                    'amount_currency': diff_currency_p \
                            and total_currency or False,
                    'currency_id': diff_currency_p \
                            and inv.currency_id.id or False,
                    'ref': ref
            })

            date = inv.date_invoice or time.strftime('%Y-%m-%d')
            part = inv.partner_id.id

            #KGB ORIGINAL
            #line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context={})),iml)
            #KGB CHANGE START because there is no invoice data/hook in line_get_convert.inv.type 
            # and inv.journal_id.posting_policy is needed
            ctx.update({'invoice': inv})
            line = map(lambda x:(0,0,self.line_get_convert(cr, uid, x, part, date, context=ctx)),iml)

            #KGB CHANGE END

            line = self.group_lines(cr, uid, iml, line, inv)

            journal_id = inv.journal_id.id
            journal = self.pool.get('account.journal').browse(cr, uid, journal_id)
            if journal.centralisation:
                raise osv.except_osv(_('UserError'),
                        _('You cannot create an invoice on a centralised journal. Uncheck the centralised counterpart box in the related journal from the configuration menu.'))

            line = self.finalize_invoice_move_lines(cr, uid, inv, line)

            move = {
                'ref': inv.reference and inv.reference or inv.name,
                'line_id': line,
                'journal_id': journal_id,
                'date': date,
                'narration':inv.comment
            }
            period_id = inv.period_id and inv.period_id.id or False
            ctx.update({'company_id': inv.company_id.id})
            if not period_id:
                period_ids = period_obj.find(cr, uid, inv.date_invoice, context=ctx)
                period_id = period_ids and period_ids[0] or False
            if period_id:
                move['period_id'] = period_id
                for i in line:
                    i[2]['period_id'] = period_id

            move_id = self.pool.get('account.move').create(cr, uid, move, context=context)
            new_move_name = self.pool.get('account.move').browse(cr, uid, move_id).name
            # make the invoice point to that move
            self.write(cr, uid, [inv.id], {'move_id': move_id,'period_id':period_id, 'move_name':new_move_name})
            # Pass invoice in context in method post: used if you want to get the same
            # account move reference when creating the same invoice after a cancelled one:
            self.pool.get('account.move').post(cr, uid, [move_id], context={'invoice':inv})
        self._log_event(cr, uid, ids)
        return True
"""
