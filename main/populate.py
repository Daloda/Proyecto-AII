# encoding:utf-8
from builtins import str
import os
import sys
import urllib.request

from bs4 import BeautifulSoup
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AII2Project.settings")
django.setup()

from main import models


# Obtener marcas
def procesar_pagina(d:str):
    fichero = urllib.request.urlopen(d)
    documento = BeautifulSoup(fichero, "html.parser")
    return documento


# Obtener marcas
def obtener_marcas():
    paginaGeneral = "https://motos.coches.net"
    paginaMarcas = procesar_pagina(paginaGeneral + "/fichas_tecnicas/")
    marcas = paginaMarcas.findAll("div", {"class": "box_brand"})
    recordsMarcas = []
    recordsUrls = []
    for marca in marcas:
        finalMarca = marca.a.getText()
        recordsMarcas.append(finalMarca);
        urls = marca.findAll("img")
        for url in urls:
            url = url.get("src").replace('..', '')
            finalUrl = paginaGeneral + url          
            recordsUrls.append(finalUrl)            
    return recordsMarcas, recordsUrls


# Obtener modelos
def obtener_modelos():
    marcas, urlMarcas = obtener_marcas()
    recordsModelos = []
    for marca in marcas:
        res = marca.replace(' ', '_').lower()
        paginaMarcas = procesar_pagina("https://motos.coches.net/fichas_tecnicas/" + res)
        modelos = paginaMarcas.find("div", {"id": "_ctl0_ContentPlaceHolder1_ModelsPictures1_photos"}).find_all('a')
        for modelo in modelos:
            final = modelo.get('href')
            recordsModelos.append(final) 
    return recordsModelos


# Obtener caracteristica moto
def cargar_url_foto(pagina):
    paginaCaracteristcas = pagina.find("a", {"id":"_ctl0_ContentPlaceHolder1_PhotosAd1_link_imgFotogrande"})
    urlImagen = paginaCaracteristcas.find("img").get("src")
    return urlImagen  


def obtener_caracteristicas():
    modelos = obtener_modelos()
    recordsCaracteristicasTotales = []
    for modelo in modelos:
        recordsCaracteristicasIndividuales = []
        paginaCaracteristica = procesar_pagina("https://motos.coches.net" + modelo)
        recordsCaracteristicasIndividuales.append(cargar_url_foto(paginaCaracteristica))
        modelosCaracteristicas = paginaCaracteristica.find("div", {"class": "princ-wrapper floatright"})
        caracteristicas = modelosCaracteristicas.findAll("span")
        for caracteristica in caracteristicas:
            res = "--"
            if(caracteristica.getText() != ""):
                res = caracteristica.getText()
            recordsCaracteristicasIndividuales.append(res)
        recordsCaracteristicasTotales.append(recordsCaracteristicasIndividuales)
    return recordsCaracteristicasTotales


# Cargar datos en BD
def cargar_marcas_bd():
    models.Marca.objects.all().delete()
    marcas, urlMarcas = obtener_marcas()
    tamano = len(marcas)
    try:
        for x in range(0, tamano):
            marcaD = marcas[x]
            urlMarcaD = urlMarcas[x] 
            marcaSave = models.Marca(marcaNombre=marcaD, logo=urlMarcaD)
            marcaSave.save()
    except:
        print("Hay un problema con la marca en la posición", x, ". Mensaje de error:", sys.exc_info()[0])
     
    print("Se han guardado " + str(x) + " marcas en la BD") 

        
def cargar_motos_bd():
    i = 0;
    models.Moto.objects.all().delete()
    caracteristicasTotales = obtener_caracteristicas()
    try:
        for caracteristica in caracteristicasTotales:
            i = i + 1;
            fotoFinal = caracteristica[0];
            marcaNombreD = caracteristica[1];
            modeloFinal = caracteristica[2];
            cilindradaFinal = caracteristica[3];
            potencia_maximaFinal = caracteristica[4];
            periodo_comercializacionFinal = caracteristica[5];
            
            marcaNombreFinal  = models.Marca.objects.all().get(pk=marcaNombreD)
        
            motoSave = models.Moto(foto=fotoFinal, modelo=modeloFinal, marcaNombre = marcaNombreFinal, cilindrada=cilindradaFinal, potencia_maxima=potencia_maximaFinal, periodo_comercializacion=periodo_comercializacionFinal)
            motoSave.save()
    except:
        print("Hay un problema con la moto en la posición", i, ". Mensaje de error:", sys.exc_info()[0])

    print("Se han guardado " + str(i) + " motos en la BD") 


if __name__ == '_main_':
    cargar_marcas_bd()
    cargar_motos_bd()

