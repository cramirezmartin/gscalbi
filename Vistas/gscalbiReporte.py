# coding=utf-8
import os
import sys

from PyQt4 import  QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import qgis
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *

from ..Entidad.vector import _vector
from ..Entidad.configuracion import _configuracion
import unicodedata
import time
import math
import matplotlib
import pylab
import numpy
from pylab import *
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import numpy as np

"""
Clase interfaz que permite mostrar los resultados del análisis, exportarlos a HTML y PDF y
construir el árbol de capas de los diferentes clústeres generados.
"""
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'UI//gscalbiReporte.ui'))
class _gscalbiReporte(QtGui.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        super(_gscalbiReporte, self).__init__(parent)
        self.setupUi(self)
        self.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"//..//Recursos//icon.png"))
        self.btnCerrar.clicked.connect(self.close)
        self.configuracion = NULL
        self.matrix = NULL

        """
        Creando una ventana para ir mostrando al usuario el avance del algoritmo a medida que
        va avanzando por cada uno de los pasos.
        """
        self.ventana = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.ventana.resize(300, 130)
        self.ventana.setMaximumSize(300, 130)
        self.ventana.setMinimumSize(300, 130)
        self.ventana.setModal(True)
        self.ventana.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"//..//Recursos//icon.png"))
        self.ventana.setWindowTitle("Progreso GSCALBI")
        self.ventana.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.ventana.setStyleSheet("*{background-color: rgb(255, 255, 255);}");
        label = QtGui.QLabel(self.ventana)
        label.resize(220,45)
        label.move(70,20)
        label.setText("Visualizando resultados")
        self.lblAccion = QtGui.QLabel(self.ventana)
        self.lblAccion.resize(220,15)
        self.lblAccion.move(70,50)
        self.pbar = QtGui.QProgressBar(self.ventana)
        self.pbar.resize(210,20)
        self.pbar.move(40,80)
        self.ventana.show()

    """
    Funcionalidad: construirHTML
    Recibe: (_configuracion:obj, array, array, array)
    Retorno: string
    Descripción: Permite construir el texto de salida con toda la información de la ejecución de la aplicación
                 Dicho texto se retorna para posteriormente guardarlo en HTML y PDF
    """
    def construirHTML(self, configuracion, matrix, salidasWeka, tiempos):
        self.configuracion = configuracion
        self.matrix = matrix

        """ Estableciendo el mensaje a mostrar para los parámetros de la 'posición de el espacio' """
        self.posicionTipo = '"sin especificar"'
        self.distanciaLimite = '"sin especificar"'
        self.sistemaCoordenadas = '"sin especificar"'
        if configuracion.getSiPosicion() :
            self.posicionTipo = self.configuracion.getPosicionEspacio()
            self.distanciaLimite = self.configuracion.getDistanciaLimite()
            self.sistemaCoordenadas = self.configuracion.getSistemaCoordenadas()

        """ Limpiando la salidas de Weka para sustituir el caracter de 'salto de linea' y 'espacio' de UNICODE a HTML """
        self.salidaElementos = salidasWeka[0]
        self.salidaElementos = self.salidaElementos.replace("\n\n","<br>")
        self.salidaElementos = self.salidaElementos.replace("\n","<br>")
        self.salidaElementos = self.salidaElementos.replace(" ","&nbsp;")
        self.elementosProblemas = salidasWeka[2]
        self.salidaLocaciones = salidasWeka[1]
        self.salidaLocaciones = self.salidaLocaciones.replace("\n\n","<br>")
        self.salidaLocaciones = self.salidaLocaciones.replace("\n","<br>")
        self.salidaLocaciones = self.salidaLocaciones.replace(" ","&nbsp;")
        self.locacionesProblemas = salidasWeka[3]

        """
        Construyendo la cedecera del informe
        Contiene el logo de la aplicación, el título y los parámetros establecido para la posición en el espacio,
        distancia máxima entre elementos y locaciones y si se especificó el parámetro de asociación por definición
        """
        html = '<table><tr><td width="60" rowspan="2"><img src="data:image/jpeg;base64,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" width="42" height="42"></td><td>GeoSpatial Clustering Around Location Based on Intersection</td></tr><tr><td>Agrupamiento Geoespacial por Locaciones Basado en Intersecci&oacute;n</td></tr></table><br/>'
        #html += "<br/>Mapa trabajado con el sistema de coordenadas en: " + self.sistemaCoordenadas
        html += "<br/>Distancia m&aacute;xima entre elementos y locaciones: <b><font color='blue'>" + str(self.distanciaLimite) + "</font></b>"
        html += "<br/>Posici&oacute;n de los elementos con respecto a las locaciones: <b><font color='blue'>" + self.posicionTipo + "</font></b>"
        parametrosAsociacion = "<b><font color='blue'>Distancia calculada</font></b>"
        if self.configuracion.getSiAsociacion() : parametrosAsociacion = "Establecida por el campo \"<b><font color='blue'>" + self.configuracion.getParametroAsociacion() + "\"</font></b>"
        html += "<br/>Par&aacute;metro de asociaci&oacute;n: <b><font color='blue'>" + parametrosAsociacion + "</font></b>"
        html += "<br/>M&eacute;todo de agrupaci&oacute;n: <b><font color='blue'>" + self.configuracion.getMetodoAgrupacion() + "</font></b>"

        """
        Construyendo la información de salida para el agrupamiento de los elementos
        Contiene los datos iniciales tenidos en cuenta para el agrupamiento, la salida de Weka
        y los elementos con problemas
        """
        html += "<br/><br/>Resultados del agrupamiento de los elementos: <b><font color='blue'>\""+self.configuracion.getCapaElementos()+"\"</font></b><br>Cl&uacute;steres: <b><font color='blue'>"+str(self.configuracion.getClustersElementos())+"</font></b><br>Variables analizadas: "
        for i in self.configuracion.getVariablesElementos() : html += "<b><font color='blue'>"+i+"</font></b>, "
        html = html[0:-2]+"<br>Salida de Weka para el agrupamiento de los elementos:<br><font color='blue'>"+self.salidaElementos+"</font>"
        html += "<br/>Elementos con problemas: <font color='red'>" + str(self.elementosProblemas) + "</font>"

        """
        Construyendo la información de salida para el agrupamiento de las locaciones
        Contiene los datos iniciales tenidos en cuenta para el agrupamiento, la salida de Weka
        y las locaciones con problemas
        """
        html += "<br/><br/>Resultados del agrupamiento de las locaciones: <b><font color='blue'>\""+self.configuracion.getCapaLocaciones()+"\"</font></b><br>Cl&uacute;steres: <b><font color='blue'>"+str(self.configuracion.getClustersLocaciones())+"</font></b><br>Variables analizadas: "
        for i in self.configuracion.getVariablesLocaciones(): html += "<b><font color='blue'>"+i+"</font></b>, "
        html = html[0:-2]+"<br>Salida de Weka para el agrupamiento de las locaciones:<br><font color='blue'>"+self.salidaLocaciones+"</font>"
        html += "<br/>Locaciones con problemas: <font color='red'>" + str(self.locacionesProblemas) + "</font>"

        """
        Construyendo la información de salida para el algoritmo diseñado
        Contiene la matrix de intersección que muestra la cantidad de elementos por clústeres
        """
        html += "<br/><br/>Resultados del algoritmo GSCALBI:<br><br>Matrix de intersecci&oacute;n<br>"
        html += "<table border='0' cellspacing='10'>"
        html += "<tr><td></td>"
        for i in range(0, self.configuracion.getClustersLocaciones()):
            html += "<td><font color='blue'><b><u>CL"+str(i)+"</u></b></font></td>"
        html += "</tr>"
        pos = 0
        for i in matrix:
            html += "<tr><td><font color='blue'><b>CE"+str(pos)+"|</b></font></td>"
            pos += 1
            for j in i:
                html += "<td><font color='blue'>"+str(len(j))+"</font></td>"
            html += "</tr>"
        html += "</table><br>"

        """
        Construyendo la información de salida para el algoritmo diseñado
        Contiene los tiempos demorados en cada uno de los pasos
        """
        html += "Tiempo de ejecuci&oacute;n de la asociaci&oacute;n: <font color='blue'>" + str(round(tiempos[0],5)) + "</font> segundos<br>"
        html += "Tiempo de ejecuci&oacute;n de los agrupamientos: <font color='blue'>" + str(round(tiempos[1],5)) + "</font> segundos<br>"
        html += "Tiempo de ejecuci&oacute;n de la intersecci&oacute;n: <font color='blue'>" + str(round(tiempos[2],5)) + "</font> segundos<p>&nbsp;</p>"

        """
        Construyendo la información de salida para el algoritmo diseñado
        Contiene la información (id_Elemento, id_Locación_Asociada) para cada objeto en cada celda de la matrix de intersección.
        """
        html += "RESULTADOS DE LOS CL&Uacute;STERES FINALES <b>(id_Elemento, id_Locaci&oacute;n_Asociada)</b>:<br><br>"
        c = 0
        for i in range(0, self.configuracion.getClustersElementos()):
            for j in range(0, self.configuracion.getClustersLocaciones()):
                html += "<b>Elementos de la celda CE" + str(i) + "-CL" + str(j) + "</b><br/>"
                for item in self.matrix[i][j]:
                    html += "(" + item[0] + ", " + item[1] + "), "
                html = html[0:-2] + "<br/><br/>"

        self.resultado = html
    # ------------------------------------------------------------------------------------------------------------------
    """
    Funcionalidad: mostrarResultados
    Descripción: Permite capturar la salida del informe construida y guardarla en HTML y PDF
    """
    def mostrarResultados(self):
        self.txbResultados.setHtml(self.resultado)
        self.show()

        """ Creando el fichero HTML """
        archivo = open(self.configuracion.getDireccion()+"//resultado.html", "w")
        archivo.write("<style type='text/css'>*{font-family:monospace} td p{padding: 10px}</style>"+self.resultado)
        archivo.close()

        """ Creando el fichero PDF """
        printer = QtGui.QPrinter(QtGui.QPrinter.HighResolution)
        printer.setPageSize(QtGui.QPrinter.Letter)
        printer.setColorMode(QtGui.QPrinter.Color)
        printer.setOutputFormat(QtGui.QPrinter.PdfFormat)
        printer.setOutputFileName(self.configuracion.getDireccion()+"//resultado.pdf")
        self.txbResultados.print_(printer)
    # ------------------------------------------------------------------------------------------------------------------
    """
    Funcionalidad: construirCapas
    Descripción: Permite construir el árbol de capa asociadas a la ejecución del algoritmo.
                 Cada capa nueva creada corresponde con un clúster (celda en la matrix de asociación)
                 y en cada una de ellas se encuentran solo los elementos correspondiente
                 a cada una de las celdas de la matrix de intersección asociada a cada capa
    """
    def construirCapas(self):
        arreglo = []
        """ Recorriendo el árbol de capas para eliminar las capas de agrupamientos previos """
        self.ventanaActualizar("Borrando capas de resultados anteriores", 25)
        for i in range(0, 9):
            for j in range(0, 9):
                capas = QgsMapLayerRegistry.instance().mapLayersByName("CE"+str(i)+"_CL"+str(j))
                for layer in capas : arreglo.append(layer.id())
        QgsMapLayerRegistry.instance().removeMapLayers(arreglo)
        
        """ Creando el grupo de capas donde se van a agrupar las capas generadas producto del análisis """
        legenda = iface.legendInterface()
        capas = []
        pos = 0
        grupoName = "GSCALBI"
        for g in legenda.groups():
            if g == grupoName : legenda.removeGroup(pos)
            pos += 1
        grupo = 0
        try : QgsProject.instance().layerTreeRoot().insertGroup(grupo, grupoName)
        except : legenda.addGroup(grupoName, True, grupo)

        """ Creando la carpeta donde se guardarán cada una de las capas generadas producto del análisis """
        if not os.path.exists(self.configuracion.getDireccion()+"//capas//") : os.makedirs(self.configuracion.getDireccion()+"//capas//")
        ficheros = os.walk(self.configuracion.getDireccion()+"//capas//")
        for root, dirs, files in ficheros:
            for f in files :
                os.remove(self.configuracion.getDireccion()+"//capas//"+f)

        """ Inicializando valores neecsarios para crear las capas """
        capa = QgsMapLayerRegistry.instance().mapLayersByName(self.configuracion.getCapaElementos())[0]
        """
        Clonando la capa de los elementos tantas veces como clústeres de estos haya
        Se les coloca de nombre a cada capa creada CEx_CLy indicando que estas contendrán solo los elementos
        de la matrix de intersección para dicha celda
        """
        exp_crs = QgsCoordinateReferenceSystem(4326, QgsCoordinateReferenceSystem.EpsgCrsId)
        for i in range(0, self.configuracion.getClustersElementos()):
            for j in range(0, self.configuracion.getClustersLocaciones()):
                self.ventanaActualizar("Creando la capa CE" + str(i) + "_CL" + str(j),self.pbar.value() + 20 / self.configuracion.getClustersElementos())
                QgsVectorFileWriter.writeAsVectorFormat(capa,self.configuracion.getDireccion()+"//capas//CE"+str(i)+"_CL"+str(j)+".shp","utf-8",exp_crs,"ESRI Shapefile")
                layer = QgsVectorLayer(self.configuracion.getDireccion()+"//capas//CE"+str(i)+"_CL"+str(j)+".shp", "CE"+str(i)+"_CL"+str(j), "ogr")
                capas.append(layer)
                QgsMapLayerRegistry.instance().addMapLayer(layer)

        """
        Una vez clonadas las capas de los elementos y asignado el nombre representativo para cada una se actualizan
        Para hacer esto se recorren cada una de las geometrías de cada una de las capas y se busca si este
        se encuentra o no en la matrix de intersección
        De no estar el elemento en la celda correspondiente de la matrix de intersección se agrega su identificador,
        asignado por QGis, al arreglo de elementos a borrar
        Al final se borran de la capa todos aquellos elementos cuyo identificador se encuentre en el arreglo de elementos a borrar
        """
        for i in range(0, self.configuracion.getClustersElementos()):
            for j in range(0, self.configuracion.getClustersLocaciones()):
                objetosBorrar = []
                self.ventanaActualizar("Actualizando la capa CE" + str(i) + "_CL" + str(j),self.pbar.value() + 20 / self.configuracion.getClustersElementos())
                capa = QgsMapLayerRegistry.instance().mapLayersByName("CE" + str(i) + "_CL" + str(j))[0]
                for features in capa.getFeatures():
                    idElement = int(features.attributes()[capa.dataProvider().fieldNameIndex(self.configuracion.getIdElementos())])
                    esta = False
                    for item in self.matrix[i][j]:
                        if str(idElement) == str(item[0]):
                            esta = True
                            break
                    if esta == False : objetosBorrar.append(features.id())

                capa = QgsMapLayerRegistry.instance().mapLayersByName("CE" + str(i) + "_CL" + str(j))[0]
                capa.startEditing()
                for obj in objetosBorrar : capa.deleteFeature(obj)
                capa.commitChanges()

        """ Una vez actualizadas todas las capas se mueven para el grupo creado inicialmente """
        self.ventanaActualizar("Moviendo capas para el grupo GSCALBI", 98)
        for c in capas : legenda.moveLayer(c, grupo)
        self.ventanaActualizar("Terminando ...", 100)
        time.sleep(0.5)
        self.ventana.close()
    # ------------------------------------------------------------------------------------------------------------------
    """
    Funcionalidad: indiceSilueta
    Descirpción: Permite construir las gráficas referentes al índice de silueta para evaluar la calidad de los clústeres
    """
    def indiceSilueta(self):
        try:
            fig = plt.figure(u"Índice de Silueta")
            rect = fig.patch
            rect.set_facecolor('white')
            plt.rc('font', size=12)
            # ---------------------------------------------------------------------------------------------------------------
            """ Calculando para todos los elementos la distancia media interna entre el elementos y los demás elementos del mismo clúster """
            for elemento in self.configuracion.getVectoresElementos():
                distancia = 0
                cantidad = 0
                for objeto in self.configuracion.getVectoresElementos():
                    if elemento.getCluster() == objeto.getCluster():
                        distancia += self.distanciaObjetos(elemento.getId(), elemento.getDatos(), objeto.getId(), objeto.getDatos())
                        cantidad += 1
                if cantidad > 1: cantidad -= 1
                if cantidad != 0: elemento.setDistanciaIntraCluster(distancia/cantidad)
            #---------------------------------------------------------------------------------------------------------------
            """ Calculando para todos los elementos la distancia media externa entre los elementos y los elementos de los demás clústeres """
            for elemento in self.configuracion.getVectoresElementos():
                for cluster in range(0, self.configuracion.getClustersElementos()):
                    if elemento.getCluster() != cluster:
                        distancia = 0
                        cantidad = 0
                        for objeto in self.configuracion.getVectoresElementos():
                            if objeto.getCluster() == cluster:
                                distancia += self.distanciaObjetos(elemento.getId(), elemento.getDatos(), objeto.getId(), objeto.getDatos())
                                cantidad += 1
                        if cantidad != 0 : elemento.setDistanciaExtraCluster(distancia/cantidad)
            # ---------------------------------------------------------------------------------------------------------------
            """ Construyendo las gráficas s(i) de los clústeres sin reducir """
            atr=['#0000FF','#00FF00','#FF0000','#FF00FF','#FFFF00','#00FFFF','#FF8000','#000000', '#CCCCCC']
            mark = ['o', 'x', 'D', '^', 's', '*', 'p', 'h', '.']
            plt.subplot(1, 3, 1)
            mayor = 0
            for cluster in range(0, self.configuracion.getClustersElementos()):
                array = []
                array2 = []
                for elemento in self.configuracion.getVectoresElementos():
                    if elemento.getCluster() == cluster:
                        array.append(elemento.getIndiceSilueta())
                        array2.append(elemento.getId())
                        if mayor < elemento.getId() : mayor = elemento.getId()
                #plt.scatter(array2,array, label=u"Clúster "+str(cluster), color=atr[cluster])
                if len(array) != 0 and len(array2) != 0:
                    plt.scatter(array2, array, label=u"Clúster " + str(cluster), color='k', marker=mark[cluster], facecolors='none', s=100)
            """ Configurando los parámetros de las gráficas de los clústeres sin reducir"""
            plt.plot([0, mayor], [0, 0], color='k')
            plt.xlabel("Elementos")
            plt.ylabel("S(i)")
            plt.grid(True)
            plt.legend(loc="lower right", prop={"size": 10})
            plt.axis([-10, mayor+10, -1.5, 1.1])
            plt.title(u"Clústeres Elementos")
            # ---------------------------------------------------------------------------------------------------------------
            """ Calculando para las locaciones la distancia media interna entre la locación y los demás objetos del mismo clúster """
            for locacion in self.configuracion.getVectoresLocaciones():
                distancia = 0
                cantidad = 0
                for objeto in self.configuracion.getVectoresLocaciones():
                    if locacion.getCluster() == objeto.getCluster():
                        distancia += self.distanciaObjetos(locacion.getId(), locacion.getDatos(), objeto.getId(), objeto.getDatos())
                        cantidad += 1
                if cantidad > 1: cantidad -= 1
                if cantidad != 0: locacion.setDistanciaIntraCluster(distancia / cantidad)
            # ---------------------------------------------------------------------------------------------------------------
            """ Calculando para las locaciones la distancia media externa entre la locación y los objetos de los demás clústeres """
            for locacion in self.configuracion.getVectoresLocaciones():
                for cluster in range(0, self.configuracion.getClustersLocaciones()):
                    if locacion.getCluster() != cluster:
                        distancia = 0
                        cantidad = 0
                        for objeto in self.configuracion.getVectoresLocaciones():
                            if objeto.getCluster() == cluster:
                                distancia += self.distanciaObjetos(locacion.getId(), locacion.getDatos(), objeto.getId(), objeto.getDatos())
                                cantidad += 1
                        if cantidad != 0 : locacion.setDistanciaExtraCluster(distancia / cantidad)
            # ---------------------------------------------------------------------------------------------------------------
            """ Construyendo las gráficas s(i) de las locaciones  """
            plt.subplot(1, 3, 2)
            mayor = 0
            for cluster in range(0, self.configuracion.getClustersLocaciones()):
                array = []
                array2 = []
                for locacion in self.configuracion.getVectoresLocaciones():
                    if locacion.getCluster() == cluster:
                        array.append(locacion.getIndiceSilueta())
                        array2.append(locacion.getId())
                        if mayor < locacion.getId(): mayor = locacion.getId()
                # plt.scatter(array2,array, label=u"Clúster "+str(cluster), color=atr[cluster])
                if len(array) != 0 and len(array2) != 0:
                    plt.scatter(array2, array, label=u"Clúster " + str(cluster), color='k', marker=mark[cluster], facecolors='none', s=100)
            """ Configurando los parámetros de las gráficas de las locaciones """
            plt.plot([0, mayor], [0, 0], color='k')
            plt.xlabel("Locaciones")
            plt.grid(True)
            plt.legend(loc="lower right", prop={"size": 10})
            plt.axis([-10, mayor + 10, -1.5, 1.1])
            plt.title(u"Clústeres Locaciones")
            # ---------------------------------------------------------------------------------------------------------------
            """ Configurando los arreglos necesarios para graficar el S(i) de los clústeres reducidos """
            clusteresFinales = []
            vectoresFinales = []
            for i in range(0, self.configuracion.getClustersElementos()):
                clusteresFinales.append([])
            """ Obteniendo de la matrix los identificadores de los elementos en los clústeres finales """
            for i in range(0, len(self.matrix)):
                for y in range(0, len(self.matrix[i])):
                    if len(clusteresFinales[i]) < len(self.matrix[i][y]):
                        clusteresFinales[i] = self.matrix[i][y]
            """ Obteniendo cada vector de cada un de los identificadores de los vectores de los clústeres finales """
            for i in range(0, len(clusteresFinales)):
                for j in range(0, len(clusteresFinales[i])):
                    vectoresFinales.append(self.getElemento(clusteresFinales[i][j][0]))
            # ---------------------------------------------------------------------------------------------------------------
            """ Calculando la distancia entre el elementos y los demás elementos del mismo clúster reducido"""
            for elemento in vectoresFinales:
                distancia = 0
                cantidad = 0
                for objeto in vectoresFinales:
                    if elemento.getCluster() == objeto.getCluster():
                        distancia += self.distanciaObjetos(elemento.getId(), elemento.getDatos(), objeto.getId(),objeto.getDatos())
                        cantidad += 1
                if cantidad > 1: cantidad -= 1
                if cantidad != 0: elemento.setDistanciaIntraClusterReducido(distancia/cantidad)
            # ---------------------------------------------------------------------------------------------------------------
            """ Calculando la distancia entre los elementos y los elementos de los demás clústeres reducidos """
            for elemento in vectoresFinales:
                for cluster in range(0, self.configuracion.getClustersElementos()):
                    if elemento.getCluster() != cluster:
                        distancia = 0
                        cantidad = 0
                        for objeto in vectoresFinales:
                            if objeto.getCluster() == cluster:
                                distancia += self.distanciaObjetos(elemento.getId(), elemento.getDatos(),objeto.getId(), objeto.getDatos())
                                cantidad = cantidad + 1
                        if cantidad != 0 : elemento.setDistanciaExtraClusterReducido(distancia/cantidad)
            # ---------------------------------------------------------------------------------------------------------------
            """ Construyendo las gráficas s(i) de los clústers reducidos """
            plt.subplot(1, 3, 3)
            mayor = 0
            for cluster in range(0, self.configuracion.getClustersElementos()):
                array = []
                array2 = []
                for elemento in vectoresFinales:
                    if elemento.getCluster() == cluster:
                        array.append(elemento.getIndiceSiluetaReducido())
                        array2.append(elemento.getId())
                        if mayor < elemento.getId(): mayor = elemento.getId()
                #plt.scatter(array2, array, label=u"Clúster " + str(cluster), color=atr[cluster])
                if len(array) != 0 and len(array2) != 0:
                    plt.scatter(array2, array, label=u"Clúster " + str(cluster), color='k', marker=mark[cluster], facecolors='none', s=100)
            """ Configurando los parámetros de las gráficas de los clústeres reducidos """
            plt.plot([0, mayor], [0, 0], color='k')
            plt.xlabel("Elementos")
            plt.title(u"Clústeres Reducidos")
            plt.grid(True)
            plt.legend(loc="lower right", prop={"size": 10})
            plt.axis([-10, mayor + 10, -1.5, 1.1])
            fig.show()
            #savefig(self.configuracion.getDireccion()+"//indiceSilueta.png")
            # ---------------------------------------------------------------------------------------------------------------
            """ Ordenando los arreglo de todos los elementos """
            vectores = self.configuracion.getVectoresElementos()
            for i in range(0, len(vectores)):
                for j in range(0, len(vectores)):
                    if vectores[i].getId() < vectores[j].getId():
                        tmp = vectores[i]
                        vectores[i] = vectores[j]
                        vectores[j] = tmp
            """ Ordenando los arreglo de los elementos de los clústeres reducidos"""
            for i in range(0, len(vectoresFinales)):
                for j in range(0, len(vectoresFinales)):
                    if vectoresFinales[i].getId() < vectoresFinales[j].getId():
                        tmp = vectoresFinales[i]
                        vectoresFinales[i] = vectoresFinales[j]
                        vectoresFinales[j] = tmp
            # ---------------------------------------------------------------------------------------------------------------
            """
                Creando el HTML de la tabla de 'distancia media interna', 'distancia media externa' y s(i)
                para todos los elementos de los clústeres finales completos
            """
            self.resultado += "<br/><br/><b>VALIDACI&Oacute;N DE LOS CL&Uacute;STERES POR: <font color='blue'>&Iacute;ndice de silueta</font></b><br/>"
            html = "<br/><br/>Resultados de los cl&uacute;res completos<br/>"
            html += "<table border='1'>"
            html += "<tr style='color: white; background: black;'>"
            html += "<td><p>Elemento</p></td>"
            html += "<td><p>Cl&uacute;ster</p></td>"
            html += "<td><p>Distancia media interna</p></td>"
            html += "<td><p>Distancia media externa</p></td>"
            html += "<td><p>S(i)</p></td>"
            html += "</tr>"
            for elemento in self.configuracion.getVectoresElementos():
                html += "<tr>"
                html += "<td><p>" + str(elemento.getId()) + "</p></td>"
                html += "<td><p>" + str(elemento.getCluster()) + "</p></td>"
                html += "<td><p>" + str(elemento.getDistanciaIntraCluster()) + "</p></td>"
                html += "<td><p>" + str(elemento.getDistanciaExtraCluster()) + "</p></td>"
                html += "<td><p>" + str(elemento.getIndiceSilueta()) + "</p></td>"
                html += "</tr>"
            html += "</table>"
            """
                Creando el HTML de la tabla de 'distancia media interna', 'distancia media externa' y s(i)
                para todos los elementos de los clústeres finales reducidos
            """
            html += "<br/><br/>Resultados de los cl&uacute;res reducidos<br/>"
            html += "<table border='1'>"
            html += "<tr style='color: white; background: black;'>"
            html += "<td><p>Elemento</p></td>"
            html += "<td><p>Cl&uacute;ster</p></td>"
            html += "<td><p>Distancia media interna</p></td>"
            html += "<td><p>Distancia media externa</p></td>"
            html += "<td><p>S(i)</p></td>"
            html += "</tr>"
            for elemento in vectoresFinales:
                html += "<tr>"
                html += "<td><p>" + str(elemento.getId()) + "</p></td>"
                html += "<td><p>" + str(elemento.getCluster()) + "</p></td>"
                html += "<td><p>" + str(elemento.getDistanciaIntraClusterReducido()) + "</p></td>"
                html += "<td><p>" + str(elemento.getDistanciaExtraClusterReducido()) + "</p></td>"
                html += "<td><p>" + str(elemento.getIndiceSiluetaReducido()) + "</p></td>"
                html += "</tr>"
            html += "</table>"
            self.resultado += html
        except:
            QMessageBox.critical(self, "Error", u"Ha ocurrido un error durante la validación de los clústeres, repita el análisis. Si el problema persiste reinicie la aplicación.")
    # ------------------------------------------------------------------------------------------------------------------
    """
    Funcionalidad: distanciaObjetos
    Recibe: (array[numéricos], array[numéricos])
    Retorna: numérico
    Descripción: Permite calcular la distancia entre los dos vectores dado los valores de sus datos
    """
    def distanciaObjetos(self, identificador, variablesObjeto, identificador2, variablesObjetoDos):
        distancia = 0
        for i in range(0, len(variablesObjeto)):
            d1 = variablesObjeto[i]
            d2 = variablesObjetoDos[i]

            distancia += math.pow((d1 - d2), 2)
        return math.sqrt(distancia)

    """
    Funcionalidad: getElemento
    Recibe: string
    Retorna: vector
    Descripción: Permite obtener el vector dado el identificador
    """
    def getElemento(self, identificador):
        for elemento in self.configuracion.getVectoresElementos():
            if str(elemento.getId()) == identificador:
                return elemento

    """
    Funcionalidad: ventanaActualizar
    Recibe: (string, numeric)
    Descripción: Permite actualizar la ventana en la que se ve el progreso de la ejecución del algoritmo
                 Recibe un string que define el mensaje a mostrar sobre la barra d eprogreso y un
                 valor numérico que establece el porciento por el cual va el análisis
    """
    def ventanaActualizar(self, msg, valor):
        self.ventana.setWindowTitle("Progreso GSCALBI - " + str(valor) + "%")
        self.ventana.children()[1].setText(msg)
        self.ventana.children()[2].setValue(valor)
        #print("[" + str(valor) + "%] " + msg)
        self.ventana.repaint()