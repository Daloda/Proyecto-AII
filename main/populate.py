# encoding:utf-8
from builtins import str
import urllib.request

from bs4 import BeautifulSoup



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
        finalMarca = marca.a.getText().replace(' ', '_')
        recordsMarcas.append(finalMarca.lower());
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
        paginaMarcas = procesar_pagina("https://motos.coches.net/fichas_tecnicas/" + marca)
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
def cargar_bd():
    i = 0;
    caracteristicasTotales = obtener_caracteristicas()
    marcas, urlMarcas = obtener_marcas()
    tamano = len(marcas)
    for caracteristica in caracteristicasTotales:
        i = i + 1;
        urlD = caracteristica[0];
#       print(urlD)
        modeloD = caracteristica[1];
#       print(modeloD)
#       fabricanteD = caracteristica[2];
#       print(fabricanteD)
        cilindradaD = caracteristica[3];
#       print(cilindradaD)
        potencia_maximaD = caracteristica[4];
#       print(potencia_maximaD)
        periodo_comercializacionD = caracteristica[5];
#       print(periodo_comercializacionD)

#        motoSave = Moto(foto=urlD, modelo=modeloD, cilindrada=cilindradaD, potencia_maxima=potencia_maximaD, periodo_comercializacion=periodo_comercializacionD)
#        motoSave.save()
        
    tamano = len(marcas)
    for x in range(0, tamano):
        marcaD = marcas[x]
        urlMarcaD = urlMarcas[x] 
 #       marcaSave = Marca(nombre=marcaD, logo=urlMarcaD)
#        marcaSave.save()
    
    print("Se han guardado " + str(i) + " motos en la BD") 
    print("Se han guardado " + str(x) + " marcas de motos") 

    
print(cargar_bd())

