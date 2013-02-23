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
import string
import datetime
import re
from openerp.osv import fields, osv, orm



class res_certificate(osv.Model):
    _name='res.certificate'
    _description='Stored Certificates'
    _order='name'
    
    def _get_cert_selection(self,cursor,user_id, context=None):
        return (('fina_demo','Fina Demo Certifiacte'),
                ('fina_prod','Fina Production Certificate'),
                ('personal','Personal Certificate'),
                ('other','Other types ->TODO')
               )
        
    _columns = {
        'name': fields.char('Name', size=128, help="Internal name for certificate", reguired=True, select=True),
        'res_partner_id':fields.many2one('res.partner','partner_id','Korisnik',help='Authorized user for this certificate'),
        'cert_type':fields.selection(_get_cert_selection,'Certificate Type'),
        'cert': fields.text('Certificate', help='Certifikat (text)') ,
        'cert_password': fields.char('Certificate Password', size=64),
        'cert_key': fields.text('Private Key', help="Private key for user"),
        'key_password':fields.char('Private Key Password', size=64),
        'certificate':fields.binary('Certificate')
        ## TODO : binary fields for storing raw certificate 
        ##        how to upload certificate file (base64 encoded)?
        }
    
res_certificate()


## this is for other SOAP destination servers that may be used
## za hr bi bilo dovoljno i selection polje
class res_certificate_server(osv.Model):
    _name="res.certificate.server"
    _description="Servers for SOAP communication"
    _columns = {
        'name':fields.char('Name',size=128, help='Internal name', required=True),
        'link':fields.char('Link',size=256,required=True)        
        }