# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: account_storno
#    Author: Goran Kliska
#    mail:   gkliskaATgmail.com
#    Copyright (C) 2011- Slobodni programi d.o.o., Zagreb
#                  http://www.slobodni-programi.hr
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
    "name" : "Account storno",
    "description" : """

Author: Goran Kliska @ Slobodni programi d.o.o.
        http://www.slobodni-programi.hr
Contributions: 
  Tomislav Bošnjaković @ Storm Computers d.o.o.: Bugs report  

Description:
 Enables storno accounting.
 Adds new field "Posting policy" with values Storno/Contra on the Journal. 
 For Storno journals refund invoices are done in the same journal with negative *(-1) quantities.
 Negative amounts are posted on the same side (debit or credit) as positive.
 Countries where Storno accounting is mandatory or considered as best practice:
     Czech Republic, Poland, Romania, Russia, Slovakia, Ukraine, Croatia, Bosnia and Herzegovina, Serbia, Romania, ...
 

WARNING:
 This module is managing only invoices. 
 Other modules are required for stock, vaucher, etc. storno posting.

""",
    "version" : "11.1",
    "author" : "Slobodni programi d.o.o.",
    "category" : "Localisation/Croatia",
    "website": "http://www.slobodni-programi.hr",

    'depends': [
                'account',
                ],
    'init_xml': [],
    'update_xml': [ 'account_view.xml',
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
