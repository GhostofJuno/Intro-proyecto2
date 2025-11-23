import pygame

pygame.init()

# Constantes
ancho_ventana = 1000
alto_ventana = 700
ancho_mapa = 25
alto_mapa = 20
tamanio_celda = 30
fps = 60

# Colores
negro = (0, 0, 0)
blanco = (255, 255, 255)
gris_oscuro = (50, 50, 50)
verde_liana = (34, 139, 34)
azul_tunel = (100, 149, 237)
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
                        (self.x * tamanio_celda + offset_x, 
                         self.y * tamanio_celda + offset_y, 
                         tamanio_celda, tamanio_celda))
        pygame.draw.rect(pantalla, negro, 
                        (self.x * tamanio_celda + offset_x, 
                         self.y * tamanio_celda + offset_y, 
                         tamanio_celda, tamanio_celda), 1)

class Camino(Casilla):
    def __init__(self, x, y):
        super().__init__(x, y, camino)
        self.color = blanco
    
    def puede_pasar_jugador(self):
        return True
    
    def puede_pasar_enemigo(self):
        return True

class Muro(Casilla):
    def __init__(self, x, y):
        super().__init__(x, y, muro)
        self.color = gris_oscuro

class Tunel(Casilla):
    def __init__(self, x, y):
        super().__init__(x, y, tunel)
        self.color = azul_tunel
    
    def puede_pasar_jugador(self):
        return True
    
    def dibujar(self, pantalla, offset_x, offset_y):
        super().dibujar(pantalla, offset_x, offset_y)
        centro_x = self.x * tamanio_celda + tamanio_celda // 2 + offset_x
        centro_y = self.y * tamanio_celda + tamanio_celda // 2 + offset_y
        pygame.draw.polygon(pantalla, blanco, [
            (centro_x, centro_y - 8),
            (centro_x - 6, centro_y + 8),
            (centro_x + 6, centro_y + 8)
        ])
