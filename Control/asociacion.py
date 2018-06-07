# coding=utf-8
import os
import sys
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import qgis
from qgis.utils import iface
from qgis.core import *
from qgis.gui import *
import math

from ..Entidad.vector import _vector
from ..Entidad.configuracion import _configuracion

"""
Clase que contiene la información necesaria para establecer la asociación entre los elementos y las locaciones
"""
class _asociacion:
    def __init__(self, configuracion):
        self.configuracion = configuracion

    """
    Funcionalidad: asociarElementosPorLocacion
    Retorno: -
    Resultado: Vectores de los elementos con el valor de la asociacion modificado.
    """
    def asociarElementosPorLocacion(self):
        distanciaObj = QgsDistanceArea()
        distanciaObj.setEllipsoid('WGS84')
        distanciaObj.setEllipsoidalMode(True)
        """
        Para cada elementos de los vectores de las locaciones se busca la locación asociada
        """
        for elemento in self.configuracion.getVectoresElementos():
            elementoCentroId = elemento.getFeature().geometry().centroid().asPoint()
            distancia = -1
            """
            Para cada locación de los vectores de las locaciones se calcula la distancia entre esta y
            la posoción en el espacio con respecto al elemento analizado.
            """
            for locacion in self.configuracion.getVectoresLocaciones():
                locacionCentroId = locacion.getFeature().geometry().centroid().asPoint()
                calculo = distanciaObj.measureLine(elementoCentroId, locacionCentroId)
                """
                Se toma el identificador de aquella más cercana y se asigna al elemento.
                De esta manera dicha locación queda asociada al elemento en cuestión.
                """
                if (calculo < distancia or distancia == -1) and self.calcularDistanciaLimite(calculo) == True and self.calcularPosicion(elementoCentroId, locacionCentroId) == True:
                    distancia = calculo
                    elemento.setAsociacion(locacion.getId())

    """
    Funcionalidad: calcularDistanciaLimite
    Recibe: numeric
    Retorno: boolean
    Descripción: Permite conocer si la distancia pasada como parámetro, calculada entre un elemento y una locación
                 se encuentra por debajo de la distancia límite establecida para que una locación pueda ser asociada
                 a un elemento determinado.
                 Retorna true si no se ha establecido una distancia límite o si esta es mayor igual en caso de si estarlo.
    """
    def calcularDistanciaLimite(self, distancia):
        if not self.configuracion.getSiPosicion() : return True
        else:
            if distancia <= self.configuracion.getDistanciaLimite() : return True
            else : return False

    """
    Funcionalidad: calcularPosicion
    Recibe: (QgsPointXY, QgsPointXY)
    Retorno: boolean
    Descripción: Permite conocer si el punto dos se encuentra correctamente ubicado en el espacio con respecto al punto uno.
                 Para ello se tiene en cuenta el valor del parámetro recivido por la función getPosicionEspacio.
                 De no estar definida la posicion en el espacio o si ambos puntos son iguales retorna true.
                 De otra mnanera se analiza la información de las coordenas X y Y y en dependencia de las 4 posibles
                 posiciones (norte, sur, este y oeste) se calcula si pueden asociarce o no.
    """
    def calcularPosicion(self, uno, dos):
        if (uno.x() == dos.x() and uno.y() == dos.y()) or not self.configuracion.getSiPosicion() : return True
        else:
            if self.configuracion.getPosicionEspacio() == "Norte":
                if uno.y() > dos.y() and math.fabs(uno.x() - dos.x()) <= math.fabs(uno.y() - dos.y()) : return True
                else : return False
            elif self.configuracion.getPosicionEspacio() == "Sur":
                if uno.y() < dos.y() and math.fabs(uno.x() - dos.x()) <= math.fabs(uno.y() - dos.y()) : return True
                else : return False
            elif self.configuracion.getPosicionEspacio() == "Este":
                if uno.x() > dos.x() and math.fabs(uno.x() - dos.x()) >= math.fabs(uno.y() - dos.y()) : return True
                else : return False
            elif self.configuracion.getPosicionEspacio() == "Oeste":
                if uno.x() < dos.x() and math.fabs(uno.x() - dos.x()) >= math.fabs(uno.y() - dos.y()) : return True
                else : return False
            else : return True

