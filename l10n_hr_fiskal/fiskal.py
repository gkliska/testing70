#!/usr/bin/python
#coding:utf-8

import sys, time, libxml2, xmlsec, os, StringIO, uuid, base64, hashlib, suds, datetime
from suds.client import Client
from suds.plugin import MessagePlugin, PluginContainer
from M2Crypto import RSA

######################
## potrebno iz fina certa izvaditi kljuceve i upakirati ih u folder...
keyFile = 'openerp/addons/l10n_hr_fiskal/kljuc.pem'
certFile = 'openerp/addons/l10n_hr_fiskal/cert.pem'
# ovo bi isto učitao iz baze, polja su spremna samo trebam izvadit van..  zasada ovako---

    # 
class FiskalBase():
    #Formatiram si datum po potrebi
    def CurrDateTime(self): 
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
    
    

import logging
logging.basicConfig(level=logging.INFO, filename='/var/log/fisk/fiskalizacija.log')
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport').setLevel(logging.DEBUG)
#--> Loging isključio.. mozda ostaviti kasnije... ali sad trenutno netrebao.. 


###################### Override failed metode zbog XML cvora koji fali u odgovoru porezne ################

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
class PrijavaProstora():
    
    path=os.getcwd()
    wsdl='file://' + path + '/openerp/addons/l10n_hr_fiskal/wsdl/FiskalizacijaService.wsdl'
    client2 = Client(wsdl, cache=None, prettyxml=True, timeout=15, faults=False, plugins=[DodajPotpis()]) 
    client2.add_prefix('tns', 'http://www.apis-it.hr/fin/2012/types/f73')
    
    zaglavlje = client2.factory.create('tns:Zaglavlje')
    pp = client2.factory.create('tns:PoslovniProstor')
    #adresni_podatak = client2.factory.create('tns:AdresniPodatak')
    def posalji(self):
        odgovor=self.client2.service.poslovniProstor(self.zaglavlje, self.pp)
        poruka_zahtjev =  self.client2.last_sent().str()
        poruka_odgovor = str(odgovor)
        pass #TODO upakirati zahjtev i odgovor pa posle raskopati i spremiti u bazu!
        return poruka_odgovor
        #http_status = odgovor[0]
        #return http_status
        
        



class Fiskalizacija():
    
    path=os.getcwd()
    wsdl='file://' + path + '/openerp/addons/l10n_hr_fiskal/wsdl/FiskalizacijaService.wsdl'
    
    client2 = Client(wsdl, cache=None, prettyxml=True, timeout=15, faults=False, plugins=[DodajPotpis()]) 
    #client2 = Client(wsdl, prettyxml=True, timeout=3, plugins=[DodajPotpis()]) 
    client2.add_prefix('tns', 'http://www.apis-it.hr/fin/2012/types/f73')
    zaglavlje = client2.factory.create('tns:Zaglavlje')
    
    
    
    racun = client2.factory.create('tns:Racun')
    
    
    
    def izracunaj_zastitni_kod(self, datumvrijeme):    
        medjurezultat = self.racun.Oib + str(datumvrijeme) + str(self.racun.BrRac.BrOznRac) + self.racun.BrRac.OznPosPr + self.racun.BrRac.OznNapUr + str(self.racun.IznosUkupno)
        pkey = RSA.load_key(keyFile)
        signature = pkey.sign(hashlib.sha1(medjurezultat).digest())
        self.racun.ZastKod = hashlib.md5(signature).hexdigest()

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
  
    def echo(self):
        #self.echo = self.client2.service.echo('Ovo moze biti bolikoji teskt za test poruku')
        try:
            pingtest=self.client2.service.echo('TEST PORUKICA')
            return pingtest
        except:
            return 'ERROR SEND ECHO'
        #if(self.client2.service.echo('OK') == 'OK'): return True
    
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