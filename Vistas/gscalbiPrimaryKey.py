# coding=utf-8
import os
import sys

from PyQt4 import QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import qgis
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
import unicodedata

"""
Clase interfaz que permite visualizar la ventana para asignar un nuevo campo a una determinada capa
o serializar los valores de un determinado campo. El objetivo de dicha interfaz es poder contar
con un campo que se pueda definir como identificador de los elementos o locaciones. Dicho campo debe
contener valores únicos.
"""
FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'UI//gscalbiPrimaryKey.ui'))
class _gscalbiPrimaryKey(QtGui.QDialog, FORM_CLASS):
    def __init__(self,parent=None):
        super(_gscalbiPrimaryKey, self).__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"//..//Recursos//iconpk.png"))
        self.btnAceptar.clicked.connect(self.btnAceptarClick)
        self.cmbCapa.currentIndexChanged.connect(self.CargarAtributosCapaElementos)
        self.radioButtonNC.clicked.connect(self.habilitarAccion)
        self.radioButtonSC.clicked.connect(self.habilitarAccion)
        self.habilitarAccion()

    """
    Funcionalidad: cargarCapas
    Descripción: Método para cargar las capas y actualizar el combo de lista de las capas
    """
    def cargarCapas(self):
        capas = QgsMapLayerRegistry.instance().mapLayers().items()
        if len(capas) != 0:
            layerArray = []
            for layer in capas: layerArray.append(layer[1].name())
            for i in range(0, len(layerArray)):
                for j in range(i + 1, len(layerArray)):
                    if layerArray[i] > layerArray[j]:
                        tmp = layerArray[i]
                        layerArray[i] = layerArray[j]
                        layerArray[j] = tmp
            model = QStandardItemModel()
            for texto in layerArray:
                item = QStandardItem(texto)
                model.appendRow(item)
            self.cmbCapa.setModel(model)

    """
    Funcionalidad: CargarAtributosCapaElementos
    Descripción: Método que permite actualizar el combo de lista de los atributos de la capa de los elementos
    """
    def CargarAtributosCapaElementos(self):
        try:
            capa = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbCapa.currentText())[0]
            campos = capa.dataProvider().fields()
            model = QStandardItemModel()
            for texto in campos: model.appendRow(QStandardItem(texto.name()))
            self.cmbAtributo.setModel(model)
        except:
            QMessageBox.critical(self, "Error", "Ha ocurrido un error al cargar los atributos de la capa " + self.cmbCapa.currentText())

    """
    Funcionalidad: btnAceptarClick
    Descripción: Acción a realizar cuando se da click en el botón 'Aceptar'.
                 En dependencia de la opción marcada se ejecuta uno u otro método
    """
    def btnAceptarClick(self):
        if self.radioButtonNC.isChecked(): self.btnAceptarNCClick()
        if self.radioButtonSC.isChecked(): self.btnAceptarAddValorClick()

    """
    Funcionalidad: btnAceptarAddValorClick
    Descripción: Método que permite a un campo ya existente asignarle valores desde 1 hasta 'n',
                donde 'n' es la cantidad de objetos (features) en dicha capa.
    """
    def btnAceptarAddValorClick(self):
        try:
            capa = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbCapa.currentText())[0]
            pos = capa.dataProvider().fieldNameIndex(self.cmbAtributo.currentText())
            id = 1
            capa.startEditing()
            for feature in capa.dataProvider().getFeatures():
                capa.changeAttributeValue(feature.id(), pos, id)
                id += 1
            capa.commitChanges()
        except:
            QMessageBox.critical(self, "Error", "No se ha podido crear el valor serializado para el campo " + self.cmbAtributo.currentText() + " de la capa " + self.cmbCapa.currentText())
        self.close()

    """
    Funcionalidad: btnAceptarNCClick
    Descripción: Método que permite crear un campo nuevo en la capa seleccionada y a este asignarle valores
                 desde 1 hasta 'n', donde 'n' es la cantidad de objetos (features) en dicha capa.
    """
    def btnAceptarNCClick(self):
        try:
            campo = self.txtNuevoCampo.text()
            if campo == "" or not campo or campo == None:
                QMessageBox.critical(self, "Error", "El valor del nuevo campo no puede estar en blanco")
            else:
                capa = QgsMapLayerRegistry.instance().mapLayersByName(self.cmbCapa.currentText())[0]
                capa.startEditing()
                hecho = capa.dataProvider().addAttributes([QgsField(campo, QVariant.Int)])
                if hecho:
                    capa.updateFields()
                    pos = capa.dataProvider().fieldNameIndex(campo)
                    id = 1
                    for feature in capa.dataProvider().getFeatures():
                        capa.changeAttributeValue(feature.id(), pos, id)
                        id += 1
                else : QMessageBox.critical(self, "Error", "No se ha podido crear el nuevo campo. Utilice la funcionalidad de Gesti\xf3n de Tabla de Atributos para crear el nuevo campo")
                capa.commitChanges()
                self.close()
        except:
            QMessageBox.critical(self, "Error", "Ha ocurrido un error al realizar la operaci\xf3n")

    """
    Funcionalidad: habilitarAccion
    Descripción: Método que permite habilitar, solo uno a la vez, los paneles de la vista para entrar los datos referentes
                 a si se va a crear un nuevo campo o serializar los valores de uno ya existente.
    """
    def habilitarAccion(self):
        self.wgtNC.setVisible(self.radioButtonNC.isChecked())
        self.wgtSC.setVisible(self.radioButtonSC.isChecked())