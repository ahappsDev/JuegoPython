import pygame
import random
import color_mapa
import numpy as np

VACIO = 0
MURO = 1

PORCENTAJE_MURO = 50

LADO_CELDA = 10
ANCHO_MAPA = 100
ALTO_MAPA = 100

GENERACIONES = 10

colores_mapa = {
                VACIO: color_mapa.NEGRO,
                MURO: color_mapa.MARRON,
            }


def distancia(a, b):
    """
    Distancia Manhattan entre dos posiciones
    :param a: Posicion a
    :param b: Posicion b
    :return: Distancia de manhattan
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class Nodo:

    def __init__(self, celda):
        (x, y) = celda
        self.i = x
        self.j = y
        self.F = 0
        self.G = 0
        self.H = 0
        self.estado_celda = VACIO
        self.vecinos = []
        self.nodos_vecinos = []
        self.nodo_padre = None

    def setEstado(self, estado):
        """
        Setear estado de la celda a Muro o Vacio
        :param estado: Estado al que se quiere transitar
        :return:
        """
        self.estado_celda = estado


class Mapa:
    """
    Clase mapa del juego
    """
    def __init__(self, ancho_mapa, alto_mapa, lado_celda):
        """
        Constructor que inciliza todos los parametros del mapa
        y establece los vecinos de cada celda
        :param ancho_mapa: Ancho del mapa
        :param alto_mapa: Alto del mapa
        :param lado_celda: Ancho y alto de celda
        """
        self.ancho_mapa = ancho_mapa
        self.alto_mapa = alto_mapa
        self.lado_celda = lado_celda
        self.mapa = {(x, y): Nodo((x, y))
                     for x in range(self.ancho_mapa)
                     for y in range(self.alto_mapa)}
        self.pantalla = pygame.display.set_mode(
            (self.ancho_mapa * self.lado_celda,
             self.alto_mapa * self.lado_celda))
        self.offset_vecinos = [
            (-1, 0), (1, 0),
            (0, 1), (0, -1),
            (-1, -1), (-1, 1),
            (1, 1), (1, -1)]
        for i in range(1, self.ancho_mapa-1):
            for j in range(1, self.alto_mapa-1):
                self.mapa[(i, j)].vecinos = self.vecinos((i, j))

    def heuristica(self, nodoA, nodoB):
        """
        Función heurísitca para calcular nueva distancia
        :param nodoA: Nodo origen
        :param nodoB: Nodo destino
        :return: Distancia nueva teniendo en cuenta la heuristica
        """
        dist = distancia([nodoA.i, nodoA.j], [nodoB.i, nodoB.j])
        return dist

    def generar_aleatorio(self):
        """
        Llenar aleatoriamente el mapa de juego de muros
        siguiendo un porcentaje
        :return:
        """
        for i in range(1, self.ancho_mapa-1):
            for j in range(1, self.alto_mapa-1):
                if random.randint(0, 100) < PORCENTAJE_MURO:
                    self.mapa[(i, j)].estado_celda = MURO

    def generar_automata(self):
        """
        Aplicación del autómata al mapa para redondear y llenar huecos
        :return:
        """
        for gen in range(0, GENERACIONES):
            self.crear_copia_mapa() # Se crea copia del mapa para no sobrescribir
            # Iterar por todas las celdas del mapa
            for w in range(1, self.ancho_mapa-1):
                for h in range(1, self.alto_mapa-1):
                    celda = (w, h)
                    # Conseguir los vecinos de la celda
                    vecinos = self.vecinos_aux(celda)
                    # Contar cuantos son muro de los vecinos
                    num_muros = vecinos.count(MURO)
                    # Contar cuantos son vacios de los vecinos
                    num_vacios = vecinos.count(VACIO)

                    # Si todos los vecinos son muro ponemos la celda actual a muro
                    if not num_vacios:
                        self.mapa[celda].estado_celda = MURO
                    # Si todos los vecinos son vacios ponemos la celda actual a vacia
                    elif not num_muros:
                        self.mapa[celda].estado_celda = VACIO
                    # Si hay mas vacios que muros ponemos la celda a vacio
                    elif num_vacios > num_muros:
                        self.mapa[celda].estado_celda = VACIO
                    # Si hay mas muros que vacios ponemos la celda a muro
                    elif num_vacios < num_muros:
                        self.mapa[celda].estado_celda = MURO
            self.mostrar_mapa()
            pygame.display.update()
            pygame.time.wait(100)

    def crear_copia_mapa(self):
        """
        Crear una copia del mapa para poder manejar una copia que
        no se pueda sobrescribir
        :return:
        """
        self.mapa_aux = {(x, y): self.mapa[(x, y)].estado_celda
                         for x in range(self.ancho_mapa)
                         for y in range(self.alto_mapa)}

    def __getitem__(self, celda):
        """
        Conseguir un estado de una celda
        :param celda: Celda a consultar
        :return: Estado de esa celda
        """
        return self.mapa[celda].estado_celda

    def esta_dentro(self, celda):
        """
        Comprobar si celda esta dentro del mapa
        :param celda: Celda a comprobar
        :return: Booleano de si esta dentro o no
        """
        (x, y) = celda
        return ((x >= 0) and (x < self.ancho_mapa)
                and (y >= 0) and (y < self.alto_mapa))

    def vecinos(self, celda):
        """
        Funcion que devuelve los vecinos de una celda
        :param celda: Celda de la que partimos
        :return: Lista de celdas vecinas
        """
        (x, y) = celda
        vecinos = []
        for i, j in self.offset_vecinos:
            celda_vecina = (x + i, y + j)
            if not self.esta_dentro(celda_vecina):
                continue
            vecinos.append(self.mapa[celda_vecina])
        return vecinos

    def vecinos_aux(self, celda):
        """
        Funcion que devuelve vecinos de una celda
        en el mapa de copia
        :param celda:
        :return:
        """
        (x, y) = celda
        vecinos = []
        for i, j in self.offset_vecinos:
            celda_vecina = (x + i, y + j)
            if not self.esta_dentro(celda_vecina):
                continue
            vecinos.append(self.mapa_aux[celda_vecina])
        return vecinos

    def es_vecino(self, pos1, pos2):
        """
        Comprueba si una celda es vecina de otra
        :param pos1: Primera posicion
        :param pos2: Segunda posicion
        :return:
        """
        (x1, y1) = pos1
        (x2, y2) = pos2
        esVecino = False
        for i, j in self.offset_vecinos:
            x_aux = x1 + i
            y_aux = y1 + j
            if x_aux == x2 and y_aux == y2:
                esVecino = True
                break
        return esVecino

    def buscar_camino_recto(self, origen, destino):
        """
        Busca camino recto entre dos celdas
        :param origen: Celda origen
        :param destino: Celda destino
        :return: Camino recto encontrado
        """
        camino = []
        origenIndex = origen
        destinoIndex = destino
        origen = self.mapa[origen]
        destino = self.mapa[destino]

        # Se consigue la distancia entre el origen y el destino
        distan = distancia(origenIndex, destinoIndex)
        orig = np.array([origen.i, origen.j])
        dest = np.array([destino.i, destino.j])
        # Se construye el vector director del origen al destino
        direct = dest - orig
        # Se normaliza el vector
        direct = direct / np.linalg.norm(direct)

        actual = origen
        contador = 0
        # Hasta que no se llegue al destino y el contador sea
        # menor a la distancia
        while actual != destino and contador < distan:
            # Desplazarse una unidad en dirección al destino
            x = origen.i + contador * direct[0]
            x = int(x + (0.5 if x > 0 else -0.5))
            y = origen.j + contador * direct[1]
            y = int(y + (0.5 if y > 0 else -0.5))

            coords = (x, y)
            # Se comprueba que la posicion esté dentro del mapa
            if self.esta_dentro(coords):
                actual = self.mapa[coords]
                # Se agrega nodo al camino
                camino.append(actual)
            contador += 1
        return camino

    def es_visble(self, origen, destino):
        """
        Comprueba que haya visibildiad en camino recto
        :param origen: Celda origen
        :param destino: Celda destino
        :return: Si el camino es visible o no
        """
        origenIndex = origen
        destinoIndex = destino
        origen = self.mapa[origen]
        destino = self.mapa[destino]

        # Se consigue la distancia entre el origen y el destino
        distan = distancia(origenIndex, destinoIndex)
        orig = np.array([origen.i, origen.j])
        dest = np.array([destino.i, destino.j])
        # Se construye el vector director del origen al destino
        direct = dest - orig
        # Se normaliza el vector
        direct = direct / np.linalg.norm(direct)

        actual = origen
        contador = 0
        # Hasta que no se llegue al destino y el contador sea
        # menor a la distancia
        while actual != destino and contador < distan:
            x = origen.i + contador * direct[0]
            x = int(x + (0.5 if x > 0 else -0.5))
            y = origen.j + contador * direct[1]
            y = int(y + (0.5 if y > 0 else -0.5))

            coords = (x, y)
            # Si se choca con un muro devuelve falso
            if self.mapa[(x, y)].estado_celda == MURO:
                return False
            # Se comprueba que la posicion esté dentro del mapa
            if self.esta_dentro(coords):
                actual = self.mapa[coords]
            contador += 1
        return True

    def calcular_sucesor(self, actual, vecino):
        """
        Calculo de nuevo peso teniendo en cueta el peso G calculado y
        la heuristica
        :param actual: Nodo actual
        :param vecino: Nodo vecino
        :return: Nuevo peso G
        """
        return actual.G + self.heuristica(actual, vecino)

    def buscar_camino(self, origen, destino):
        """
        Buscar camino utilizando el algoritmo A Estrella
        :param origen:
        :param destino:
        :return:
        """
        origen = self.mapa[origen]
        destino = self.mapa[destino]

        ListaCerrada = list()
        ListaAbierta = list()

        # Se inicializan los pesos
        for w in range(0, self.ancho_mapa):
            for h in range(0, self.alto_mapa):
                self.mapa[(w, h)].nodo_padre = None
                self.mapa[(w, h)].F = 0
                self.mapa[(w, h)].G = 0
                self.mapa[(w, h)].H = 0
                self.mapa[(w, h)].vecinos = []

        ListaAbierta.append(origen)

        # Mientras que la lista abierta tenga nodos
        while ListaAbierta:
            # Ordenar lista abierta segun el peso F
            ListaAbierta = sorted(ListaAbierta, key=lambda nodo: nodo.F)
            # Sacar prime elemento de lista abierta
            actual = ListaAbierta.pop(0)
            # Meter ese nodo en lista cerrada
            ListaCerrada.append(actual)
            # Si se ha llegado al destino
            if actual == destino:
                print("CAMINO ENCONTRADO")
                camino = []
                # Recorrer camino de forma inversa guardando los nodos
                while actual != origen:
                    camino.append(actual)
                    actual = actual.nodo_padre
                # Invertir camino para secuencia correcta
                return camino[::-1]
            # Se consiguen los vecinos del nodo actual
            vecinos = self.vecinos((actual.i, actual.j))
            # para cada vecino
            for vecino in vecinos:
                # Pasar al siguiente vecino si el vecino actual
                # a procesar es muro o si ya esta en lista cerrada
                if vecino.estado_celda == MURO or vecino in ListaCerrada:
                    continue
                # Si vecino esta en lista abierta
                if vecino in ListaAbierta:
                    # Se calcula nueva G
                    nuevaG = self.calcular_sucesor(actual, vecino)
                    # Se actualiza la G del vecino si es necesario
                    if vecino.G > nuevaG:
                        vecino.G = nuevaG
                        vecino.nodo_padre = actual
                else:
                    # Si no esta en lista abierta se calcula nueva G
                    vecino.G = self.calcular_sucesor(actual, vecino)
                    # Se calcula nueva H
                    vecino.H = self.calcular_sucesor(vecino, destino)
                    # Se actualiza la F del vecino
                    vecino.F = vecino.G + vecino.H
                    # Se pone al nodo actual como padre del vecino
                    vecino.nodo_padre = actual
                    # Se mete vecino en lista abierta
                    ListaAbierta.append(vecino)

        print("NO CAMINO ENCONTRADO")
        return None

    def mostrar_mapa(self):
        """
        Mostrar mapa
        :return:
        """
        for y in range(self.alto_mapa):
            for x in range(self.ancho_mapa):
                self.mostrar_celda(
                    (x, y), colores_mapa[self.mapa[(x, y)].estado_celda])

    def mostrar_celda(self, celda, color):
        """
        Mostrar cierta celda con cierto color
        :param celda: Celda a pintar
        :param color: Color de la celda
        :return:
        """
        (x, y) = celda
        pygame.draw.rect(self.pantalla, color, (y * self.lado_celda,
                                                x * self.lado_celda,
                                                self.lado_celda,
                                                self.lado_celda))

    def mostrar_celda_nodo(self, celda, color):
        """
        Utilizar un nodo para imprimir la celda
        :param celda: Celda a pintar
        :param color: Color de la celda
        :return:
        """
        (x, y) = celda.i, celda.j
        pygame.draw.rect(self.pantalla, color,
                         (y * self.lado_celda, x * self.lado_celda,
                          self.lado_celda, self.lado_celda))


if __name__ == '__main__':

    mapa = Mapa(ANCHO_MAPA, ALTO_MAPA, LADO_CELDA)

    mapa.generar_aleatorio()
    mapa.generar_automata()

    mapa.mostrar_mapa()
    pasos = mapa.buscar_camino((0, 0), (ANCHO_MAPA-1, ALTO_MAPA-1))

    camino_recorrido = []
    for paso in pasos:
        camino_recorrido.append(paso)
        mapa.mostrar_mapa()
        actual = paso
        for celda in camino_recorrido:
            if celda is not actual:
                mapa.mostrar_celda_nodo(celda, color_mapa.AZUL)
            else:
                mapa.mostrar_celda_nodo(celda, color_mapa.ROJO)
        pygame.display.update()
        pygame.time.wait(10)

    pasos = mapa.buscar_camino_recto((0, 0), (ANCHO_MAPA-1, ALTO_MAPA-1))
    camino_recorrido = []
    for paso in pasos:
        camino_recorrido.append(paso)
        mapa.mostrar_mapa()
        actual = paso
        for celda in camino_recorrido:
            if celda is not actual:
                mapa.mostrar_celda_nodo(celda, color_mapa.AZUL)
            else:
                mapa.mostrar_celda_nodo(celda, color_mapa.ROJO)
        pygame.display.update()
        pygame.time.wait(10)

    pygame.time.wait(1000)
