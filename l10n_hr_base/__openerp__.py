# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Module: l10n_hr_base
#    Author: Goran Kliska
#    mail:   goran.kliska(AT)slobodni-programi.hr
#    Copyright: Slobodni programi d.o.o., Zagreb
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
    "name" :"Croatian localization - base module",
    "description": """
Croatian localisation.
======================

Author: Goran Kliska @ Slobodni programi d.o.o.
        www.slobodni-programi.hr

Contributions:
    Infokom d.o.o.

Description:

Podaci o organizaciji u raznim tijelima drzavne uprave:
  Porezna uprava
  Porezna ispostava
  Br. obveze mirovinsko
  Br. obveze zdravstveno
  Maticni broj
  Nacionalna klasifikacija djelatnosti

Banke:
 VBB - Vodeći broj banke
 Popis banaka


""",
    "version": "1.61",
    "author": "Slobodni programi d.o.o.",
    "category": "Localisation/Croatia",
    "website": "http://www.slobodni-programi.hr",

    'depends': [
               'base_vat',
                ],
    'init_xml': [],
    'update_xml': [
                   'security/ir.model.access.csv',
                   'data/res.bank.csv',
                   'data/l10n_hr_base.nkd.csv',
                   'company_view.xml',
                   'l10n_hr_base_view.xml',
                   ],
    "demo_xml" : [],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
