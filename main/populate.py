# encoding:utf-8
import os
from tkinter import *
from tkinter import messagebox
import urllib.request

from bs4 import BeautifulSoup
import django
from whoosh import qparser
from whoosh.fields import Schema, TEXT
from whoosh.index import create_in, open_dir
from whoosh.qparser.default import MultifieldParser
import shelve
from main.recommendations import  transformPrefs, calculateSimilarItems

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
        print("Hay un problema con la marca en la posición " + str(x) + ". Mensaje de error:", sys.exc_info()[0])
        messagebox.showinfo("Hay un problema con la marca en la posición" + str(x) + ". Mensaje de error:", sys.exc_info()[0])
     
    print("Se han guardado " + str(x) + " marcas en la BD") 
    messagebox.showinfo("Marcas guardada", "Se han guardado " + str(x) + " marcas en la BD")

        
def cargar_motos_bd():
    i = 0;
    models.Moto.objects.all().delete()
    caracteristicasTotales = obtener_caracteristicas()
    try:
        for caracteristica in caracteristicasTotales:
            i = i + 1;
            idFinal = str(i)
            fotoFinal = caracteristica[0];
            marcaNombreD = caracteristica[1];
            modeloFinal = caracteristica[2];
            cilindradaFinal = caracteristica[3];
            potencia_maximaFinal = caracteristica[4];
            periodo_comercializacionFinal = caracteristica[5];

            marcaNombreFinal = models.Marca.objects.all().get(pk=marcaNombreD)
        
            # Guardamos los valores en base de datos             
            motoSave = models.Moto(id=idFinal, foto=fotoFinal, modelo=modeloFinal, marcaNombre=marcaNombreFinal, cilindrada=cilindradaFinal, potencia_maxima=potencia_maximaFinal, periodo_comercializacion=periodo_comercializacionFinal)
            motoSave.save()
    except:
        print("Hay un problema con la moto en la posición " + str(i) + ". Mensaje de error:", sys.exc_info()[0])
        messagebox.showinfo("Hay un problema con la moto en la posición" + str(i) + ". Mensaje de error:", sys.exc_info()[0])

    print("Se han guardado " + str(i) + " motos en la BD") 
    messagebox.showinfo("Motos guardada", "Se han guardado " + str(i) + " motos en la BD")



# Se aplica Whoosh----------------------------------------
dirindex = "Index"

def cargar_marcas_bd_whoosh():
    models.Marca.objects.all().delete()
    marcas, urlMarcas = obtener_marcas()
    tamano = len(marcas)
    for x in range(0, tamano):
        marcaD = marcas[x]
        urlMarcaD = urlMarcas[x] 
        marcaSave = models.Marca(marcaNombre=marcaD, logo=urlMarcaD)
        marcaSave.save()


def add_docs(writer):
    marcas = models.Marca.objects.all()
    if not len(marcas) > 0:
        cargar_marcas_bd_whoosh()
    caracteristicasTotales = obtener_caracteristicas()
    i = 0
    try:
        for caracteristica in caracteristicasTotales:
            i = i + 1;
            idWhoosh = str(i)
            fotoWhoosh = caracteristica[0];
            marcaNombreD = caracteristica[1];
            modeloWhoosh = caracteristica[2];
            cilindradaWhoosh = caracteristica[3];
            potencia_maximaWhoosh = caracteristica[4];
            periodo_comercializacionWhoosh = caracteristica[5];
                
            marcaNombreWhoosh = models.Marca.objects.all().get(pk=marcaNombreD).marcaNombre
            
            writer.add_document(id=idWhoosh, foto=fotoWhoosh, marcaNombre=marcaNombreWhoosh, modelo=modeloWhoosh, cilindrada=cilindradaWhoosh, potencia_maxima=potencia_maximaWhoosh, periodo_comercializacion=periodo_comercializacionWhoosh)
    except:
        print("Hay un problema con la moto en la posición " + str(i) + ". Mensaje de error:", sys.exc_info()[0])
        messagebox.showinfo("Hay un problema con la moto en la posición" + str(i) + ". Mensaje de error:", sys.exc_info()[0])
           
    print("Fin de indexado.", "Se han indexado " + str(i) + " motos")
    messagebox.showinfo("Fin de indexado", "Se han indexado " + str(i) + " motos")

        
def indexar():
    if not os.path.exists(dirindex):
        os.mkdir(dirindex)
    else:
        sn = 's'
    if sn == 's':
        ix = create_in(dirindex, schema=get_schema())
        writer = ix.writer()
        add_docs(writer)
        writer.commit()


def get_schema():
    return Schema(id=TEXT(stored=True), foto=TEXT(stored=True), marcaNombre=TEXT(stored=True), modelo=TEXT(stored=True),
                  cilindrada=TEXT(stored=True), potencia_maxima=TEXT(stored=True), periodo_comercializacion=TEXT(stored=True))
     
     
def buscarModelo():

    def mostrar_lista(event):
        lb.delete(0, END)  # borra toda la lista
        ix = open_dir(dirindex)
        with ix.searcher() as searcher:
            query = MultifieldParser(["modelo","marcaNombre"], ix.schema, group = qparser.AndGroup).parse(str(en.get()))
            results = searcher.search(query, limit=None)
            for r in results:
                lb.insert(END, r['foto'])
                lb.insert(END, r['marcaNombre'])
                lb.insert(END, r['modelo'])
                lb.insert(END, r['cilindrada'])
                lb.insert(END, r['potencia_maxima'])
                lb.insert(END, r['periodo_comercializacion'])
                lb.insert(END, '')

    v = Toplevel()
    v.title("Busqueda por marca o modelo")
    f = Frame(v)
    f.pack(side=TOP)
    l = Label(f, text="Introduzca marca o modelo de moto:")
    l.pack(side=LEFT)
    en = Entry(f)
    en.bind("<Return>", mostrar_lista)
    en.pack(side=LEFT)
    sc = Scrollbar(v)
    sc.pack(side=RIGHT, fill=Y)
    lb = Listbox(v, yscrollcommand=sc.set)
    lb.pack(side=BOTTOM, fill=BOTH)
    sc.config(command=lb.yview)
    

def loadDict():
    Prefs={}
    shelf = shelve.open("dataRS.dat")
    ratings = models.Rating.objects.all()
    for ra in ratings:
        user = int(ra.usuario.id)
        itemid = int(ra.moto.id)
        rating = float(ra.rating)
        Prefs.setdefault(user, {})
        Prefs[user][itemid] = rating
    shelf['Prefs']=Prefs
    shelf['ItemsPrefs']=transformPrefs(Prefs)
    shelf['SimItems']=calculateSimilarItems(Prefs, n=10)
    shelf.close()
            

root = Tk()
menubar = Menu(root)

indexmenu = Menu(menubar, tearoff=0)
indexmenu.add_command(label="Salir", command=root.quit)
menubar.add_cascade(label="Inicio", menu=indexmenu);

find2menu = Menu(menubar, tearoff=0)
find2menu.add_command(label="Indexar", command=indexar)
find2menu.add_command(label="Busqueda por marca o modelo", command=buscarModelo)
menubar.add_cascade(label="Indices", menu=find2menu);

find3menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="Cargar BD", menu=find3menu);
find3menu.add_command(label="Cargar Marcas", command=cargar_marcas_bd)
find3menu.add_command(label="Cargar Motos", command=cargar_motos_bd)

find4menu = Menu(menubar, tearoff=0)
menubar.add_cascade(label="SR", menu=find4menu);
find4menu.add_command(label="Cargar SR", command=loadDict)

root.config(menu=menubar)
root.mainloop()
    
