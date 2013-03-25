#!/usr/bin/python
#coding:utf-8

import sys, time, libxml2, xmlsec, os, StringIO, uuid, base64, hashlib, suds, datetime
from suds.client import Client
from suds.plugin import MessagePlugin, PluginContainer
from M2Crypto import RSA

import logging

#Globals
keyFile = certFile = "" 


#logging.basicConfig(level=logging.INFO, filename='/var/log/fisk/fiskalizacija.log')
#logging.getLogger('suds.client').setLevel(logging.DEBUG)
#logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#--> Loging isključio.. mozda ostaviti kasnije... ali sad trenutno netrebao.. 

def received(self, context):
    self.poruka_odgovor = context.reply
 
    libxml2.initParser()
    libxml2.substituteEntitiesDefault(1)
 
    xmlsec.init()
    xmlsec.cryptoAppInit(None)
    xmlsec.cryptoInit()
 
    mngr = xmlsec.KeysMngr()
    xmlsec.cryptoAppDefaultKeysMngrInit(mngr)
    #mngr.certLoad(verifyCertFile, xmlsec.KeyDataFormatPem, xmlsec.KeyDataTypeTrusted)
    mngr.certLoad(certFile, xmlsec.KeyDataFormatPem, xmlsec.KeyDataTypeTrusted)
  
    doc = libxml2.parseDoc(context.reply)
    xmlsec.addIDs(doc, doc.getRootElement(), ['Id'])
    node = xmlsec.findNode(doc.getRootElement(), xmlsec.NodeSignature, xmlsec.DSigNs)
    dsig_ctx = xmlsec.DSigCtx(mngr)
    dsig_ctx.verify(node)
    if(dsig_ctx.status == xmlsec.DSigStatusSucceeded): self.valid_signature = 1
 
    xmlsec.cryptoShutdown()
    xmlsec.cryptoAppShutdown()
    xmlsec.shutdown()
    libxml2.cleanupParser()
    return context

###################### Override failed metode zbog XML cvora koji fali u odgovoru porezne ################
def failed(self, binding, error):
    return _failed(self, binding, error)


def _failed(self, binding, error):
    status, reason = (error.httpcode, str(error))
    reply = error.fp.read()
    if status == 500:
        if len(reply) > 0:
            reply, result = binding.get_reply(self.method, reply)
            self.last_received(reply)
            plugins = PluginContainer(self.options.plugins)
            ctx = plugins.message.unmarshalled(reply=result)
            result = ctx.reply
            return (status, result)
        else:
            return (status, None)
    if self.options.faults:
        raise Exception((status, reason))
    else:
        return (status, None)

suds.client.SoapClient.failed = _failed

from datetime import datetime
from pytz import timezone

def zagreb_now():
    return datetime.now(timezone('Europe/Zagreb'))
    #now_utc = datetime.now(timezone('UTC'))
    #now_utc.astimezone(timezone('Europe/Zagreb'))
    #now_zagreb= datetime.now(timezone('Europe/Zagreb'))

def fiskal_num2str(num):
    return "{:-.2f}".format(num)

class DodajPotpis(MessagePlugin):
    
    def sending(self, context):
        msgtype = "RacunZahtjev"
        if "PoslovniProstorZahtjev" in context.envelope: msgtype = "PoslovniProstorZahtjev"
    
        doc2 = libxml2.parseDoc(context.envelope)

        zahtjev = doc2.xpathEval('//*[local-name()="%s"]' % msgtype)[0]
        doc2.setRootElement(zahtjev)

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

from tools import config

def SetFiskalFilePaths(key, cert):
    global keyFile, certFile
    keyFile, certFile = key, cert

class Fiskalizacija():
    
    def init(self, msgtype, wsdl, key, cert):
        #file paths for wsdl, key, cert
        self.wsdl = wsdl  
        self.key = key 
        self.cert = cert
        SetFiskalFilePaths(key, cert)

        self.client2 = Client(wsdl, cache=None, prettyxml=True, timeout=15, faults=False, plugins=[DodajPotpis()] ) 
        self.client2.add_prefix('tns', 'http://www.apis-it.hr/fin/2012/types/f73')
        self.zaglavlje = self.client2.factory.create('tns:Zaglavlje')

        #Not needed
        if msgtype in ('echo'):
            pass
        elif msgtype in ('PoslovniProstor'):
            self.prostor = self.client2.factory.create('tns:PoslovniProstor')
        elif msgtype in ('Racun'):
            self.racun = self.client2.factory.create('tns:Racun') 



    def time_formated(self): 
        tstamp = zagreb_now() #datetime.datetime.now() this was server def. tz time
        ##PAZI TIME OFFSET!!! uzmi timestamp , al vrijeme ima offset!!
        
        #tstamp=datetime.now(timezone('Europe/Zagreb')) #BOLE 
        v_date='%02d.%02d.%02d' % (tstamp.day, tstamp.month, tstamp.year)
        v_datum_vrijeme='%02d.%02d.%02dT%02d:%02d:%02d' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        v_datum_racun='%02d.%02d.%02d %02d:%02d:%02d' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        #tstamp=datetime.now(timezone('UTC'))
        vrijeme={'datum':v_date,                    #vrijeme SAD
                 'datum_vrijeme':v_datum_vrijeme,   # format za zaglavlje XML poruke
                 'datum_racun':v_datum_racun,       # format za ispis na računu
                 'time_stamp':tstamp}               # timestamp, za zapis i izračun vremena obrade
        return vrijeme

    def set_start_time(self):
        self.start_time = self.time_formated()

    def set_stop_time(self):
        self.stop_time = self.time_formated()
        

    def echo(self):
        #self.echo = self.client2.service.echo('Ovo moze biti bolikoji teskt za test poruku')
        try:
            pingtest=self.client2.service.echo('TEST PORUKICA')
            return pingtest
        except:
            return 'ERROR SEND ECHO'
        #if(self.client2.service.echo('OK') == 'OK'): return True


    def posalji_prostor(self):
        odgovor=self.client2.service.poslovniProstor(self.zaglavlje, self.pp)
        poruka_zahtjev =  self.client2.last_sent().str()
        poruka_odgovor = str(odgovor)
        return poruka_odgovor, poruka_zahtjev
        
    
    def izracunaj_zastitni_kod(self):    
        self.racun.ZastKod = self.get_zastitni_kod(self.racun.Oib,
                                                  self.racun.DatVrijeme,
                                                  str(self.racun.BrRac.BrOznRac),
                                                  self.racun.BrRac.OznPosPr,
                                                  self.racun.BrRac.OznNapUr,
                                                  str(self.racun.IznosUkupno)
                                                  )

    def get_zastitni_kod(self, Oib, DatVrijeme, BrOznRac, OznPosPr, OznNapUr, IznosUkupno):    
        medjurezultat = ''.join((Oib, DatVrijeme, BrOznRac, OznPosPr, OznNapUr, IznosUkupno)) 
        pkey = RSA.load_key(keyFile)
        signature = pkey.sign(hashlib.sha1(medjurezultat).digest())
        return hashlib.md5(signature).hexdigest()


    def posalji_racun(self):
        
        try:
            return self.client2.service.racuni(self.zaglavlje, self.racun)
        except:
            pass#a=self.client2.service.racuni(self.zaglavlje, self.racun)
            return 'greška u slanju podataka' 

    def generiraj_poruku(self):
        self.client2.options.nosend = True
        poruka = str(self.client2.service.racuni(self.zaglavlje, self.racun).envelope)
        self.client2.options.nosend = False
        return poruka
        
    
    def time_formated(self): 
        tstamp=datetime.datetime.now()
        ##PAZI TIME OFFSET!!! uzmi timestamp , al vrijeme ima offset!!
        v_date='%02d.%02d.%02d' % (tstamp.day, tstamp.month, tstamp.year)
        v_datum_vrijeme='%02d.%02d.%02dT%02d:%02d:%02d' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        v_datum_racun='%02d.%02d.%02d %02d:%02d:%02d' % (tstamp.day, tstamp.month, tstamp.year, tstamp.hour, tstamp.minute, tstamp.second)
        vrijeme={'datum':v_date,                    #vrijeme SAD
                 'datum_vrijeme':v_datum_vrijeme,   # format za zaglavlje XML poruke
                 'datum_racun':v_datum_racun,       # format za ispis na računu
                 'time_stamp':tstamp}               # timestamp, za zapis i izračun vremena obrade
        return vrijeme