# coding=utf-8
import os
import sys
from PyQt4 import  QtCore, QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import time
import platform
from ..Entidad.vector import _vector
from ..Entidad.configuracion import _configuracion
from random import randint
import codecs

"""
Clase que contiene toda la información para el trabajo con la biblioteca Weka.
Encargada de crear los ficheros ARFF con la información seleccionada y, haciendo uso líneas de comando, ejecutar
el algoritmo SimpleKMeans de Weka.
Encargada de parsear los ficheros generados con Weka producto del agrupamiento y retornar los arreglos correspondientes
de elementos y locaciones con el valor del clúster definido para  cada objeto.
"""
class _weka:
    def __init__(self, configuracion):
        self.weka = os.path.dirname(__file__)+'//..//Recursos//weka.jar'
        
        self.configuracion = configuracion
        
        self.vectoresElementos = self.configuracion.getVectoresElementos()
        self.variablesElementos = self.configuracion.getVariablesElementos()
        self.clusterElementos = self.configuracion.getClustersElementos()
        
        self.vectoresLocation = self.configuracion.getVectoresLocaciones()
        self.variablesLocacion = self.configuracion.getVariablesLocaciones()
        self.clusterLocaciones = self.configuracion.getClustersLocaciones()
        
        self.direccionSalida = self.configuracion.getDireccion()
        
        self.salida = [None, None, None, None]
        self.ep = []
        self.lp = []

    """
    Funcionalidad: crearARFFs
    Descripción: Esta funcionalidad se encarga de crear los ficheros "gscalbiElementos.arff" y "gscalbiLocaciones.arff".
                 Dichos ficheros serán usado posteriormente para realizar el agrupamiento.
    Retorno: array[boolean, None, string]
    """
    def crearARFFs(self):
        """ Eliminando los ficheros que puedan estar ya existentes en la dirección seleccionada """
        if not os.path.exists(self.direccionSalida) : os.makedirs(self.direccionSalida)
        if os.path.exists(self.direccionSalida+"//gscalbiElementos.arff") : os.remove(self.direccionSalida+"//gscalbiElementos.arff")
        if os.path.exists(self.direccionSalida+"//gscalbiLocaciones.arff") : os.remove(self.direccionSalida+"//gscalbiLocaciones.arff")

        """ Creando el fichero gscalbiElementos.arff """
        archivo = open(self.direccionSalida+"//gscalbiElementos.arff", "w")
        archivo.write("@relation gscalbiElementos\n")            
        archivo.write("@attribute id real\n")
        for elementos in self.variablesElementos : archivo.write("@attribute "+elementos+" real\n")
        archivo.write("@attribute id_locacion real\n")
        archivo.write("@data")
        hecho = False
        """
        Recorriendo el arreglo de vectores de los elementos tomando solo aquellos con una asociación
        ya establecida por la clase _asociacion o asignada (diferente de -1) directamente por el usuario
        """
        for items in self.vectoresElementos:
            if items.getAsociacion() != -1:
                archivo.write("\n")
                archivo.write(str(items.getId()))
                """
                Recorriendo el arreglo de datos para cada uno de los elementos
                Creando la cadena de datos a escribir en el fichero ARFF sustituyendo aquellos valores nulos por un '?'
                """
                datosElementos = items.getDatos()
                for data in datosElementos:
                    dato = str(data)
                    if not data or data==None or data=="" or (type(data) != float and type(data) != int and type(data) != long):
                        dato = '?'
                        self.ep.append(items.getId())
                    archivo.write(","+dato)
                """ Escribiendo la cadena del vector elemento en el fichero ARFF """
                archivo.write(","+str(items.getAsociacion()))
                hecho = True
        archivo.close()

        """
        Si ningún elemento ha podido ser añadido al fichero se retorna un arreglo de estructura [boolean, None, string]
        donde el 1er parámetro define si la operación se realizó o no (en este caso False), el 2do
        no se usa en este momento y el 3ro define el mensaje del error ocacionado (en este caso que ningún
        elemento posee asociaciones dado los parámetros seleccionados por el usuario).
        """
        if not hecho : return [False, None, "Ning\xfan elemento posee asociaci\xf3n dado estos par\xe1metros"]
        else :
            """ Creando el fichero gscalbiLocaciones.arff """
            archivo = open(self.direccionSalida+"//gscalbiLocaciones.arff", "w")
            archivo.write("@relation gscalbiLocaciones\n")            
            archivo.write("@attribute id real\n")
            for local in self.variablesLocacion : archivo.write("@attribute "+local+" real\n")
            archivo.write("@data")
            """ Recorriendo el arreglo de vectores de las locaciones tomando cada uno de los elementos """
            for items in self.vectoresLocation:
                archivo.write("\n")
                archivo.write(str(items.getId()))
                """
                Recorriendo el arreglo de datos para cada uno de las locaciones
                Creando la cadena de datos a escribir en el fichero ARFF sustituyendo aquellos valores nulos por un '?'
                """
                for data in items.getDatos():
                    dato = str(data)
                    if not data or data==None or data=="" or (type(data) != float and type(data) != int and type(data) != long):
                        dato = '?'
                        self.lp.append(items.getId())
                    """ Escribiendo la cadena del vector elemento en el fichero ARFF """
                    archivo.write(","+dato)
            archivo.close()
            """ Se retorna un arreglo de estructura [boolean, None, string] donde solo el 1er valor importa y debe ser True """
            return [True, None, ""]

    """
    Funcionalidad: agrupar
    Descripción: Funcionalidad que se encarga de realizar el agrupamiento de los elementos y las locaciones.
                 Para ello hace uso de la biblioteca Weka a través de líneas de comandos.
                 Para lograr que en cada iteracción sobre los mismos datos se obtenga un resultado distinto (requisito de minería de datos)
                 se crea un 2do fichero para los ARFF de los elementos y las locaciones, dichos ficheros son denominados
                 'gscalbiElementosTrain.arff' y 'gscalbiLocacionesTrain.arff' y contienen los mismos datos que los ficheros originales pero
                 organizados de manera aleatoria.
    Retorno: Array[boolean, array[string, string, array[numeric], array[numeric]], string]
                     parámetro boolean: Establece si la funcionalidad se ha ejecutado sin problemas
                     parámetro array[string]: Arreglo que almacena en las dos 1ras posiciones las salidas de Weka al agrupamiento de elementos y locaciones
                                              En las 2 posiciones siguientes se almacenan 2 arreglos con los elementos y locaciones, respectivamente
                                              con problemas en alguno de sus datos y que dicho valor ha sido sustituido por un '?'
                     parámetro string: Establece el mensaje de error en caso de que el 1er parámetro sea False.
    """
    def agrupar(self):
        """ Eliminando los posibles ficheros ya existente en la dirección especificada """
        if os.path.exists(self.direccionSalida+"//gscalbiElementosClusterizado.arff") : os.remove(self.direccionSalida+"//gscalbiElementosClusterizado.arff")
        if os.path.exists(self.direccionSalida+"//gscalbiLocacionesClusterizado.arff") : os.remove(self.direccionSalida+"//gscalbiLocacionesClusterizado.arff")
        if os.path.exists(self.direccionSalida+"//comandos.bat") : os.remove(self.direccionSalida+"//comandos.bat")
        if os.path.exists(self.direccionSalida+"//comandos.sh") : os.remove(self.direccionSalida+"//comandos.sh")

        """
        Creando el fichero comandos.(bat|sh) para poder realizar el agrupamiento de manera externa a la aplicación
        A través de este, si no fue posible con la aplicación, se puede obtener los ficheros con el resultados de los agrupamientos
        """
        ext = ""
        if platform.system() == "Windows" : ext = ".bat"
        elif platform.system() == "Linux" or platform.system() == "Unix" : ext = ".sh"
        comandosFile = open(self.direccionSalida+"//comandos"+ext, "w")
        hecho = True

        """
        Creando los comando, para ejecutar el agrupamiento con Weka, y guardándolo en el fichero de comandos.(bat|sh)
        Ficheros 'gscalbiElementosClusterizado.arff' y 'gscalbiLocacionesClusterizado.arff' creados a partir de los
        ficheros 'gscalbiElementosTrain.arff' y 'gscalbiLocacionesTrain.arff' producto del algoritmo SimpleKMeans de Weka
        """
        comando = ""
        se = str(randint(0, len(self.configuracion.getVectoresElementos())))
        sl = str(randint(0, len(self.configuracion.getVectoresLocaciones())))
        print len(self.configuracion.getVectoresElementos())
        print se + "-" + sl
        if self.configuracion.getMetodoAgrupacion() == "SimpleKMeans":
            comando = 'java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.SimpleKMeans -N ' + str(self.clusterElementos) + ' -A \\"weka.core.EuclideanDistance -R 2-' + str(len(self.variablesElementos) + 1) + '\\" -I 100 -O -S ' + se + '" -i "' + self.direccionSalida + '//gscalbiElementos.arff" -o "' + self.direccionSalida + '//gscalbiElementosClusterizado.arff"'
            comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.SimpleKMeans -N ' + str(self.clusterLocaciones) + ' -A \\"weka.core.EuclideanDistance -R 2-' + str(len(self.variablesLocacion) + 1) + '\\" -I 100 -O -S ' + sl + '" -i "' + self.direccionSalida + '//gscalbiLocaciones.arff" -o "' + self.direccionSalida + '//gscalbiLocacionesClusterizado.arff"'
        if self.configuracion.getMetodoAgrupacion() == "HierarchicalClusterer":
            comando = 'java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.HierarchicalClusterer -N ' + str(self.clusterElementos) + ' -L COMPLETE -P -A \\"weka.core.EuclideanDistance -R 2-' + str(len(self.variablesElementos) + 1) + '\\"" -i "' + self.direccionSalida + '//gscalbiElementos.arff" -o "' + self.direccionSalida + '//gscalbiElementosClusterizado.arff"'
            comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.HierarchicalClusterer -N ' + str(self.clusterLocaciones) + ' -L COMPLETE -P -A \\"weka.core.EuclideanDistance -R 2-' + str(len(self.variablesLocacion) + 1) + '\\"" -i "' + self.direccionSalida + '//gscalbiLocaciones.arff" -o "' + self.direccionSalida + '//gscalbiLocacionesClusterizado.arff"'
        if self.configuracion.getMetodoAgrupacion() == "EM":
            comando = 'java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.EM -I 100 -S ' + se + ' -N ' + str(self.clusterElementos) + '" -I 1,' + str(len(self.variablesElementos) + 2) + ' -i "' + self.direccionSalida + '//gscalbiElementos.arff" -o "' + self.direccionSalida + '//gscalbiElementosClusterizado.arff"'
            comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.AddCluster -W "weka.clusterers.EM -I 100 -S ' + sl + ' -N ' + str(self.clusterLocaciones) + '" -I 1 -i "' + self.direccionSalida + '//gscalbiLocaciones.arff" -o "' + self.direccionSalida + '//gscalbiLocacionesClusterizado.arff"'

        """ Copiando los comando para el fichero """
        comandosFile.write(comando+"\n")
        """ Ejecutando el comando. Obteniendo los ficheros del agrupamiento """
        os.system(comando)
        if not os.path.exists(self.direccionSalida+"//gscalbiElementosClusterizado.arff") or not os.path.exists(self.direccionSalida+"//gscalbiLocacionesClusterizado.arff") : hecho = False

        """ Creando los ficheros ARFF, de los atributos eliminados, para la salida de los algoritmos de agrupamiento """
        comando = 'java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.Remove -R 1,' + str(len(self.variablesElementos) + 2) + ' -i "' + self.direccionSalida + '//gscalbiElementos.arff" -o "' + self.direccionSalida + '//gscalbiElementosAtrRemove.arff"'
        comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.filters.unsupervised.attribute.Remove -R 1 -i "' + self.direccionSalida + '//gscalbiLocaciones.arff" -o "' + self.direccionSalida + '//gscalbiLocacionesAtrRemove.arff"'
        comandosFile.write(comando + "\n")
        os.system(comando)

        """
        Repitiendo el algoritmo para obtener el resumen de salida de la ejecución del algoritmo.
        Necesario debido a que en el paso anterior no se obtiene dicho resumen del análisis realizado,
        solo se crean los ficheros ARFF correespondientes con los datos finales.
        En este paso se obtiene solo el resumen de salida de la ejecución del algoritmo y se guarda en un fichero de texto
        Se crean 2 comandos, uno para obtener el resumen de salida del agrupamiento de los elementos y otro para las locaciones.
        """
        if self.configuracion.getMetodoAgrupacion() == "SimpleKMeans":
            comando = 'java -Xmx1G -cp "'+self.weka+'" weka.clusterers.SimpleKMeans -N '+str(self.clusterElementos)+' -A "weka.core.EuclideanDistance" -I 100 -O -S ' + se + ' -t "'+self.direccionSalida+'//gscalbiElementosAtrRemove.arff" > "'+self.direccionSalida+'//gscalbiElementosClusterizado.txt"'
            comando += ' | java -Xmx1G -cp "'+self.weka+'" weka.clusterers.SimpleKMeans -N '+str(self.clusterLocaciones)+' -A "weka.core.EuclideanDistance" -I 100 -O -S ' + sl + ' -t "'+self.direccionSalida+'//gscalbiLocacionesAtrRemove.arff" > "'+self.direccionSalida+'//gscalbiLocacionesClusterizado.txt"'
        if self.configuracion.getMetodoAgrupacion() == "HierarchicalClusterer":
            comando = 'java -Xmx1G -cp "' + self.weka + '" weka.clusterers.HierarchicalClusterer -N '+str(self.clusterElementos)+' -L COMPLETE -P -A "weka.core.EuclideanDistance" -t "' + self.direccionSalida + '//gscalbiElementosAtrRemove.arff" > "' + self.direccionSalida + '//gscalbiElementosClusterizado.txt"'
            comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.clusterers.HierarchicalClusterer -N '+str(self.clusterLocaciones)+' -L COMPLETE -P -A "weka.core.EuclideanDistance" -t "' + self.direccionSalida + '//gscalbiLocacionesAtrRemove.arff" > "' + self.direccionSalida + '//gscalbiLocacionesClusterizado.txt"'
        if self.configuracion.getMetodoAgrupacion() == "EM":
            comando = 'java -Xmx1G -cp "' + self.weka + '" weka.clusterers.EM -I 100 -S ' + se + ' -N '+str(self.clusterElementos)+' -t "' + self.direccionSalida + '//gscalbiElementosAtrRemove.arff" > "' + self.direccionSalida + '//gscalbiElementosClusterizado.txt"'
            comando += ' | java -Xmx1G -cp "' + self.weka + '" weka.clusterers.EM -I 100 -S ' + sl + ' -N '+str(self.clusterLocaciones)+' -t "' + self.direccionSalida + '//gscalbiLocacionesAtrRemove.arff" > "' + self.direccionSalida + '//gscalbiLocacionesClusterizado.txt"'

        """ Copiando los comando para el fichero """
        comandosFile.write(comando+"\n")
        """ Ejecutando el comando. Obteniendo las salidas del agrupamiento """
        os.system(comando)

        """ Eliminando los ficheros creados, randomizados y de los atributos eliminados, para la salida de los algoritmos de agrupamiento """
        if os.path.exists(self.direccionSalida + "//gscalbiElementosAtrRemove.arff"): os.remove(self.direccionSalida + "//gscalbiElementosAtrRemove.arff")
        if os.path.exists(self.direccionSalida + "//gscalbiLocacionesAtrRemove.arff"): os.remove(self.direccionSalida + "//gscalbiLocacionesAtrRemove.arff")

        """ Leyendo el resumen de salida de ejecución del algoritmo en los ficherso de texto correspondientes """
        if os.path.exists(self.direccionSalida+"//gscalbiElementosClusterizado.txt") and os.path.exists(self.direccionSalida+"//gscalbiLocacionesClusterizado.txt") :
            archivoSalida = open(self.direccionSalida+"//gscalbiElementosClusterizado.txt", "r")
            self.salida[0] = archivoSalida.read()
            archivoSalida.close()
            archivoSalida = open(self.direccionSalida+"//gscalbiLocacionesClusterizado.txt", "r")
            self.salida[1] = archivoSalida.read()
            archivoSalida.close()

        """ Eliminando del arreglo de elementos con problemas los datos duplicados y ordenando el arreglo """
        elementosProblemas = []
        for item in self.ep:
            esta = False
            for objeto in elementosProblemas:
                if item == objeto:
                    esta = True
                    break
            if not esta: elementosProblemas.append(item)
        elementosProblemas.sort()

        """ Eliminando del arreglo de locaciones con problemas los datos duplicados y ordenando el arreglo """
        locacionesProblemas = []
        for item in self.lp:
            esta = False
            for objeto in locacionesProblemas:
                if item == objeto:
                    esta = True
                    break
            if not esta: locacionesProblemas.append(item)
        locacionesProblemas.sort()

        self.salida[2] = elementosProblemas
        self.salida[3] = locacionesProblemas
        
        comandosFile.close()

        """
        En caso que los ficheros no se puedan crear por la propia aplicación se informa al usuario para que este los cree
        manualmente a tavés de la ejecución del fichero comandos.(bat|sh). El programa se mantiene en espera hasta que existan
        los ficheros 'gscalbiElementosClusterizado.arff' y 'gscalbiLocacionesClusterizado.arff' o se cancele el mismo.
        """
        self.msg = "No se han podido crear los ficheros ARFF mediante la ejecuci\xf3n de comandos\nEjecute manualmente el fichero 'comandos' ubicado en:\n" + str(self.direccionSalida)
        while not hecho:
            reply = QMessageBox.question(None, 'Advertencia', self.msg, QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
            if reply == QtGui.QMessageBox.Yes:
                if os.path.exists(self.direccionSalida+"//gscalbiElementosClusterizado.arff") and os.path.exists(self.direccionSalida+"//gscalbiLocacionesClusterizado.arff") and os.path.exists(self.direccionSalida+"//gscalbiElementosClusterizado.txt") and os.path.exists(self.direccionSalida+"//gscalbiLocacionesClusterizado.txt"):
                    archivoSalida = open(self.direccionSalida+"//gscalbiElementosClusterizado.txt", "r")
                    self.salida[0] = archivoSalida.read()
                    archivoSalida = open(self.direccionSalida+"//gscalbiLocacionesClusterizado.txt", "r")
                    self.salida[1] = archivoSalida.read()
                    archivoSalida.close()
                    hecho = True
            else : return [False, None, "Se ha cancelado la aplicaci\xf3n"]
        
        return [True, self.salida, ""]

    """
    Funcionalidad: getResultadoWeka
    Descripción: Se encarga de tomar los datos de los ficheros 'gscalbiElementosClusterizado.arff' y 'gscalbiLocacionesClusterizado.arff'
                 y parsearlos para construir los arreglos de salida de los elementos y locaciones con el valor del clúster al que fue
                 asignado cada uno de ellos.
                 De cada fichero se toma cada línea (correspondiente a cada elemento/locacion) a partir de la posición de '@data',
                 se parsea esta y cada dato se coloca en el arreglo en el orden correspondiente.
    Retorno: Array[boolean, array[array[enteros]], string]
                     parámetro boolean: Valor True
                     parámetro array[array[enteros]]: Arreglo que guarda la información de los elementos y locaciones agrupados con Weka
                                                      Estructura básica: array[datosC, datosL]
                                                      Estructura completa: array[array[idE,idL-A,CE], array[idL,CL]]
                                                                            * idE: Contiene el identificador del elemento
                                                                            * idL-A: Contiene el identificador de la locación asociada al elemento
                                                                            * CE: Contiene la información del clúster en donde fue ubicado el elemento
                                                                            * idL: Contiene el identificador de la locación
                                                                            * CL: Contiene la información del clúster en donde fue ubicada la locación
                     parámetro string: Cadena vacía
    """
    def getResultadoWeka(self):
        """ Parseando los datos de los elementos """
        archivo = open(self.direccionSalida+"//gscalbiElementosClusterizado.arff", "r")
        adata = archivo.readline()
        while adata != "@data\n" : adata = archivo.readline()
        linea = archivo.readline()
        datosC = []
        while linea:
            linea = archivo.readline()
            if linea:
                tmp = linea.split(",")
                idE = tmp[0]
                idL = tmp[len(tmp)-2]
                c = tmp[len(tmp)-1][7]
                datosC.append([idE,idL,c])
        archivo.close()

        """ Parseando los datos de las locaciones """
        archivo = open(self.direccionSalida+"//gscalbiLocacionesClusterizado.arff", "r")
        adata = archivo.readline()
        while adata != "@data\n" : adata = archivo.readline()
        linea = archivo.readline()
        datosL = []
        while linea:
            linea = archivo.readline()
            if linea:
                tmp = linea.split(",")
                idL = tmp[0]
                c = tmp[len(tmp)-1][7]
                datosL.append([idL,c])
        archivo.close()

        """ Asignando a cada vector su clúster correspondiente """
        for elemento in datosC:
            for vector in self.vectoresElementos:
                if str(vector.getId()) == elemento[0]:
                    vector.setCluster(int(elemento[2]) - 1)
                    break

        for locacion in datosL:
            for vector in self.vectoresLocation:
                if str(vector.getId()) == locacion[0]:
                    vector.setCluster(int(locacion[1]) - 1)
                    break

        return [True, [datosC, datosL], ""]