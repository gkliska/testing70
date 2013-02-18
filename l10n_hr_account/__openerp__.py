# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_account
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


{
    "name" : "Croatian localization - taxes",
    "description" : """
Croatian localisation.
======================

Author: Goran Kliska @ Slobodni programi d.o.o.
     Change fiscal position is borrowed from module account_invoice_change_fiscal_position
     Thanks to Leonardo Pistone <leonardo.pistone@domsense.com>

Contributions: 
     .
Description:

  Model i Poziv na broj na izlaznim računima, 
  Datum isporuke na izlaznim računima,
  Promjena fiskalne pozicije na stavkama računa
  
   
TODO Ispis ovih podataka na racunu, mozda u posebnom modulu.

""",
    "version" : "0.3",
    "author" : "Slobodni programi d.o.o.",
    "category" : "Localisation/Croatia",
    "website": "http://www.slobodni-programi.hr",

    'depends': [
               'account',
                ],
    'init_xml': [],
    'update_xml': [
                   'account_view.xml',
                   'account_invoice_view.xml',
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
