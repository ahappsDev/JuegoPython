import pygame
import sys
import random
import color_mapa
import numpy as np
from pygame.locals import *
from mapa import Mapa, distancia, VACIO
from enum import Enum

LADO_CELDA = 10
ANCHO_MAPA = 70
ALTO_MAPA = 70

class Estado(Enum):
    PATRULLAR = 1
    BUSCAR = 2
    RASTREAR = 3
    LUCHA = 4
    HUIR = 5
    MUERTO = 6


class Monstruo():
    def __init__(self, posicion):
        self.posicion = posicion
        self.estado = Estado.PATRULLAR
        self.lentitud = 2
        self.vida = 12
        self.armadura = 2
        self.turno = 0
        self.fuerza = 4

        self.switcher = {
            Estado.PATRULLAR: self.patrullar,
            Estado.BUSCAR: self.buscar,
            Estado.RASTREAR: self.rastrear,
            Estado.HUIR: self.huir,
            Estado.LUCHA: self.luchar,
            Estado.MUERTO: self.morir
        }
        self.distancia_visto = None
        self.distancia_olido = None
        self.max_dist_olfato = 10
        self.max_dist_vista = 12

    def morir(self):
        pass

    def oler(self):
        """
        Comprobar si la distancia entre el jugador y mosntruo 
        es menor a la distancia de olfato
        :return: Booleano si huele al jugador
        """
        pos1 = self.posicion
        pos2 = jugador.posicion
        return distancia(pos1, pos2) <= self.max_dist_olfato

    def ver(self):
        """
        Comprobar si el monstruo puede visualizar al jugador
        :return: Booleano si ve al jugador
        """
        esVisible = mapa.es_visble(jugador.posicion, self.posicion)
        enRangoVisible = (distancia(self.posicion, jugador.posicion)
                          <= self.max_dist_vista)
        return esVisible and enRangoVisible

    def percibir(self):
        """
        Comprueba si el mosntruo percibe al jugador y 
        actualiza su estado
        :return: Booleano si percibe al jugador
        """
        percibido = True
        if(self.oler()):
            if(self.vida > jugador.vida):
                self.estado = Estado.RASTREAR
            else:
                self.estado = Estado.HUIR
        elif(self.ver()):
            if(self.vida > jugador.vida):
                self.estado = Estado.BUSCAR
            else:
                self.estado = Estado.HUIR
        else:
            self.estado = Estado.PATRULLAR
            percibido = False

        return percibido

    def buscar(self):
        """
        Calculo del camino recto y actulización de 
        la posición actual
        :return: 
        """
        pasos = mapa.buscar_camino_recto(jugador.posicion, self.posicion)
        self.posicion = (pasos[len(pasos)-1].i, pasos[len(pasos)-1].j)

    def rastrear(self):
        """
        Calculo del camino más corto y actulización de 
        la posición actual
        :return:
        """
        if(self.posicion != jugador.posicion):
            pasos = mapa.buscar_camino(self.posicion, jugador.posicion)
            if not ((jugador.posicion[0] == pasos[0].i)
                    and (jugador.posicion[1] == pasos[0].j)):
                self.posicion = (pasos[0].i, pasos[0].j)

    def huir(self):
        """
        Calculo del camino en dirección contraria al jugador
        y actulización de la posición actual
        :return:
        """
        if(self.posicion != jugador.posicion):
            #Se guardan las posiciones del jugador y del monstruo
            posJugador = np.array([jugador.posicion[0], jugador.posicion[1]])
            posMonstruo = np.array([self.posicion[0], self.posicion[1]])

            #Calculo de la dirección opuesta al jugador
            dirMJ = posJugador - posMonstruo
            posNuevo = np.array([-jugador.posicion[0], -jugador.posicion[1]])
            dirNJM = posNuevo - posMonstruo

            maximoBusquedas = 10
            contadorBusquedas = 0

            # Mientras las busquedas sean menores al máximo y
            # las coordenadas del destino y la dirección sean validas.
            while contadorBusquedas < maximoBusquedas:
                if mapa.esta_dentro((posNuevo[0], posNuevo[1])):
                    if mapa[(posNuevo[0], posNuevo[1])] == VACIO:
                        if not np.dot(dirMJ, dirNJM) > -0.3:
                            break

                # Generación del incremento en X e Y aleatoriamente
                pasoX = random.randint(-1, 1)
                pasoY = random.randint(-1, 1)

                # Se actualiza la nueva posición destino del monstruo
                posNuevo[0] = self.posicion[0] + pasoX
                posNuevo[1] = self.posicion[1] + pasoY

                # Actualiza la dirección 
                dirNJM = posNuevo - posMonstruo
                contadorBusquedas += 1

            # Calculo del camino hacia el destino
            #  y actualización de la posición
            if contadorBusquedas < maximoBusquedas:
                pasos = mapa.buscar_camino(
                    self.posicion, (posNuevo[0], posNuevo[1]))
                self.posicion = (pasos[0].i, pasos[0].j)

    def patrullar(self):
        """
        Calculo de una posición aleatoria
        y actulización de la posición actual
        :return:
        """
        pasoX = random.randint(-1, 1)
        pasoY = random.randint(-1, 1)
        nextPosition = (self.posicion[0]+pasoX, self.posicion[1]+pasoY)
        if mapa.esta_dentro(nextPosition) and (mapa[nextPosition] == VACIO):
            vacio = mapa.__getitem__(nextPosition)
            if (vacio == 0):
                self.posicion = nextPosition

    def atacar(self):
        """
        Generación aleatoriamente del daño 
        entre 0 y su fuerza máxima
        :return: Int ataque generado
        """
        return (random.randint(0, self.fuerza))

    def defender(self, ataque):
        """
        Recibir daño en caso de recibir un ataque mayor
        a la defensa y comprobar si esta muerto
        :param ataque: Int daño recibido
        :return:
        """
        if(self.armadura < ataque):
            self.vida -= (ataque - self.armadura)
        if self.vida <= 0:
            self.estado = Estado.MUERTO

    def luchar(self):
        """
        Generar ataque al jugador si 
        esta en rango valido
        :return: 
        """
        if self.estado is not Estado.MUERTO:
            if mapa.es_vecino(self.posicion, jugador.posicion):
                jugador.defender(self.atacar())

    def actualizar(self):
        """
        Actualiza y ejecuta el estado actual
        :return:
        """
        if(self.turno % self.lentitud == 0):
            if self.estado != Estado.MUERTO:
                if self.percibir():
                    self.luchar()
            func = self.switcher.get(self.estado)
            func()
        self.turno += 1


class Jugador():
    def __init__(self, posicion):
        self.posicion = posicion
        self.movimientos = []
        self.vida = 8
        self.armadura = 3
        self.fuerza = 6

    def atacar(self):
        """
        Generación aleatoriamente del daño 
        entre 0 y su fuerza máxima
        :return: Int ataque generado
        """
        return(random.randint(0, self.fuerza))

    def defender(self, ataque):
        """
        Recibir daño en caso de recibir un ataque mayor
        a la defensa y comprobar si esta muerto
        :param ataque: Int daño recibido
        :return:
        """
        if(ataque > self.armadura):
            self.vida -= (ataque-self.armadura)

    def luchar(self, m):
        """
        Generar ataque al jugador si 
        esta en rango valido
        :return: 
        """
        if mapa.es_vecino(self.posicion, m.posicion):
            m.defender(self.atacar())

    def actualizar(self, events):
        """
        Actualizar las acciones del jugador segun las 
        interacciones del usuario
        :param events: Interacciones del usuario
        :return:
        """
        for event in events:
            if event.type == QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

            # Evento tecla pulsada
            if event.type == KEYDOWN:

                # limpian los movimientos en cola
                self.movimientos.clear()

                # Se genera un nueva posición en caso de pulsar una flecha
                newPos = list(self.posicion)
                if event.key == K_RIGHT:
                    newPos[1] += 1
                if event.key == K_LEFT:
                    newPos[1] -= 1
                if event.key == K_UP:
                    newPos[0] -= 1
                if event.key == K_DOWN:
                    newPos[0] += 1
                newPos = tuple(newPos)

                # Se actualiza la posición en caso de ser valida
                if mapa.esta_dentro(newPos) and (mapa[newPos] == VACIO):
                    self.posicion = newPos

                # Tecla espacio genera un ataque
                if event.key == K_SPACE:
                    for monstruo in monstruos:
                        self.luchar(monstruo)

            # Evento click 
            elif event.type == MOUSEBUTTONDOWN:
                # Se recoge la posición de la celda destino pulsada
                pos = (event.pos[1] // LADO_CELDA, event.pos[0] // LADO_CELDA)
                # Genera el camino más corto al destino
                pasos = mapa.buscar_camino(self.posicion, pos)
                # Se actualiza la cola de movimientos
                if pasos is not None:
                    self.movimientos.clear()
                    for paso in pasos:
                        self.movimientos.append((paso.i, paso.j))

        # Se actualiza la posición del jugador si hay movimiento en cola
        if (len(self.movimientos) > 0):
            self.posicion = self.movimientos.pop(0)


if __name__ == "__main__":
    pygame.init()

    mapa = Mapa(ANCHO_MAPA, ALTO_MAPA, LADO_CELDA)
    mapa.generar_aleatorio()
    mapa.generar_automata()

    jugador = Jugador((0, 0))
    monstruos = [
        Monstruo((0, ANCHO_MAPA-1)),
        Monstruo((ALTO_MAPA-1, ANCHO_MAPA-1)),
        Monstruo((ALTO_MAPA-1, 0))
        ]

    # Bucle infinito que simula el juego
    while True:
        # Se pinta le mapa
        mapa.mostrar_mapa()
        # Se recogen los eventos
        events = pygame.event.get()
        for event in events:
            if event.type == QUIT:
                pygame.display.quit()
                pygame.quit()
                sys.exit()

        # Se actualiza las acciones del jugador en caso de estar vivo
        if(jugador.vida > 0):
            jugador.actualizar(events)
            mapa.mostrar_celda(jugador.posicion, color_mapa.ROJO)
        else:
            mapa.mostrar_celda(jugador.posicion, color_mapa.VERDE)

        # Se actualizan los estados de los monstruos vivos
        for monstruo in monstruos:
            monstruo.actualizar()
            color = color_mapa.AZUL
            if(monstruo.estado == Estado.MUERTO):
                color = color_mapa.MORADO
            mapa.mostrar_celda(monstruo.posicion, color)

        pygame.display.update()
        pygame.time.wait(100)