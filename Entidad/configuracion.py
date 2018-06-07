# coding=utf-8
import os
import sys

from PyQt4 import *
from PyQt4.QtCore import *
import math

"""
Clase empleada para manejar los datos que se trabajan en toda la aplicación a medida que avanza la ejecución del algoritmo
Recibe:
    * (capaElementos:string) Valor que establece qué capa se empleará para los elementos a analizar
    * (variablesElementos:array[string]) Arreglo que contiene los atributos de la capa que se emplearán para conformar los vectores de los elementos
    * (clustersElementos:entero) Valor que establece cuántos clústeres se van a emplear en el agrupoamiento de los elementos
    * (idElementos:string) Valor que establece de los atributo de la capa de los elementos cuál será empleado para establecer el identificador de los elementos
    * (capaLocaciones:string) Valor que establece qué capa se empleará para las locaciones a tener en cuenta para la asociación
    * (variablesLocaciones:array[string]) Arreglo que contiene los atributos de la capa se emplearán para conformar los vectores de las locaciones
    * (clustersLocaciones:entero) Valor que establece cuántos clústeres se van a emplear en el agrupamiento de las locaciones
    * (idLocaciones:string) Valor que establece de los atributo de la capa de las locaciones cuál será empleado para establecer el identificador de las locaciones
    * (siPosicion:boolean) Valor que establece si se va a tener en cuenta los parámetros referentes a "Distancia Minima entre elementos y locaciones" y "Posición en el espacio entre los elementos y las locaciones"
    * (distanciaLimite:numeric) Valor que establece la distancia mínima que debe haber entre un elemento y una locacción para que esta esté asociada a él
    * (posicionEspacio:string) Valor que establece la posición relativa entre un elemento y la locación para que esta pueda estar asociada a él (norte, sur, este y oeste)
    * (siAsociacion:boolean) Valor que establece si la asociación entre elementos y locaciones se hará calculando la distancia o si esta ya se encuentra establecida previamente como parte de los datos de los elementos
    * (parametroAsociacion:string) Valor que establece qué atributo de la capa seleccionada como de los elementos guarda el dato referente a que locación está asociada a dicho elemento.
                                   El parámetro estblecido por este campo debe corresponder (en los datos) con el establecido como identificador de las locaciones
    * (sistemaCoordenadas:string) Valor que guarda el sistema de coordenadas empleado por el mapa en cuentión
    * (direccion:string) Dirección donde se almacenarán las capas e informes generados por la ejecución del algoritmo
"""
class _configuracion:
    def __init__(self, capaElementos, variablesElementos, clustersElementos, idElementos,
                 capaLocaciones, variablesLocaciones, clustersLocaciones, idLocaciones,
                 siPosicion, distanciaLimite, posicionEspacio,
                 siAsociacion, parametroAsociacion,
                 sistemaCoordenadas, direccion, metodoAgrupacion):

        self.capaElementos = capaElementos
        self.variablesElementos = variablesElementos
        self.clustersElementos = clustersElementos
        self.idElementos = idElementos
        self.vectoresElementos = []

        self.capaLocaciones = capaLocaciones
        self.variablesLocaciones = variablesLocaciones
        self.clustersLocaciones = clustersLocaciones
        self.idLocaciones = idLocaciones
        self.vectoresLocaciones = []

        self.siPosicion = siPosicion
        self.distanciaLimite = distanciaLimite
        self.posicionEspacio = posicionEspacio

        self.siAsociacion = siAsociacion
        self.parametroAsociacion = parametroAsociacion

        self.sistemaCoordenadas = sistemaCoordenadas
        self.direccion = direccion

        self.metodoAgrupacion = metodoAgrupacion
        self.matrix = None

    """
    Funcionalidad: getCapaElementos()
    Recibe: -
    Retorna: (string) Valor que establece qué capa se está empleando para los elementos a analizar
    """
    def getCapaElementos(self):
        return self.capaElementos

    """
    Funcionalidad: getVariablesElementos()
    Recibe: -
    Retorna: (array[string]) Arreglo que contiene los atributos de la capa que se emplearán para conformar los vectores de los elementos
    """
    def getVariablesElementos(self):
        return self.variablesElementos

    """
    Funcionalidad: getClustersElementos()
    Recibe: -
    Retorna: (entero) Valor que establece cuántos clústeres se van a emplear en el agrupoamiento de los elementos
    """
    def getClustersElementos(self):
        return self.clustersElementos

    """
    Funcionalidad: getIdElementos()
    Recibe: -
    Retorna: (string) Valor que establece de los atributo de la capa de los elementos cuál será empleado para establecer el identificador de los elementos
    """
    def getIdElementos(self):
        return self.idElementos

    """
    Funcionalidad: getVectoresElementos()
    Recibe: -
    Retorna: (array[_vector]) Arreglo que contiene los objetos de tipo _vector de los elementos
    """
    def getVectoresElementos(self):
        return self.vectoresElementos

    """
    Funcionalidad: setVectoresElementos()
    Recibe: (array[_vector]) Arreglo que contiene los objetos de tipo _vector de los elementos
    Retorna: -
    """
    def setVectoresElementos(self, vectoresElementos):
        self.vectoresElementos = vectoresElementos

    """
    Funcionalidad: getCapaLocaciones()
    Recibe: -
    Retorna: (string) Valor que establece qué capa se está empleando para las locaciones a tener en cuenta
    """
    def getCapaLocaciones(self):
        return self.capaLocaciones

    """
    Funcionalidad: getVariablesLocaciones()
    Recibe: -
    Retorna: (array[string]) Arreglo que contiene los atributos de la capa que se emplearán para conformar los vectores de las locaciones
    """
    def getVariablesLocaciones(self):
        return self.variablesLocaciones

    """
    Funcionalidad: getClustersLocaciones()
    Recibe: -
    Retorna: (entero) Valor que establece cuántos clústeres se van a emplear en el agrupoamiento de las locaciones
    """
    def getClustersLocaciones(self):
        return self.clustersLocaciones

    """
    Funcionalidad: getIdLocaciones()
    Recibe: -
    Retorna: (string) Valor que establece de los atributo de la capa de las locaciones cuál será empleado para establecer el identificador de las locaciones
    """
    def getIdLocaciones(self):
        return self.idLocaciones

    """
    Funcionalidad: getVectoresLocaciones()
    Recibe: -
    Retorna: (array[_vector]) Arreglo que contiene los objetos de tipo _vector de las locaciones
    """
    def getVectoresLocaciones(self):
        return self.vectoresLocaciones

    """
    Funcionalidad: setVectoresLocaciones()
    Recibe: (array[_vector]) Arreglo que contiene los objetos de tipo _vector de las locaciones
    Retorna: -
    """
    def setVectoresLocaciones(self, vectoresLocaciones):
        self.vectoresLocaciones = vectoresLocaciones

    """
    Funcionalidad: getSiPosicion()
    Recibe: -
    Retorna: (boolean) Valor que establece si se va a tener en cuenta los parámetros referentes a "Distancia Minima entre elementos y locaciones"
             y "Posición en el espacio entre los elementos y las locaciones"
    """
    def getSiPosicion(self):
        return self.siPosicion

    """
    Funcionalidad: getDistanciaLimite()
    Recibe: -
    Retorna: (numeric) Valor que establece la distancia mínima que debe haber entre un elemento y una locacción para que esta esté asociada a él
    """
    def getDistanciaLimite(self):
        return self.distanciaLimite

    """
    Funcionalidad: getPosicionEspacio()
    Recibe: -
    Retorna: (string) Valor que establece la posición relativa entre un elemento y la locación para que esta pueda estar asociada a él (norte, sur, este y oeste)
    """
    def getPosicionEspacio(self):
        return self.posicionEspacio

    """
    Funcionalidad: getSiAsociacion()
    Recibe: -
    Retorna: (boolean) Valor que establece si la asociación entre elementos y locaciones se hará calculando la distancia
             o si esta ya se encuentra establecida previamente como parte de los datos de los elementos
    """
    def getSiAsociacion(self):
        return self.siAsociacion

    """
    Funcionalidad: getParametroAsociacion()
    Recibe: -
    Retorna: (string) Valor que establece qué atributo de la capa seleccionada como de los elementos guarda el dato referente a que locación está asociada a dicho elemento.
             El parámetro estblecido por este campo debe corresponder (en los datos) con el establecido como identificador de las locaciones
    """
    def getParametroAsociacion(self):
        return self.parametroAsociacion

    """
    Funcionalidad: getSistemaCoordenadas()
    Recibe: -
    Retorna: (string) Valor que guarda el sistema de coordenadas empleado por el mapa en cuentión
    """
    def getSistemaCoordenadas(self):
        return self.sistemaCoordenadas

    """
    Funcionalidad: getDireccion()
    Recibe: -
    Retorna: (string) Dirección donde se almacenarán las capas e informes generados por la ejecución del algoritmo
    """
    def getDireccion(self):
        return self.direccion

    """
    Funcionalidad: getMetodoAgrupacion()
    Recibe: -
    Retorna: (string) Método, algoritmo empleando en el agrupamiento de los elementos y las locaciones
    """
    def getMetodoAgrupacion(self):
        return self.metodoAgrupacion

    """
    Funcionalidad: getMatrix()
    Retorno: array[array[array[array[numeric, numeric, entero]]]]
    Descripción: Permite obtener la matrix de intersección, en esta:
                    * El arreglo de 1er nivel guarda un arreglo que representa las filas de los elementos,
                      tiene una longitus igual a la cantidad de clústeres en que se dividieron los elementos.
                    * El arreglo de 2do nivel guarda un arreglo que representa las columnas de las locaciones,
                      toene una longitud igual a la cantidad de clústeres en que se dividieron las locaciones.
                    * El arreglo de 3er nivel guarda la información referente al objeto colocado en la posición
                      referenciada por los arreglos externos a él. Tiene una longitud igual a la cantidad de
                      objetos ubicados en la celda correspondiente. Cada celda hace referencia a los objetos del
                      clúster_elemento_X_clúster_locacion_y.
                    * El arreglo de 4to nivel contiene la información de cada objeto, tiene logitud 3 donde el 1er valor
                      representa el identificador del elemento, el 2do valor representa el identificador de la locación
                      asociada y el 3ro representa el clúster en que colocado dicho elemento.
                      El 3er valor de este arreglo es igual en -1 a la posición actual iterada del arreglo de 2do nivel
    """
    def getMatrix(self):
        return self.matrix

    """
    Funcionalidad: setMatrix()
    Recibe: array[array[array[array[numeric, numeric, entero]]]]. Permite modificar el valor de la matrix de interesección ya existente
    Retorno: -
    """
    def setMatrix(self, matrix):
        self.matrix = matrix