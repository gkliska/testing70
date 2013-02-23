#!/usr/bin/python
#coding:utf-8

import sys, time, libxml2, xmlsec, os, StringIO, uuid, base64, hashlib, suds
from suds.client import Client
from suds.plugin import MessagePlugin
from M2Crypto import RSA

######################
## potrebno iz fina certa izvaditi kljuceve 

keyFile = 'openerp/addons/l10n_hr_fiskal/kljuc.pem'
certFile = 'openerp/addons/l10n_hr_fiskal/cert.pem'

import logging

logging.basicConfig(level=logging.INFO, filename='/var/log/fisk/fiskalizacija.log')
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)

class DodajPotpis(MessagePlugin):
  def sending(self, context):

    msgtype = "RacunZahtjev"
    if "PoslovniProstorZahtjev" in context.envelope: msgtype = "PoslovniProstorZahtjev"
    
    doc2 = libxml2.parseDoc(context.envelope)

    racunzahtjev = doc2.xpathEval('//*[local-name()="%s"]' % msgtype)[0]
    doc2.setRootElement(racunzahtjev)

    x = doc2.getRootElement().newNs('http://www.apis-it.hr/fin/2012/types/f73', 'tns')
 
    for i in doc2.xpathEval('//*'):
        i.setNs(x)

    libxml2.initParser()
    libxml2.substituteEntitiesDefault(1)

    xmlsec.init()
    xmlsec.cryptoAppInit(None)
    xmlsec.cryptoInit()

    doc2.getRootElement().setProp('Id', msgtype)
    xmlsec.addIDs(doc2, doc2.getRootElement(), ['Id'])    

    signNode = xmlsec.TmplSignature(doc2, xmlsec.transformExclC14NId(), xmlsec.transformRsaSha1Id(), None)

    doc2.getRootElement().addChild(signNode)
    
    refNode = signNode.addReference(xmlsec.transformSha1Id(), None, None, None)
    refNode.setProp('URI', '#%s' % msgtype)
    refNode.addTransform(xmlsec.transformEnvelopedId())
    refNode.addTransform(xmlsec.transformExclC14NId())
 
    dsig_ctx = xmlsec.DSigCtx()
    key = xmlsec.cryptoAppKeyLoad(keyFile, xmlsec.KeyDataFormatPem, None, None, None)
    dsig_ctx.signKey = key
    xmlsec.cryptoAppKeyCertLoad(key, certFile, xmlsec.KeyDataFormatPem)
    key.setName(keyFile)

    keyInfoNode = signNode.ensureKeyInfo(None)
    x509DataNode = keyInfoNode.addX509Data()
    xmlsec.addChild(x509DataNode, "X509IssuerSerial")
    xmlsec.addChild(x509DataNode, "X509Certificate")

    dsig_ctx.sign(signNode)
    
    if dsig_ctx is not None: dsig_ctx.destroy()
    context.envelope = """<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
  <soapenv:Body>""" + doc2.serialize().replace('<?xml version="1.0" encoding="UTF-8"?>','') + """</soapenv:Body></soapenv:Envelope>""" # Ugly hack
    
    # Shutdown xmlsec-crypto library, ako ne radi HTTPS onda ovo treba zakomentirati da ga ne ugasi prije reda
    xmlsec.cryptoShutdown()
    xmlsec.shutdown()
    libxml2.cleanupParser()

    return context

############################################################################################################################################

class Fiskalizacija():
    #wsdl = 'file:///home/bole/openerp/git/fiskalizacija/wsdl/FiskalizacijaService.wsdl' # Za test
    wsdl = 'openerp/addons/l10n_hr_fiskal/wsdl/FiskalizacijaService.wsdl' # Za test
    wsdl = 'file:///media/documents/openerp/openerp-7.0-20130212-002145/openerp/addons/l10n_hr_fiskal/wsdl/FiskalizacijaService.wsdl' # RADI !!!
    ## TODO : read path, i zaljepi local path do fajla! ovak nema smisla
    
    client2 = Client(wsdl, cache=None, prettyxml=True, timeout=15, faults=False, plugins=[DodajPotpis()]) 
    #client2 = Client(wsdl, prettyxml=True, timeout=3, plugins=[DodajPotpis()]) 
    client2.add_prefix('tns', 'http://www.apis-it.hr/fin/2012/types/f73')

    racun = client2.factory.create('tns:Racun')
    zaglavlje = client2.factory.create('tns:Zaglavlje')

    def izracunaj_zastitni_kod(self, datumvrijeme):    
        medjurezultat = self.racun.Oib + str(datumvrijeme) + str(self.racun.BrRac.BrOznRac) + self.racun.BrRac.OznPosPr + self.racun.BrRac.OznNapUr + str(self.racun.IznosUkupno)
        pkey = RSA.load_key(keyFile)
        signature = pkey.sign(hashlib.sha1(medjurezultat).digest())
        self.racun.ZastKod = hashlib.md5(signature).hexdigest()

    def posalji(self):
        return self.client2.service.racuni(self.zaglavlje, self.racun)

    def generiraj_poruku(self):
        self.client2.options.nosend = True
        poruka = str(self.client2.service.racuni(self.zaglavlje, self.racun).envelope)
        self.client2.options.nosend = False
        return poruka
  
    def echo(self):
        self.echo = self.client2.service.echo('testtttt')
