# coding=utf-8
import os
import sys
from PyQt4 import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import qgis
from qgis.core import *
from qgis.gui import *
import time

from ..Entidad.vector import _vector
from ..Entidad.configuracion import _configuracion
from asociacion import _asociacion
from weka import _weka

"""
Contiene toda la información para ejecutar el algoritmo diseñado.
Las principales funcionalidades están enfocadas a los pasos 1 y 3 del algoritmo
"""
class _algoritmo:
    def __init__(self, configuracion):
        self.configuracion = configuracion

        self.tiempoAsociacion = 0
        self.tiempoAgrupamientos = 0
        self.tiempoInterseccion = 0
        
        self.matrix = []

    """
    Funcionalidades: getTiempoAsociacion, getTiempoAgrupamientos y getTiempoInterseccion
    Descripción: Permite obtener los tiempos calculados correspondiente a cada uno de los pasos del algoritmo.
    Dichos tiempo se calculan al iniciar cada funcionalidad y al terminar se resta al tiempo actual el capturado inicialmente.
    """
    def getTiempoAsociacion(self): return self.tiempoAsociacion
    def getTiempoAgrupamientos(self): return self.tiempoAgrupamientos
    def getTiempoInterseccion(self): return self.tiempoInterseccion

    """
    Funcionalidad: ejecutar
    Descripción: Se encarga de poner en marcha la ejecución del algoritmo
                 Dentro s erealiza la asociación de los elementos y locaciones
                 y la comunicaciñon con la clase _weka para el trabajo con esta
    """
    def ejecutar(self):
        asociacion = -1
        self.vectoresElementos = []
        """ Creando los vectores de los elementos a partir de la información seleccionada en la interfaz principal """
        capa = QgsMapLayerRegistry.instance().mapLayersByName(self.configuracion.getCapaElementos())[0]
        dataVariables = []
        """ Creando el arreglo de variables a partir de las seleccionads """
        for variable in self.configuracion.getVariablesElementos() : dataVariables.append(capa.dataProvider().fieldNameIndex(variable))
        """ Recorriendo todas las features de la capa, para seleccionar de cada una de ellas los valores para conformar los vectores """
        for feature in capa.getFeatures():
            puede = True
            datosVector = []
            """ Tomando el valor correspondiente al identificador para una feature de un elemento """
            idFeature = int(feature.attributes()[capa.dataProvider().fieldNameIndex(self.configuracion.getIdElementos())])
            """ Poniendo en el arreglo de valores solo los datos correspondiente a los atributos seleccionados """
            for dataPos in dataVariables :
                dato = feature.attributes()[dataPos]
                if not dato or dato == None or dato == "NULL":
                    puede = False
                    break
                datosVector.append(dato)
            if puede:
                """ Guardando en el parámetro correspondiente a la asociación el valor de esta en caso de estar definida """
                if self.configuracion.getSiAsociacion() : asociacion = feature.attributes()[capa.dataProvider().fieldNameIndex(self.configuracion.getParametroAsociacion())]
                """ Definiendo asociacion = -1 para el caso de que algún elemento, que supuestamente debe tener un valor en dicho campo, lo tenga vacío o nulo """
                if asociacion == "NULL" or not asociacion : asociacion = -1
                """ Agregando el nuevo vector creado al arreglo de vectores correspondiente a los elementos """
                self.vectoresElementos.append(_vector(idFeature, datosVector, feature, asociacion))
        """ Agregando el arreglo completo de vectores de los elementos al parámetro correspondiente de la clase _configuracion para poder usarlo en el resto de la ejecución """
        self.configuracion.setVectoresElementos(self.vectoresElementos)
        if len(self.vectoresElementos) < self.configuracion.getClustersElementos() : return [False, u"Los datos de los elementos tienen demasiados problemas para poder realizar un análisis correcto"]

        """ Creando los vectores de las locaciones a partir de la información seleccionada en la interfaz principal """
        self.vectoresLocation = []
        capa = QgsMapLayerRegistry.instance().mapLayersByName(self.configuracion.getCapaLocaciones())[0]
        dataVariables = []
        """ Creando el arreglo de variables a partir de las seleccionads """
        for variable in self.configuracion.getVariablesLocaciones() : dataVariables.append(capa.dataProvider().fieldNameIndex(variable))
        """ Recorriendo todas las features de la capa, para seleccionar de cada una de ellas los valores para conformar los vectores """
        for feature in capa.getFeatures():
            puede = True
            datosVector = []
            """ Tomando el valor correspondiente al identificador para una feature de una locacion"""
            idLocation = int(feature.attributes()[capa.dataProvider().fieldNameIndex(self.configuracion.getIdLocaciones())])
            """ Poniendo en el arreglo de valores solo los datos correspondiente a los atributos seleccionados """
            for dataPos in dataVariables :
                dato = feature.attributes()[dataPos]
                if not dato or dato == None or dato == "NULL":
                    puede = False
                    break
                datosVector.append(dato)
            if puede:
                """ Agregando el nuevo vector creado al arreglo de vectores correspondiente a las locaciones. Debido a que ests no tienen asociación, el valor pasado en este campo es nulo """
                self.vectoresLocation.append(_vector(idLocation, datosVector, feature, NULL))
        """ Agregando el arreglo completo de vectores de los elementos al parámetro correspondiente de la clase _configuracion para poder usarlo en el resto de la ejecución """
        self.configuracion.setVectoresLocaciones(self.vectoresLocation)
        if len(self.vectoresLocation) < self.configuracion.getClustersLocaciones(): return [False, u"Los datos de las locaccciones tienen demasiados problemas para poder realizar un análisis correcto"]

        """ Si la asociación está definida se salta esta parte del programa """
        self.tiempoAsociacion = 0
        if not self.configuracion.getSiAsociacion():
            self.tiempoAsociacion = time.clock()
            self.asociacion = _asociacion(self.configuracion)
            self.asociacion.asociarElementosPorLocacion()
            self.tiempoAsociacion = time.clock() - self.tiempoAsociacion

        """ Creando una instancia de la clase _weka para la comunicación con esta biblioteca """
        self.tiempoAgrupamientos = time.clock()
        self.weka = _weka(self.configuracion)

        """
        Funcionalidad invocada: crearARFFs
        Descripción: Ver en weka.py
        Retorno: Array[boolean, None, string]
                 parámetro boolean: Establece si la funcionalidad se ha ejecutado sin problemas
                 parámetro None: campo vacío, no se usa en esa parte
                 parámetro string: Establece el mensaje de error en caso de que el 1er parámetro sea False.
        """
        salida = self.weka.crearARFFs()
        if salida[0] :
            """
            Funcionalidad: agrupar
            Descripción: Ver en weka.py
            Retorno: Array[boolean, array[string, string, array[numeric], array[numeric]], string]
                     parámetro boolean: Establece si la funcionalidad se ha ejecutado sin problemas
                     parámetro array[string]: Arreglo que almacena en las dos 1ras posiciones las salidas de Weka al agrupamiento de elementos y locaciones
                                              En las 2 posiciones siguientes se almacenan 2 arreglos con los elementos y locaciones, respectivamente
                                              con problemas en alguno de sus datos y que dicho valor ha sido sustituido por un '?'
                     parámetro string: Establece el mensaje de error en caso de que el 1er parámetro sea False.
            """
            salida = self.weka.agrupar()
        else : return [False, u"No se han podido crear los ficheros ARFF"]

        if salida[0] :
            self.salidaEle = salida[1][0]
            self.salidaLoc = salida[1][1]
            self.salidaEP = salida[1][2]
            self.salidaLP = salida[1][3]
            """
            Funcionalidad: getResultadoWeka
            Descripción: Ver en weka.py
            Retorno: Array[boolean, array[array[enteros]], string]
                     parámetro boolean: Valor True
                     parámetro array[array[enteros]]: Arreglo que guarda la información de los elementos y locaciones agrupados con Weka
                                                      Estructura completa: array[array[idE,idL-A,CE], array[idL,CL]]
                                                                            * idE: Contiene el identificador del elemento
                                                                            * idL-A: Contiene el identificador de la locación asociada al elemento
                                                                            * CE: Contiene la información del clúster en donde fue ubicado el elemento
                                                                            * idL: Contiene el identificador de la locación
                                                                            * CL: Contiene la información del clúster en donde fue ubicada la locación
                     parámetro string: Cadena vacía
            """
            salida = self.weka.getResultadoWeka()
            self.tiempoAgrupamientos = time.clock() - self.tiempoAgrupamientos
        else : return [False, u"No se han podido agrupar los elementos"]

        if salida[0] :
            self.datosC = salida[1][0]
            self.datosL = salida[1][1]
            self.tiempoInterseccion = time.clock()
            self.intersectarClusteres()
            self.tiempoInterseccion = time.clock() - self.tiempoInterseccion
            return [True, ""]
        else : return [False, u"No se han podido recuperar los datos de Wek "]

    """
    Funcionalidad: intersectarClusteres
    Descripción: Funcionalidad que se encarga de actualizar la matrix de intersección luego de ejecutado los agrupamientos con Weka
    """
    def intersectarClusteres(self):
        self.matrix = []
        """ Creando la matrix con todos los espacios definido y vacíos """
        for i in range(0,self.configuracion.getClustersElementos()):
            self.matrix.append([])
            for j in range(0,self.configuracion.getClustersLocaciones()):
                self.matrix[i].append([])
                self.matrix[i][j] = []
        """
        Recorriendo los arreglos de los agrupamientos de elementos y locacciones y colocando a cada elementos en la celda correspondiente
        *   De cada item ubicado en datosC tomar el valor del clúster en que fue ubicado este (ce)
        *   De cada item ubicado en datosC tomar el identificador de la locación asociada y
        *   buscar dicha locación en datosL y tomar el clúster en que fue ubicada esta (cla)
        *   En la poición [ce-1][cla-1] del arreglo matrix colocar dicho item
        Nota: a las posiciones ce y cla se les resta 1 porque Weka, el 1er clúster le pone valor 1, vendría a estar en la posición 0 del arreglo.
        """
        for item in self.datosC:
            ce = item[2]
            cla = 0
            for locacion in self.datosL:
                if item[1] == locacion[0]:
                    cla = locacion[1]
                    break
            self.matrix[int(ce)-1][int(cla)-1].append(item)
        """ Actualizando la matrix en la clase configuración """
        self.configuracion.setMatrix(self.matrix)

    """
    Funcionalidades: getSalidaEle, getSalidaLoc
    Retorno: string
    Descripción: Permite obtener las salidas de Weka para los elementos y las locaciones
    """
    def getSalidaEle(self) : return self.salidaEle
    def getSalidaLoc(self) : return self.salidaLoc

    """
    Funcionalidades: getSalidaEC
    Retorno: array[string]
    Descripción: Permite obtener el arreglo de elementos en cada uno de los clústeres
    """
    def getSalidaEC(self): return self.datosC

    """
    Funcionalidades: getSalidaEP, getSalidaLP
    Retorno: array[numeric]
    Descripción: Permite obtener los arreglos de elementos y locaciones en los que
                 algún dato presentó problemas y se debió sustituir con un '?'.
                 Cada elemento del arreglo representa el identificador del objeto que tuvo problemas
    """
    def getSalidaEP(self) : return self.salidaEP
    def getSalidaLP(self) : return self.salidaLP