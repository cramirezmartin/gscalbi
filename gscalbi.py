__author__ = 'CERM'

import os
from PyQt4 import  QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import resources
from Vistas.gscalbiInterfacePrincipal import _gscalbiInterfacePrincipal
from Vistas.gscalbiPrimaryKey import _gscalbiPrimaryKey

class _gscalbi:
    def __init__(self, iface):
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(self.plugin_dir, 'i18n', 'gscalbi_{}.qm'.format(locale))
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            if qVersion() > '4.3.3' : QCoreApplication.installTranslator(self.translator)
        self.dlg = _gscalbiInterfacePrincipal()
        self.dlg.btnAbout.clicked.connect(self.btnAboutClick)
        self.dlg.setWindowFlags(QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.actions = []
        self.menu = self.tr(u'&GSCALBI')
        self.toolbar = self.iface.pluginToolBar()

    def tr(self, message) : return QCoreApplication.translate('gscalbi', message)

    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)
        if status_tip is not None : action.setStatusTip(status_tip)
        if whats_this is not None : action.setWhatsThis(whats_this)
        if add_to_toolbar : self.toolbar.addAction(action)
        if add_to_menu : self.iface.addPluginToMenu(self.menu, action)
        self.actions.append(action)

        return action

    def initGui(self):
        self.add_action(
            ':/plugins/gscalbi/Recursos/icon.png',
            text=self.tr(u'&GeoSpatial Clustering Around Location Based on Intersection'),
            callback=self.run,
            parent=self.iface.mainWindow())

    def unload(self):
        for action in self.actions:
            self.iface.removePluginMenu(self.tr(u'&GSCALBI'), action)
            self.iface.removeToolBarIcon(action)
        del self.toolbar
        self.dlg.close()

    def run(self):
        self.dlg.inicializar()
        self.dlg.cargarCapas()
        self.dlg.show()

    def btnAboutClick(self):
        self.about = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.about.resize(600, 320)
        self.about.setMaximumSize(600, 320)
        self.about.setMinimumSize(600, 320)
        self.about.setWindowTitle("Acerca de GSCALBI v1.0")
        self.about.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.about.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__)+"//Recursos//iconabout.png"))
        self.about.setStyleSheet("QTextBrowser, QTextBrowser:hover, QTextBrowser:link {border: 0px solid #FFFFFF;background-color: rgb(255, 255, 255);}")
        self.about.setModal(True)

        cuerpo = QtGui.QTextBrowser(self.about)
        cuerpo.resize(600, 320)
        cuerpo.setMaximumSize(600, 320)
        cuerpo.setMinimumSize(600, 320)
        archivo = open(os.path.dirname(__file__)+"//Recursos//about.html", "r")
        cuerpo.setHtml(archivo.read())

        boton = QtGui.QPushButton(self.about)
        boton.resize(50, 23)
        boton.move(540, 290)
        boton.setText("Cerrar")
        boton.clicked.connect(self.about.close)

        botonLicence = QtGui.QPushButton(self.about)
        botonLicence.resize(50, 23)
        botonLicence.move(480, 290)
        botonLicence.setText("Licencia")
        botonLicence.clicked.connect(self.btnLicenceClick)

        self.about.show()

    def btnLicenceClick(self):
        self.licence = QtGui.QDialog(None, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowTitleHint)
        self.licence.resize(450, 400)
        self.licence.setMaximumSize(450, 400)
        self.licence.setMinimumSize(450, 400)
        self.licence.setWindowTitle("Licencia")
        self.licence.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.licence.setWindowIcon(QtGui.QIcon(os.path.dirname(__file__) + "//Recursos//iconabout.png"))
        self.licence.setStyleSheet("QTextEdit, QTextEdit:hover, QTextEdit:link {border: 0px solid #FFFFFF;background-color: rgb(255, 255, 255);}")
        self.licence.setModal(True)

        texto = QtGui.QTextEdit(self.licence)
        texto.resize(450, 400)
        texto.setMaximumSize(450, 400)
        texto.setMinimumSize(450, 400)
        texto.setReadOnly(True)

        archivo = open(os.path.dirname(__file__) + "//LICENSE.txt", "r")
        archivo = archivo.read()
        texto.insertPlainText(archivo)
        texto.moveCursor(QTextCursor.Start)

        boton = QtGui.QPushButton(self.licence)
        boton.resize(50, 23)
        boton.move(380, 370)
        boton.setText("Cerrar")
        boton.clicked.connect(self.licence.close)
        self.licence.show()