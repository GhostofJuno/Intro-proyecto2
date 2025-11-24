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
        # guarda posición y tipo básico de la casilla
        self.x = x
        self.y = y
        self.tipo = tipo
        self.color = blanco
    
    def puede_pasar_jugador(self):
        # por defecto nadie puede pasar
        return False
    
    def puede_pasar_enemigo(self):
        # igual que arriba, se cambia en clases hijas
        return False
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # dibuja la casilla y su borde usando su color asignado
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
        # camino libre para jugador y enemigos
        Casilla.__init__(self, x, y, camino)
        self.color = blanco
    
    def puede_pasar_jugador(self):
        return True
    
    def puede_pasar_enemigo(self):
        return True

class Muro(Casilla):
    def __init__(self, x, y):
        # muro actúa como obstáculo usando el color oscuro
        Casilla.__init__(self, x, y, muro)
        self.color = gris_oscuro

class Tunel(Casilla):
    def __init__(self, x, y):
        # tunel permite paso del jugador y tiene un símbolo especial
        Casilla.__init__(self, x, y, tunel)
        self.color = azul_tunel
    
    def puede_pasar_jugador(self):
        return True
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # dibuja la base y luego el triángulo que identifica el tunel
        Casilla.dibujar(self, pantalla, offset_x, offset_y)
        centro_x = self.x * tamanio_celda + tamanio_celda // 2 + offset_x
        centro_y = self.y * tamanio_celda + tamanio_celda // 2 + offset_y
        pygame.draw.polygon(pantalla, blanco, [
            (centro_x, centro_y - 8),
            (centro_x - 6, centro_y + 8),
            (centro_x + 6, centro_y + 8)
        ])

class Liana(Casilla):
    def __init__(self, x, y):
        # liana solo sirve como obstáculo parcial según quién pase
        Casilla.__init__(self, x, y, liana)
        self.color = verde_liana
    
    def puede_pasar_enemigo(self):
        # enemigos sí pueden cruzarla
        return True
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # círculo negro para identificar la liana
        Casilla.dibujar(self, pantalla, offset_x, offset_y)
        centro_x = self.x * tamanio_celda + tamanio_celda // 2 + offset_x
        centro_y = self.y * tamanio_celda + tamanio_celda // 2 + offset_y
        pygame.draw.circle(pantalla, negro, (centro_x, centro_y), 5)

class Salida(Casilla):
    def __init__(self, x, y):
        # salida accesible para jugador y enemigos
        Casilla.__init__(self, x, y, salida)
        self.color = amarillo
    
    def puede_pasar_jugador(self):
        return True
    
    def puede_pasar_enemigo(self):
        return True
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # dibuja la casilla y coloca la letra 'E' al centro para marcar la salida
        Casilla.dibujar(self, pantalla, offset_x, offset_y)
        centro_x = self.x * tamanio_celda + tamanio_celda // 2 + offset_x
        centro_y = self.y * tamanio_celda + tamanio_celda // 2 + offset_y
        fuente = pygame.font.Font(None, 24)
        texto = fuente.render("E", True, negro)
        rect = texto.get_rect(center=(centro_x, centro_y))
        pantalla.blit(texto, rect)

class Trampa:
    def __init__(self, x, y):
        # trampa funciona como objeto independiente con posición fija
        self.x = x
        self.y = y
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # círculo naranja que indica visualmente la trampa
        pygame.draw.circle(pantalla, naranja, 
                          (int(self.x * tamanio_celda + tamanio_celda/2 + offset_x),
                           int(self.y * tamanio_celda + tamanio_celda/2 + offset_y)),
                          int(tamanio_celda/3))

