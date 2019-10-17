
import pygame
from math import *
"""-------------------------------------------------------------------
Universidad: Universidad del Valle de Guatemala
Curso: Gráficas por Computadora
Fecha: 23-5-2019
Nombre: Alejandro Tejada 
Carnet: 17584
Nombre programa: Casting.py
Propósito: Este programa es el proyecto del juego
Auxiliar: El que toque. :)
----------------------------------------------------------------------
"""

# Declaración de constantes para el juego
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BACKGROUND = (0, 255, 255)
AumentoBloqueX = 20
AumentoBloqueY = 20
TamanoBloqueX = 50
TamanoBloqueY = 50
TamanoPantallaX = 300
TamanoPantallaY = 300
colorFondoMapa2D = (255, 255, 255)
colorRayoRaycaster = (255, 255, 255)
tamañoTexturaX = 104
tamañoTexturaY = 104
tamañoTexturaManox = 104
tamañoTexturaManoy = 104
TamañoTexturaParedX = 64
TamañoTexturaParedY = 104
zoom = 60
# Declaración de texturas
texturas = {
    "1": pygame.image.load('./arbolito2.png'),
    "2": pygame.image.load('./arbolito2.png'),
    "3": pygame.image.load('./arbolito2.png'),
    "4": pygame.image.load('./arbolito2.png'),
    "5": pygame.image.load('./arbolito2.png'),
}
# Mano del jugador y sprites de los pesronas que aparecen
manoPlayer = pygame.image.load('./magicWand2.png')
ArrayPersonajes = [
    {
        "x": 100,
        "y": 420,
        "texture": pygame.image.load('./sprite7.png')
    },
    {
        "x": 390,
        "y": 125,
        "texture": pygame.image.load('./sprite3.png')
    },
    {
        "x": 250,
        "y": 125,
        "texture": pygame.image.load('./sprite4.png')
    },
    {
        "x": 250,
        "y": 425,
        "texture": pygame.image.load('./sprite1.png')
    },
    {
        "x": 390,
        "y": 420,
        "texture": pygame.image.load('./sprite6.png')
    }
]

# Clase raycast


class Raycaster(object):
    def __init__(self, screen):
        _, _, self.width, self.height = screen.get_rect()
        self.screen = screen
        self.blocksize = TamanoBloqueX
        self.player = {
            "x": self.blocksize + AumentoBloqueX,
            "y": self.blocksize + AumentoBloqueY,
            "a": pi/3,
            "fov": pi/3
        }
        self.map = []
        self.zbuffer = [-float('inf') for z in range(0, TamanoPantallaX)]

    def cargar_mapa(self, filename):
        with open(filename) as f:
            for line in f.readlines():
                self.map.append(list(line))
    # cast_ray

    def cast_ray(self, a):
        d = 0
        while True:
            x = self.player["x"] + d*cos(a)
            y = self.player["y"] + d*sin(a)

            i = int(x/TamanoBloqueX)
            j = int(y/TamanoBloqueY)

            if self.map[j][i] != ' ':
                hitx = x - i*TamanoBloqueX
                hity = y - j*TamanoBloqueY

                if 1 < hitx < (TamanoBloqueX-1):
                    maxhit = hitx
                else:
                    maxhit = hity
                tx = int(maxhit * TamañoTexturaParedX / TamanoBloqueX)
                return d, self.map[j][i], tx
            # se usará uno para que se vea bien
            d += 1
    # acá se dibuja el escenario

    def dibujar_escenario(self, x, h, texture, tx):
        start = int((TamanoPantallaX/2) - h/2)
        end = int((TamanoPantallaY/2) + h/2)
        for y in range(start, end):
            ty = int(((y - start)*TamañoTexturaParedY)/(end - start))
            c = texture.get_at((tx, ty))
            screen.set_at((x, y), c)

    # se dibujan los protes
    def dibujar_sprite(self, sprite):
        sprite_a = atan2(sprite["y"] - self.player["y"],
                         sprite["x"] - self.player["x"])
        sprite_d = ((self.player["x"] - sprite["x"]) **
                    2 + (self.player["y"] - sprite["y"])**2)**0.5
        sprite_sizex = (TamanoPantallaX/sprite_d) * zoom
        sprite_sizey = (TamanoPantallaY/sprite_d) * zoom
        # se tienen que decalarar sprites en x y en Y para evitar los números mágicos
        sprite_x = (sprite_a - self.player["a"])*TamanoPantallaX / \
            self.player["fov"] + (TamanoPantallaX/2) - sprite_sizex/2
        sprite_y = int(TamanoPantallaY/2) - sprite_sizey/2
        sprite_x = int(sprite_x)
        sprite_y = int(sprite_y)
        sprite_sizex = int(sprite_sizex)
        sprite_sizey = int(sprite_sizey)
        for x in range(sprite_x, sprite_x + sprite_sizex):
            for y in range(sprite_y, sprite_y + sprite_sizey):
                if 0 < x < TamanoPantallaX and self.zbuffer[x] >= sprite_d:
                    tx = int((x - sprite_x) * tamañoTexturaX/sprite_sizex)
                    ty = int((y - sprite_y) * tamañoTexturaY/sprite_sizey)
                    c = sprite["texture"].get_at((tx, ty))
                    # se pinta el sprite menos el color cian
                    if c != (152, 0, 136, 255):
                        screen.set_at((x, y), c)
                        self.zbuffer[x] = sprite_d
    # el jugador o la mano de harry se dibujaron de ese tamaño

    def dibujar_jugador(self, xi, yi, w=156, h=156):
        for x in range(xi, xi + w):
            for y in range(yi, yi + h):
                tx = int((x - xi) * tamañoTexturaManox/w)
                ty = int((y - yi) * tamañoTexturaManoy/h)
                c = manoPlayer.get_at((tx, ty))
                if c != (152, 0, 136, 255):
                    screen.set_at((x, y), c)
    # parte donde se renderiza

    def renderizar(self):
        for i in range(0, TamanoPantallaX):
            a = self.player["a"] - self.player["fov"] / \
                2 + self.player["fov"]*i/TamanoPantallaX
            d, c, tx = self.cast_ray(a)
            # condición de que no truene cuando es 0 el valor de la pared
            if(d <= 0):
                d = 30
                c = 1
                tx = 150
            else:
                x = i
                h = TamanoPantallaY/(d*cos(a-self.player["a"])) * zoom
                self.dibujar_escenario(x, h, texturas[c], tx)
                self.zbuffer[i] = d
        # se dibujan los sprites de personajes
        for enemy in ArrayPersonajes:
            screen.set_at((enemy["x"], enemy["y"]), (0, 0, 0))
            self.dibujar_sprite(enemy)
        # se dibuja la mano del jugador
        self.dibujar_jugador(int(TamanoPantallaX) - 200,
                             int(TamanoPantallaY) - 150)

#se inicia pygame
pygame.init()
#pantalla completa, y otras configuraicones
screen = pygame.display.set_mode(
    (TamanoPantallaX, TamanoPantallaY), pygame.DOUBLEBUF | pygame.HWACCEL | pygame.FULLSCREEN | pygame.HWSURFACE)
screen.set_alpha(None)
r = Raycaster(screen)
r.cargar_mapa('./mapita.txt')
step = 5
c = 0
while True:
    screen.fill((5, 5, 5))
    #llenamos la pantalla de negro para que combinen con los arboles
    r.renderizar()
    for e in pygame.event.get():
        if e.type == pygame.QUIT or (e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE):
            exit(0)
        if e.type == pygame.KEYDOWN:
            """
            Las condiciones de teclas son interesantes: para que cuando se de una vuelta total, el render buffer no falle
            se tiene que reiniciar la vuelta: ¿como? La solución que se me ocurrió es que una vuelta es 2PI, entonces
            cuando se pasa de eso se resetea o si es menor a cero también
            Para poder moverse, se usaron formulas de seno y coseno. Adicionalmente, se hicieron condiciones para que 
            no pueda parase de una pared.
            """
            if e.key == pygame.K_RIGHT:
                if(r.player["a"] > 2*pi):
                    r.player["a"] = 0
                else:
                    r.player["a"] += pi/10
            elif e.key == pygame.K_LEFT:
                if(r.player["a"] < -pi):
                    r.player["a"] = 2*pi
                else:
                    r.player["a"] -= pi/10
            elif e.key == pygame.K_UP:

                if(r.player["x"] >= 350):
                    r.player["x"] = r.player["x"]-5
                else:
                    if(r.player["x"] < 115):
                        r.player["x"] = r.player["x"]+5
                    else:
                        r.player["x"] = r.player["x"] + \
                            degrees(cos(r.player["a"]))

                if(r.player["y"] >= 350):
                    r.player["y"] = r.player["y"]-10
                else:
                    if(r.player["y"] < 120):
                        r.player["y"] = r.player["y"]+5
                    else:
                        r.player["y"] = r.player["y"] + \
                            degrees(sin(r.player["a"]))
            elif e.key == pygame.K_DOWN:

                if(r.player["x"] >= 350):
                    r.player["x"] = r.player["x"]-5
                else:
                    if(r.player["x"] < 115):
                        r.player["x"] = r.player["x"]+5
                    else:
                        r.player["x"] = r.player["x"] - \
                            degrees(cos(r.player["a"]))

                if(r.player["y"] >= 350):
                    r.player["y"] = r.player["y"]-5
                else:
                    if(r.player["y"] < 120):
                        r.player["y"] = r.player["y"]+5
                    else:
                        r.player["y"] = r.player["y"] - \
                            degrees(sin(r.player["a"]))

            if e.key == pygame.K_f:
                if screen.get_flags() and pygame.FULLSCREEN:
                    pygame.display.set_mode((TamanoPantallaX, TamanoPantallaY))
                else:
                    pygame.display.set_mode(
                        (TamanoPantallaX, TamanoPantallaY),  pygame.DOUBLEBUF | pygame.HWACCEL | pygame.FULLSCREEN)

    pygame.display.flip()
