import pygame

pygame.init()

# Constantes
ancho_ventana = 1000
alto_ventana = 700
ancho_mapa = 25
alto_mapa = 20
tamano_celda = 30
fps = 60

# Colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
gris = (50, 50, 50)
verde_liana = (34, 139, 34)
azul = (100, 149, 237)
rojo = (255, 0, 0)
verde_jugador = (0, 255, 0)
amarillo = (255, 255, 0)
naranja = (255, 165, 0)

# Tipos de terreno
camino = 0
muro = 1
tunel = 2
liana = 3
salida = 4

class Casilla:
    def __init__(self, x, y, tipo):
        self.x = x
        self.y = y
        self.tipo = tipo
        self.color = blanco
    
    def puede_pasar_jugador(self):
        return False
    
    def puede_pasar_enemigo(self):
        return False
    
    def dibujar(self, pantalla, offset_x, offset_y):
        pygame.draw.rect(pantalla, self.color, 
                        (self.x * tamano_celda + offset_x, 
                         self.y * tamano_celda + offset_y, 
                         tamano_celda, tamano_celda))
        pygame.draw.rect(pantalla, negro, 
                        (self.x * tamano_celda + offset_x, 
                         self.y * tamano_celda + offset_y, 
                         tamano_celda, tamano_celda), 1)
