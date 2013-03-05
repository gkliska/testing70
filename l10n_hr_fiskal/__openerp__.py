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

{
    "name" : "Croatian localization - Fiscalization module",
    "description" : """
OpenERP Fiskalizacija izdanih računa
====================================

Author: Davor Bojkić - Bole @ DAJ MI 5
        www.dajmi5.com

Contributions: Hrvoje ThePython - Free Code!
               Goran Kliska @ Slobodni Programi

Description:
TODO:
STAGE2 : napomene
    Propisati će se izgled broja računa kako se DA 
    treba ispisivati na fizičkom računu u 
    sljedećem obliku: 
    Račun
    brojčana oznaka računa/oznaka poslovnog prostora/oznaka naplatnog uređaja
    Primjer: 1234567890/POSL1/12
    
    PREGLEDATI BROJEVNI KRUG ZA IRA!


STAGE 1 DONE!
v1.01    Gumb TEST šalje i dobiva jir
            ako zeza!
            potrebno popraviti path za wsdl u fiskal.py i učitati vrijednosti sa drugih polja.. 
        
        a lot of stuff...  send echo and recive/log reply will be considered succes for stage 1.
v1.00    Dodane tablice pripadni views, 
         zasada dodijeljeni izbornici Postavke/Fiskalizacija:
            - l10n_hr_pprostor - podaci o poslovnim prostorima
            - l10n_hr_log    - log komunikacije sa serverima 
            - res_certificates - pohranjeni certifikati i ključevi
            - res_certificates_servers - serveri naziv/link
                - Podaci : Testni i Produkcijski server Porezne Uprave
            - Ostali bitni a promjenjivi podaci preuzeti sa stranica porezne:
                 wsdl/FiskalizacijaService.wsdl
                 schema/FiskalizacijaSchema
                 schema/xmldsig-core-schema.xsd

Preduvjeti: 
    na serveru instalirati:
        python-dev ,
        python-ms2crypto , 
        libxmlsec1-dev
    i onda build/install pyxmlsec-0.3.2 ili pronaći neki prikladniji! 
""",
    "version" : "1.02",
    "author" : "DAJ MI 5",
    "category" : "Localisation/Croatia",
    "website": "http://www.dajmi5.com",

    'depends': [
                'base',
                'base_vat',
                'l10n_hr',
                'l10n_hr_account'
                ],
    #'external_dependencies':{'python':['m2crypto','pyxmlsec'],
    #                         'bin':'libxmlsec-dev'},
    'init_xml': [],
    'data': [
                   'view/l10n_hr_fiskal_view.xml',
                   'view/res_certificate_view.xml',
                   'view/l10n_hr_log_view.xml',
                   'data/res.certificate.server.csv',
                   ## DEMO DATA - dodao nekoliko partnera za test
                   'demo/res.partner.csv',          #dodajem partnere
                   'demo/demo_certifikat_Z3.xml',    # dodajem Z3 Demo cert
                   'demo/res_company.xml', #za praznu bazu upiše naziv i oib.. 
                   'view/account_invoice_view.xml',
                   'view/zki_check.xml'
                   ##testing only
                   #'test.xml'
                   ],
    "demo" : [
              
              ],
    'test' : [],
    "active": False,
    "installable": True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
