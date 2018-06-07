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

from random import randint
from numpy import *
import shutil
import time
import datetime

from ..Entidad.vector import _vector
from ..Entidad.configuracion import _configuracion
from ..Control.algoritmo import _algoritmo
from gscalbiReporte import _gscalbiReporte
from gscalbiPrimaryKey import _gscalbiPrimaryKey

"""
Clase interfaz principal de la aplicación, contiene toda la información para construir la vista principal
capturar y validar los valores. A través de esta se puede mandar a ejecutar el algoritmo y visualizar
los resultados.
"""
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'UI//gscalbiInterfacePrincipal.ui'))
class _gscalbiInterfacePrincipal(QtGui.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        super(_gscalbiInterfacePrincipal, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"//..//Recursos//icon.png"))
        self.cmbElementosCapa.currentIndexChanged.connect(self.CargarAtributosCapaElementos)
        self.cmbLocacionesCapa.currentIndexChanged.connect(self.CargarAtributosCapaLocaciones)
        self.btnAceptar.clicked.connect(self.btnAceptarClick)
        self.btnCancelar.clicked.connect(self.close)
        self.btnDireccion.clicked.connect(self.cambiarDireccion)
        self.direccion = os.environ['HOME']+"//Desktop"
        self.txtDireccion.setText(self.direccion)
        self.gbxAsociacion.clicked.connect(self.asociacionChecked)
        self.btnNuevoCampo.clicked.connect(self.btnNuevoCampoClick)

    def inicializar(self):
        self.gbxAsociacion.setChecked(False)
        self.gbxPosicion.setChecked(False)
        self.configuracion = NULL
        self.sistemaCoordenadas = NULL
        self.txtDireccion.setDisabled(True)
        #self.btnDireccion.setDisabled(True)

    """
    Funcionalidad: cargarCapas
    Descripción: Método para cargar las capas y actualizar los combos de listas de las capas
    """
    def cargarCapas(self):
        capas = QgsMapLayerRegistry.instance().mapLayers().items()
        if len(capas) != 0:
            """
            Creando el arreglo de capas existentes y ordenandolo alfabéticamente
            """
            layerArray =[]
            for layer in capas: layerArray.append(layer[1].name())
            for i in range(0,len(layerArray)):
                for j in range(i+1,len(layerArray)):
                    if layerArray[i] > layerArray[j]:
                        tmp = layerArray[i]
                        layerArray[i] = layerArray[j]
                        layerArray[j] = tmp
            model = QStandardItemModel()
            """
            Creando los modelo para asignara a las listas y combos
            """
            for texto in layerArray:
                item = QStandardItem(texto)
                model.appendRow(item)
            self.cmbElementosCapa.setModel(model)
            self.cmbLocacionesCapa.setModel(model)
            if len(layerArray) >= 2 : self.cmbLocacionesCapa.setCurrentIndex(1)
            self.gbxElementos.setEnabled(True)
            self.gbxLocaciones.setEnabled(True)
            self.gbxPosicion.setEnabled(True)
            self.gbxDireccion.setEnabled(True)
            self.btnAceptar.setEnabled(True)
        else:
            self.gbxElementos.setEnabled(False)
            self.gbxLocaciones.setEnabled(False)
            self.gbxPosicion.setEnabled(False)
            self.gbxDireccion.setEnabled(False)
            self.btnAceptar.setEnabled(False)

    """
    Funcionalidad: CargarAtributosCapaElementos
    Descripción: Método que permite actualizar el listado de los atributos de la capa de los elementos
    """
    def CargarAtributosCapaElementos(self) :
        try:
            capa = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbElementosCapa.currentText())[0]
            campos = capa.dataProvider().fields()
            self.lblElementosVariables.setText("Variables de la capa '" + capa.name() + "'")
            model = QStandardItemModel()
            for texto in campos: model.appendRow(QStandardItem(texto.name()))
            self.lvwElementosVariables.setModel(model)
            self.cmbAsociacion.setModel(model)
            self.cmbIdElemento.setModel(model)
        except:
            QMessageBox.critical(self, "Error", "Ha ocurrido un error al cargar los atributos de la capa " + self.cmbElementosCapa.currentText())

    """
    Funcionalidad: CargarAtributosCapaLocaciones
    Descripción: Método que permite actualizar el listado de los atributos de la capa de las locaciones
    """
    def CargarAtributosCapaLocaciones(self):
        try:
            capa = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbLocacionesCapa.currentText())[0]
            campos = capa.dataProvider().fields()
            self.lblLocacionVariables.setText("Variables de la capa '" + capa.name() + "'")
            model = QStandardItemModel()
            for texto in campos: model.appendRow(QStandardItem(texto.name()))
            self.lvwLocacionesVariables.setModel(model)
            self.cmbIdLocaciones.setModel(model)
        except:
            QMessageBox.critical(self, "Error", "Ha ocurrido un error al cargar los atributos de la capa " + self.cmbLocacionesCapa.currentText())

    """
    Funcionalidad: btnAceptarClick
    Descripción: Acción a ejecutar cuando se de click en el botón Aceptar
    """
    def btnAceptarClick(self):
        self.tiempoTotal = time.clock()
        """
        Capturando los datos de los elementos
            * nombre de la capa que representa a los elementos
            * cantidad de clústeres a emplear en el análisis
            * atributo a emplear para el identificador de los elementos (debe tener valores único en los datos)
            * variables que conformarán los datos de los vectores a construir
        """
        self.elemento = self.cmbElementosCapa.currentText()
        self.clusterElementos = self.spnElementosClusteres.value()
        self.idElementos = self.cmbIdElemento.currentText()
        self.variablesElementos = []
        for items in self.lvwElementosVariables.selectedIndexes() : self.variablesElementos.append(items.model().item(items.row()).text())

        """
        Capturando los datos de las locaciones
            * nombre de la capa que representa a las locaciones
            * cantidad de clústeres a emplear en el análisis
            * atributo a emplear para el identificador de las locaciones (debe tener valores único en los datos)
            * variables que conformarán los datos de los vectores a construir
        """
        self.location = self.cmbLocacionesCapa.currentText()
        self.clusterLocaciones = self.spnLocacionesClusteres.value()
        self.idLocaciones = self.cmbIdLocaciones.currentText()
        self.variablesLocacion = []
        for items in self.lvwLocacionesVariables.selectedIndexes() : self.variablesLocacion.append(items.model().item(items.row()).text())

        """ Capturando el valor para el método de agrupación """
        self.metodoAgrupacion = self.cmbMetodoAgrupacion.currentText()

        """
        Verificando que los datos entrados estén válidos y los necesarios que no estén en blanco
        """
        self.bien = True
        self.msg = ""
        if QgsMapLayerRegistry.instance().mapLayersByName(self.elemento)[0].featureCount() < self.clusterElementos:
            self.msg += u"No hay suficientes datos en la capa "+self.elemento+u" para realizar un an\xe1lisis correcto.\n"
            self.bien = False
        if QgsMapLayerRegistry.instance().mapLayersByName(self.location)[0].featureCount() < self.clusterLocaciones:
            self.msg += u"No hay suficientes datos en la capa "+self.location+u" para realizar un an\xe1lisis correcto.\n"
            self.bien = False
        self.direccion = "C://gscalbi_" + datetime.datetime.strftime(datetime.datetime.now(),'%Y-%m-%d-%H-%M-%S')
        if self.txtDireccion.text() == "" or not self.txtDireccion.text() or self.txtDireccion.text() == None:
            self.msg += u"La direcci\xf3n de carpeta de destino est\xe1 mal conformada.\n"
            self.bien = False
        else : self.direccion = self.txtDireccion.text() + "//gscalbi_" + datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d-%H-%M-%S')
        if self.elemento == self.location:
            self.msg += u"Los elementos a analizar y las locaciones no deben ser iguales.\n"
            self.bien = False
        if len(self.variablesElementos) <= 1:
            self.msg += u"No se han seleccionado suficientes variables de 'elementos' para realizar un an\xe1lisis correcto.\n"
            self.bien = False
        if len(self.variablesLocacion) <= 1:
            self.msg += u"No se han seleccionado suficientes variables de 'locaciones' para realizar un an\xe1lisis correcto.\n"
            self.bien = False

        """ Verificando que el campo definido para el identificador de los elementos tenga valore únicos """
        capa = QgsMapLayerRegistry.instance().mapLayersByName(self.elemento)[0]
        fieldPosition = capa.dataProvider().fieldNameIndex(self.idElementos)
        arreglo = []
        noExiste = True
        for feature in capa.dataProvider().getFeatures() : arreglo.append(feature.attributes()[fieldPosition])
        pos = 1
        for i in arreglo:
            for j in range(pos, len(arreglo)):
                if i == arreglo[j] or not i or not arreglo[j]:
                    noExiste = False
                    break
            if not noExiste:
                self.msg += u"El campo especificado como 'identificador de los elementos' no posee valores \xfanicos, seleccione otro campo o cree uno nuevo.\n"
                self.bien = False
                break
            pos += 1

        """ Verificando que el campo definido para el identificador de las locaciones tenga valore únicos """
        capa = QgsMapLayerRegistry.instance().mapLayersByName(self.location)[0]
        fieldPosition = capa.dataProvider().fieldNameIndex(self.idLocaciones)
        arreglo = []
        noExiste = True
        for feature in capa.dataProvider().getFeatures(): arreglo.append(feature.attributes()[fieldPosition])
        pos = 1
        for i in arreglo:
            for j in range(pos, len(arreglo)):
                if i == arreglo[j] or not i or not arreglo[j]:
                    noExiste = False
                    break
            if not noExiste:
                self.msg += u"El campo especificado como 'identificador de las locaciones' no posee valores \xfanicos, seleccione otro campo o cree uno nuevo\n"
                self.bien = False
                break
            pos += 1

        if not self.bien : QMessageBox.warning(self, "Advertencia", self.msg)
        else:
            """
            Deshabilitando la ventana actual
            Creando la ventana del reporte
            """
            self.setModal(False)
            #self.hide()
            self.reporte = _gscalbiReporte()
            self.reporte.ventanaActualizar("Capturando datos", 0)
            """
            Creando los parámetros de configuración a emplear en todo el resto del programa
            """
            self.configuracion = _configuracion(self.elemento,self.variablesElementos, self.clusterElementos, self.idElementos,
                                                self.location, self.variablesLocacion, self.clusterLocaciones, self.idLocaciones,
                                                self.gbxPosicion.isChecked(), self.dspnDistancia.value() * 1000, self.cmbPosicion.currentText(),
                                                self.gbxAsociacion.isChecked(), self.cmbAsociacion.currentText(), self.sistemaCoordenadas, self.direccion, self.metodoAgrupacion)
            self.reporte.ventanaActualizar("Ejecutando el algoritmo", 5)

            """
            Creando una instancia de la clas algoritmo
            Inicializando los valores necesarios para la ejecución del mismo
            Invocando a la funcionalidad "ejecutar" para poner en marcha el algoritmo
            """
            self.algoritmoGscalbi = _algoritmo(self.configuracion)
            hecho = self.algoritmoGscalbi.ejecutar()
            if not hecho[0]:
                self.reporte.ventana.close()
                self.setModal(True)
                self.show()
                QMessageBox.warning(self, "Advertencia", hecho[1])
            else:
                self.reporte.ventanaActualizar("Capturando respuesta", 15)
                """
                Capturando la matrix de intersección, esta contiene los datos generados por el algoritmo
                Cada elemento de la matrix es un arreglo de valores que representan el identificador del elementos,
                el identificador de la locación asociada y el clúster en que fue ubicado.
                Ver en algoritmo.py el método asociado para la descripción más detallada de la información que maneja
                """
                self.matrix = self.configuracion.getMatrix()

                """
                Capturando las salidas de Weka producto de la ejecución del algoritmo SimpleKMeans para los elementos y las locaciones
                Ver en algoritmo.py los métodos asociados para la descripción de la información que manejan
                """
                self.salidasWeka = [self.algoritmoGscalbi.getSalidaEle(), self.algoritmoGscalbi.getSalidaLoc(), self.algoritmoGscalbi.getSalidaEP(), self.algoritmoGscalbi.getSalidaLP()]

                """
                Capturando los tiempos calculados correspondiente a cada uno de los pasoso del algoritmo
                Ver en algoritmo.py los métodos asociados para la descripción de la información que manejan
                """
                self.tiempos = [self.algoritmoGscalbi.getTiempoAsociacion(), self.algoritmoGscalbi.getTiempoAgrupamientos(),self.algoritmoGscalbi.getTiempoInterseccion()]

                """
                Invocando a la funcionalidad de visualizarResultados() para mostrar las salidas del algoritmo
                Terminando la ejecución de la aplicación
                """
                self.visualizarResultados()
                self.tiempoTotal = time.clock() - self.tiempoTotal
                #self.close()
                QMessageBox.information(self, "GSCALBI terminado", "Tiempo total: "+str(round(self.tiempoTotal,2))+"s")

    """
    Funcionalidad: visualizarResultados
    Descirpción: Permite crear los elementos del reporte, necesarios para mostrar los resultados de la ejecución del algoritmo
                 Construye el HTML a mostrar y exportar a HTML y PDF
                 Construye el árbol de capas por cada clúster de la matrix de intersección
    """
    def visualizarResultados (self):
        self.reporte.ventanaActualizar("Construyendo reporte", 20)
        self.reporte.construirHTML(self.configuracion, self.matrix, self.salidasWeka, self.tiempos)
        self.reporte.indiceSilueta()
        self.reporte.construirCapas()
        self.reporte.mostrarResultados()

    """
    Funcionalidad: asociacionChecked
    Descirpción: Permite habilitar/deshabilitar el área correspondiente a "Posición en el espacio" si la asociación
                 ya se se encuentra definida como parte de los datos de la capa correspondiente a los elementos
    """
    def asociacionChecked(self):
        self.gbxPosicion.setChecked(False)
        self.gbxPosicion.setEnabled(not self.gbxAsociacion.isChecked())

    """
    Funcionalidad: btnNuevoCampoClick
    Descirpción: Permite construir la interfaz para asignar un nuevo campo a la capa
                 o asignar valores serializados a un campo ya existente.
                 Esta funcionalidad es necesaria en el caso de que no se cuente con un campo del cual escoger los valores
                 para conformar los identificadores de los elementos y las locaciones
    """
    def btnNuevoCampoClick(self):
        self.dlgPk = _gscalbiPrimaryKey()
        self.dlgPk.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.dlgPk.btnAceptar.clicked.connect(self.actualizarCapas)
        self.dlgPk.cargarCapas()
        self.dlgPk.exec_()

    """
    Funcionalidad: actualizarCapas
    Descirpción: Permite actualizar los atributos mostrados para cada capa
    """
    def actualizarCapas(self):
        self.CargarAtributosCapaElementos()
        self.CargarAtributosCapaLocaciones()

    """
    Funcionalidad: cambiarDireccion
    Descirpción: Permite modificar la dirección en la que se guardarán los elmentos de la ejecución del algoritmo
                 En dicha dirección se guardarán los ficheros ARFF, capas ShapeFile de los mapas de los agrupamientos y los reportes en los diferentes formatos
    """
    def cambiarDireccion(self):
        dir = QFileDialog.getExistingDirectory()
        if dir: self.txtDireccion.setText(dir)