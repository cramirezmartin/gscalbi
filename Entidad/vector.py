# coding=utf-8
import os
import sys

from PyQt4 import *
from PyQt4.QtCore import *
import math

"""
Clase rentidad vector empleada para crear los vectores de cada uno de los objetos representados en el mapa
permite trabajar los elementos de las capas como si fueran objetos
Recibe:
    * (idem:entero) Valor que representa el identificador para cada uno de los objetos.
    * (datos:array) Arreglo de cadena de caracteres que represnetan las variables a emplear en el análisis
    * (featuire:QgsFeature) Valor que representa el objeto geométrico trabajado por el QGis para este objeto
    * (asociacion:entero) Valor que representa el identificador del objeto asociado a dicho elemento
"""
class _vector:
    def __init__(self, idem, datos, feature, asociacion):
        self.id = idem
        self.datos = datos
        self.feature = feature
        self.cluster = -1
        self.asociacion = asociacion
        self.distanciaIntraCluster = 0
        self.distanciaExtraCluster = 0
        self.distanciaIntraClusterReducido = 0
        self.distanciaExtraClusterReducido = 0

    """
    Funcionalidad: getId()
    Recibe: -
    Retorna: (numeric) Valor que representa el identificador para cada uno de los objetos.
             Dicho parámetro está establecido por el seleccionado en la interfaz principal para los elementos y las locaciones
             Corresponde con el valor del dato para el objeto para el atributo marcado
    """
    def getId(self):
        return self.id

    """
    Funcionalidad: getDatos()
    Recibe: -
    Retorna: (Arreglo) Arreglo de cadena de caracteres que represnetan las variables a emplear en el análisis
             Dicho valos está establecido por las selecciones realizadas en las listas de la interfaz principal para los elementos y las locaciones
             Corresponde con los valores del dato para el objeto en los atributos marcados
    """
    def getDatos(self):
        return self.datos

    """
    Funcionalidad: getCluster()
    Recibe: -
    Retorna: (entero) Valor que representa el cluster en el cual se ecuentra ubicado dicho elemento
    """
    def getCluster(self):
        return self.cluster

    """
    Funcionalidad: setCluster()
    Recibe: (cluster:entero) Valor que representa el cluster en el cual se ecuentra ubicado dicho elemento
    Retorna: -
    """
    def setCluster(self, cluster):
        self.cluster = cluster

    """
    Funcionalidad: getAsociacion()
    Recibe: -
    Retorna: (entero) Valor que representa el identificador del objeto asociado a dicho elemento

    Dicho valor es iniciailizado en -1 y se mantiene para el caso de los vectores que representan a las locaciones.
    Los vectores que representan a los elementos a analizar cambian este valor en el momento de realizar la asociación. Ver la
    funcionalidad "asociarElementosPorLocacion" de la clase "_asociacion"
    """
    def getAsociacion(self):
        return self.asociacion

    """
    Funcionalidad: setAsociacion()
    Recibe: (asociacion:entero) Valor que representa el identificador del objeto asociado a dicho elemento
    Retorna: -
    """
    def setAsociacion(self, asociacion):
        self.asociacion = asociacion

    """
    Funcionalidad: getFeature()
    Recibe: -
    Retorna: (QgsFeature) Valor que representa el objeto geométrico trabajado por el QGis para este objeto
    """
    def getFeature(self):
        return self.feature

    """
    Funcionalidad: getFeature()
    Recibe: (feature:QgsFeature) Valor que representa el objeto geométrico trabajado por el QGis para este objeto
    Retorna: -
    """
    def setFeature(self, feature):
        self.feature = feature

    """
    Funcionalidad: getDistanciaExtraCluster()
    Recibe: -
    Retorna: numerico. Indica la distancia media entre el elemento y los demás elementos de diferente clúster
    """
    def getDistanciaExtraCluster(self):
        return self.distanciaExtraCluster

    """
    Funcionalidad: getDistanciaIntraCluster()
    Recibe: -
    Retorna: numerico. Indica la distancia media entre el elemento y los demás elementos del mismo clúster
    """
    def getDistanciaIntraCluster(self):
        return self.distanciaIntraCluster

    """
    Funcionalidad: setDistanciaExtraCluster()
    Recibe: numerico. Indica la distancia media entre el elemento y los demás elementos de diferente clúster
    Retorna: -
    """
    def setDistanciaExtraCluster(self, distanciaExtraCluster):
        if self.distanciaExtraCluster == 0 or self.distanciaExtraCluster > distanciaExtraCluster:
            self.distanciaExtraCluster = distanciaExtraCluster

    """
    Funcionalidad: setDistanciaIntraCluster()
    Recibe: numerico. Indica la distancia media entre el elemento y los demás elementos del mismo clúster
    Retorna: -
    """
    def setDistanciaIntraCluster(self, distanciaIntraCluster):
        self.distanciaIntraCluster = distanciaIntraCluster

    """
    Funcionalidad: getIndiceSilueta()
    Recibe: -
    Retorna: numerico.

    Indica el coeficiente de la silueta, con todos los datos, para este elemento. Está dado según la fórmula (b-a)/max(a,b) donde
        * 'a' es la distancia media entre el objeto y todos los otros objetos de la misma clase
        * 'b' es la distancia media entre el objeto y todos los otros objetos del clúster más próximo
    """
    def getIndiceSilueta(self):
        max = self.distanciaExtraCluster
        if self.distanciaExtraCluster < self.distanciaIntraCluster : max = self.distanciaIntraCluster
        return (self.distanciaExtraCluster - self.distanciaIntraCluster) / max

    """
    Funcionalidad: getDistanciaExtraClusterReducido()
    Recibe: -
    Retorna: numerico. Indica la distancia media entre el elemento y los demás elementos de diferente clúster
                       En este caso el valor se establece para cuando el cálculo se ha realizado con los clústeres reducidos
    """
    def getDistanciaExtraClusterReducido(self):
        return self.distanciaExtraClusterReducido

    """
    Funcionalidad: getDistanciaIntraClusterReducido()
    Recibe: -
    Retorna: numerico. Indica la distancia media entre el elemento y los demás elementos del mismo clúster
                       En este caso el valor se establece para cuando el cálculo se ha realizado con los clústeres reducidos
    """
    def getDistanciaIntraClusterReducido(self):
        return self.distanciaIntraClusterReducido

    """
    Funcionalidad: setDistanciaExtraClusterReducido()
    Recibe: numerico. Indica la distancia media entre el elemento y los demás elementos de diferente clúster
                      En este caso el valor se establece para cuando el cálculo se ha realizado con los clústeres reducidos
    Retorna: -
    """
    def setDistanciaExtraClusterReducido(self, distanciaExtraClusterReducido):
        if self.distanciaExtraClusterReducido == 0 or self.distanciaExtraClusterReducido > distanciaExtraClusterReducido:
            self.distanciaExtraClusterReducido = distanciaExtraClusterReducido

    """
    Funcionalidad: setDistanciaIntraClusterReducido()
    Recibe: numerico. Indica la distancia media entre el elemento y los demás elementos del mismo clúster
                      En este caso el valor se establece para cuando el cálculo se ha realizado con los clústeres reducidos
    Retorna: -
    """
    def setDistanciaIntraClusterReducido(self, distanciaIntraClusterReducido):
        self.distanciaIntraClusterReducido = distanciaIntraClusterReducido

    """
    Funcionalidad: getIndiceSiluetaReducido()
    Recibe: -
    Retorna: numerico.

    Indica el coeficiente de la silueta, con los datos reducidos, para este elemento. Está dado según la fórmula (b-a)/max(a,b) donde
        * 'a' es la distancia media entre el objeto y todos los otros objetos de la misma clase
        * 'b' es la distancia media entre el objeto y todos los otros objetos del clúster más próximo
    En este caso el valor se establece para cuando el cálculo se ha realizado con los clústeres reducidos
    """
    def getIndiceSiluetaReducido(self):
            max = self.distanciaExtraClusterReducido
            if self.distanciaExtraClusterReducido < self.distanciaIntraClusterReducido : max = self.distanciaIntraClusterReducido
            return (self.distanciaExtraClusterReducido - self.distanciaIntraClusterReducido) / max
