from fiskal import *

a = Fiskalizacija()

a.t = time.localtime()
tmptime  = '%d.%02d.%02d %02d:%02d:%02d' % (a.t.tm_mday, a.t.tm_mon, a.t.tm_year, a.t.tm_hour, a.t.tm_min, a.t.tm_sec)
a.zaglavlje.DatumVrijeme = '%d.%02d.%02dT%02d:%02d:%02d' % (a.t.tm_mday, a.t.tm_mon, a.t.tm_year, a.t.tm_hour, a.t.tm_min, a.t.tm_sec)

a.zaglavlje.IdPoruke = str(uuid.uuid4())
  
a.racun.Oib = "57699704120"
a.racun.USustPdv = 'true'
a.racun.DatVrijeme = a.zaglavlje.DatumVrijeme 
a.racun.OznSlijed = 'P'
a.racun.BrRac.BrOznRac = '1'
a.racun.BrRac.OznPosPr = 'TESTIRAMO'
a.racun.BrRac.OznNapUr = '12'

a.porez = a.client2.factory.create('tns:Porez')
a.porez.Stopa = "25.00"
a.porez.Osnovica = "100.00"
a.porez.Iznos = "25.00"

a.racun.Pdv.Porez.append(a.porez)

a.racun.IznosUkupno = "125.00" # Ukupni iznos
a.racun.NacinPlac = "G" # Nacin placanja
a.racun.OibOper = "57699704120"
a.racun.NakDost = "false"

a.izracunaj_zastitni_kod(tmptime)
odgovor_string = a.posalji()
odgovor_array = odgovor_string[1]

# ... sad tu ima odgovor.Jir
jir = odgovor_array.Jir
