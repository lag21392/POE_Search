from bs4 import BeautifulSoup
import requests
from constants import *
from email.parser import *
import json
import os
import winsound
import threading
import time
from datetime import datetime
from datetime import timedelta
import asyncio
import http3


puetoProxyS=[30000,30001,30002,30003]

async def preciosArticulo(tipoDeObjeto,nombreArticulo,level,quality,corrupted,links,levelRequired,proxi,tRequest):

        arch = open("requests.txt","r")
        post_url=arch.read()
        arch.close()

        if level == None:
            level=""
        if quality == None:
            quality=""


        if corrupted == None:
            corrupted=""
        elif corrupted :

            corrupted="1"

        elif not corrupted :

            corrupted="0"

        v = post_url.split("\n")


        if v[0].find("POST") != -1 and v[1].find("Host") != -1:
            url="https://" + v[1].split(" ")[1] + v[0].split(" ")[1] + "?" +v[-1].replace("name=" ,"name=" + nombreArticulo.replace(" ","+").replace("'","%27"))
            if tipoDeObjeto=="SkillGem":
                url = url.replace("level_min=", "level_min=" + str(level))
            url = url.replace("q_min=", "q_min=" + str(quality))
            url = url.replace("corrupted=", "corrupted=" + corrupted)

            url = url.replace("link_min=", "link_min=" + links)

            url = url.replace("sockets_min=", "sockets_min=" + links)
            url = url.replace("rlevel_min=", "rlevel_min=" + levelRequired)

            status="0"
            while int(status)!=int("200"):
                client = http3.AsyncClient()
                resp = await client.get(url)
                status=resp.status_code
                '''print("preciosArticulo")
                print(status)'''
                await asyncio.sleep(tRequest)



            '''resp=requests.get(url,timeout=20,proxies=proxi)'''

        '''print(str(resp) + " "+url)'''

        pagina=BeautifulSoup(resp.content,"html.parser")
        preciosArticulosExalted=pagina.find_all("span",attrs={'class':'has-tip currency currency-exalted'})

        preciosArticulosChaos=pagina.find_all("span",attrs={'class':'has-tip currency currency-chaos'})

        tiemposRAW=pagina.find_all("span",attrs={'class':'found-time-ago'})


        precios = []
        for a in preciosArticulosChaos[0:4]:
            if isinstance(float(str(a.text[0:-1])), float) or isinstance(float(str(a.text[0:-1])), int):
                precios.append(float(str(a.text[0:-1])))
        for a in preciosArticulosExalted[0:4]:
            if isinstance(float(str(a.text[0:-1])), float) or isinstance(float(str(a.text[0:-1])), int):
                precios.append(float(float(str(a.text[0:-1]))*precioExaltedXChaos))
        tiempos=[]
        for a in tiemposRAW[0:4]:
            tiempos.append(a.text)


        return precios,url,tiempos



async def buscarMejoresPreciso(urlAnt,tipoDeObjeto,porsentaje,mayorA,proxi,tRequest):
    '''print(tipoDeObjeto+"____________________________________________________________________________________________________________________")'''
    requestOK = True

    url=""
    requiereLink = False
    requierelevelRequired = False
    if tipoDeObjeto=="DivinationCard":
        url="https://poe.ninja/api/data/itemoverview?league=Delirium&type="+tipoDeObjeto+"&language=en"

    elif tipoDeObjeto=="SkillGem":
        url="https://poe.ninja/api/data/itemoverview?league=Delirium&type="+tipoDeObjeto+"&language=en"

    elif tipoDeObjeto == "UniqueMap":
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto == "UniqueJewel":
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto  == "UniqueFlask":
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto  == "UniqueWeapon":
        requiereLink=True
        requierelevelRequired=True
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto == "UniqueArmour":
        requiereLink = True
        requierelevelRequired = True
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto  == "UniqueAccessory":
        requiereLink=True
        requierelevelRequired=True
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"
    elif tipoDeObjeto == "Beast":
        requiereLink = True
        requierelevelRequired = True
        url = "https://poe.ninja/api/data/itemoverview?league=Delirium&type=" + tipoDeObjeto + "&language=en"

    '''print(url)'''

    '''print(url)
    time.sleep(10)'''
    articulos=[]
    if url != urlAnt or urlAnt == "":
        requestOk=False
        while not requestOk:
            try:
                status="0"
                while int(status) != int("200"):
                    client = http3.AsyncClient()
                    resp = await client.get(url)
                    status = resp.status_code
                    '''print("buscarMejoresPreciso")
                    print(status)'''
                    await asyncio.sleep(tRequest)
                '''resp = requests.get(url,timeout=9,proxies=proxi)'''
                '''time.sleep(0.001)'''
                pagina = BeautifulSoup(resp.content, "html.parser")
                articulos = json.loads(pagina.text)
                requestOk=True

            except:
                print("error PoeTrade request para tipo "+tipoDeObjeto+" pagina: "+url)
    tiempos=[]
    articulosMayorA = list(filter(lambda x: x.get("chaosValue") > mayorA, articulos["lines"]))

    for line in articulosMayorA:

        nombreArticulo = line.get("name")
        valuadoChaos = line.get("chaosValue")

        if mayorA < valuadoChaos:
            links = ""
            levelRequired = ""
            valudadoExalted = line.get("exaltedValue")
            level = str(line.get("gemLevel"))
            quality = str(line.get("gemQuality"))
            corrupted = line.get("corrupted")
            if requiereLink:
                links = str(line.get("links"))
            if requierelevelRequired:
                levelRequired = str(line.get("levelRequired"))
            '''print("nombreArticulo:"+nombreArticulo+" valuadoChaos:"+str(valuadoChaos)+" valudadoExalted:"+str(valudadoExalted)+" level:"+level+" quality:"+quality+" corrupted:"+str(corrupted)+" links:"+links+" levelRequired:"+levelRequired+ " ->", end="")
            '''
            precioMinimoEncontradoLista = []
            try:

                precioMinimoEncontradoLista, url2 ,tiempos= await preciosArticulo(tipoDeObjeto, nombreArticulo, level, quality,
                                                                    corrupted, links, levelRequired,proxi,tRequest)


                '''print(str(precioMinimoEncontradoLista)+" "+str(url2)+" "+str(tiempos))'''
                i=0
                precioMinimoEncontrado=999999999999999999999

                if precioMinimoEncontradoLista != [] :
                    precioMinimoEncontrado = precioMinimoEncontradoLista[i]
                    tiempo = tiempos[i]

                    precioComparacion=0
                    if len(precioMinimoEncontradoLista) >= 4:
                        precioComparacion = precioMinimoEncontradoLista[3]

                        if len(precioMinimoEncontradoLista) >= 3:
                            precioComparacion = precioMinimoEncontradoLista[2]
                            if len(precioMinimoEncontradoLista) >= 2:
                                precioComparacion = precioMinimoEncontradoLista[1]
                            else:
                                precioComparacion = line.get("chaosValue") * porsentaje

                    if tiempo.count("minutes") and int(tiempo[0:2])<30 and precioMinimoEncontrado < line.get("chaosValue") * porsentaje:
                        '''and precioMinimoEncontrado!=4'''
                        if precioMinimoEncontrado%1 >0:
                            '''winsound.Beep(2500, 100)'''
                        else:
                            winsound.Beep(2500, 100)
                            winsound.Beep(2500, 100)
                            winsound.Beep(2500, 100)

                        print("->T:" +str(int(tiempo[0:2]))+" O: "+tipoDeObjeto+" "+ nombreArticulo + "\t" + "PrecioRecomendado: " + str(
                            valudadoExalted) + "E" + "\t" + str(valuadoChaos) + "C\t" + " PrecioEncontrado: " + str(
                            round(precioMinimoEncontrado / precioExaltedXChaos, 2)) + "E\t" + str(
                            precioMinimoEncontrado) + "C\t" + url2)
                        '''elif precioMinimoEncontrado < line.get("chaosValue") * porsentaje and precioComparacion > line.get("chaosValue") * 0.6:
                            print("->Tiempo:" +str(int(tiempo[0:2]))+" " + nombreArticulo + "\t" + "PrecioRecomendado: " + str(
                                valudadoExalted) + "E" + "\t" + str(valuadoChaos) + "C\t" + " PrecioEncontrado: " + str(
                                round(precioMinimoEncontrado / precioExaltedXChaos, 2)) + "E\t" + str(
                                precioMinimoEncontrado) + "C\t" + url2)'''
                print(".", end="")
            except:
                print("-",end="")


    return url



precioExaltedXChaos=139
url=""
tipoDeObjetoAnt=""


puerto=None
listaTipos = ["SkillGem", "DivinationCard", "UniqueMap", "UniqueJewel", "UniqueFlask", "UniqueWeapon","UniqueArmour", "Beast"]
loop = asyncio.get_event_loop()
vectorDeFunciones = []
for tipo in listaTipos:
    if puerto != None:
        proxi = {'http': '127.0.0.1:' + str(puerto), 'https': '127.0.0.1:' + str(puerto)}
    else:
        proxi = None
    vectorDeFunciones.append(buscarMejoresPreciso(tipoDeObjetoAnt, tipo, 0.61, 89, proxi,0))

while 1:
    now = datetime.now()
    format = now.strftime('--------------Día :%d, Mes: %m, Año: %Y, Hora: %H, Minutos: %M, Segundos: %S--------------')
    print(format)



    all_groups=asyncio.gather(*vectorDeFunciones)
    results = loop.run_until_complete(all_groups)






sys.exit()





