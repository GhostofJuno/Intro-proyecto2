#marii porfa revisa que todo te corra bien, si encuentras algun error me avisas porfiss
import pygame
import random
import json
import time 
from datetime import datetime

pygame.init()
pygame.mixer.init() #esto es para los rolones

# Constantes
fondo_menu = "#58934C"
ancho_ventana = 1000
alto_ventana = 700
ancho_mapa = 25
alto_mapa = 20
tamanio_celda = 30
fps = 60

# fuentes!
fuente1 = pygame.font.SysFont("Arial", 48)
fuente_boton = pygame.font.SysFont("Arial", 40)
fuente_pequeña = pygame.font.SysFont("Arial", 24)
fuente_input = pygame.font.SysFont("Arial", 32)

# Colores #los cambie jsjsj
negro          = "#0A0F0A"
blanco         = "#EAEAEA"   
gris_oscuro    = "#3B2F26"
verde_liana    = "#7FFF00"    
verde          = "#A8B57A"   
azul_tunel     = "#483D8B"   
azul_oscuro    = "#1A103D"   
rojo           = "#732323"   
verde_jugador  = "#FBC58D"   
amarillo       = "#FFD966"   
naranja        = "#C65A2E"

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
        # Nota: x e y son coordenadas de celda (enteras)
        self.x = x
        self.y = y
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # círculo naranja que indica visualmente la trampa
        centro_x = int(self.x * tamanio_celda + tamanio_celda/2 + offset_x)
        centro_y = int(self.y * tamanio_celda + tamanio_celda/2 + offset_y)
        pygame.draw.circle(pantalla, naranja, 
                            (centro_x, centro_y),
                            int(tamanio_celda/3))

class Boton:
    def __init__(self, x, y, ancho, alto, texto, color, color_hover):
        self.rect = pygame.Rect(x, y, ancho, alto)
        self.texto = texto
        self.color = color
        self.color_hover = color_hover

    def draw(self, pantalla, fuente):
        mouse_pos = pygame.mouse.get_pos()

        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(pantalla, self.color_hover, self.rect, border_radius=12)
        else:
            pygame.draw.rect(pantalla, self.color, self.rect, border_radius=12)

        txt = fuente.render(self.texto, True, negro)
        txt_rect = txt.get_rect(center=self.rect.center)
        pantalla.blit(txt, txt_rect)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return 

class Jugador:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.velocidad_normal = 0.15
        self.velocidad_correr = 0.25
        self.energia = 100
        self.energia_max = 100
        self.recuperacion_energia = 0.5
        self.consumo_energia = 0.8
        self.corriendo = False
        
    def mover(self, dx, dy, mapa, modo_juego): 
        nueva_x = self.x + dx
        nueva_y = self.y + dy
        
        #revisamos que no choque con pared
        if nueva_x < 0 or nueva_x >= ancho_mapa or nueva_y < 0 or nueva_y >= alto_mapa:
            return False
        
        margen = 0.3
        esquinas = [
            (nueva_x - margen, nueva_y - margen),
            (nueva_x + margen, nueva_y - margen),
            (nueva_x - margen, nueva_y + margen),
            (nueva_x + margen, nueva_y + margen)
        ]
        
        for ex, ey in esquinas: #revisa las esquinas alrededor del jugador para evitar que se meta
            if ex < 0 or ex >= ancho_mapa or ey < 0 or ey >= alto_mapa:
                return False
            
            # Se convierte a entero para usar como índice de matriz
            celda_x, celda_y = int(ex), int(ey)

            # Revisa límites después de convertir a int
            if not (0 <= celda_y < alto_mapa and 0 <= celda_x < ancho_mapa):
                return False

            casilla = mapa[celda_y][celda_x]

            if not casilla.puede_pasar_jugador(): #revisa tipo de casilla
                return False
            
            # no puede pasar por las lianas nunca!
            if casilla.tipo == liana: 
                return False
        
        self.x = nueva_x
        self.y = nueva_y
        return True
    
    def actualizar_energia(self):
        if self.corriendo and self.energia > 0:
            self.energia -= self.consumo_energia
            if self.energia <= 0:
                self.energia = 0
                self.corriendo = False
        elif not self.corriendo:
            self.energia += self.recuperacion_energia
            if self.energia > self.energia_max:
                self.energia = self.energia_max
    
    def dibujar(self, pantalla, offset_x, offset_y):
        # El cálculo asume que self.x y self.y son la posición del CENTRO de la entidad
        centro_x = int(self.x * tamanio_celda + offset_x)
        centro_y = int(self.y * tamanio_celda + offset_y)
        
        pygame.draw.circle(pantalla, verde_jugador,  
                            (centro_x, centro_y), 
                            int(tamanio_celda/2.5)) 

#le cambie cosas a estos bichillos
class Enemigo:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)

        # MOVIMIENTO BÁSICO
        self.velocidad = 0.05
        self.dir_x, self.dir_y = random.choice([(1,0), (-1,0), (0,1), (0,-1)])

        # PATRULLAR
        self.patrulla_rango = 6   # tamaño del área de "patrulla"
        self.patrulla_centro = (x, y)
        self.estado = "patrulla"  # o "perseguir"

        # DETECTAR JUGADOR
        self.radio_vision = 7     # distancia para detectar al jugador
        self.perder_vision = 10   # cuando se aleja demasiado

        # CONTROL
        self.frames_desde_cambio = 0
        self.cambio_cada = random.randint(30, 90) # Aumento de tiempo para patrullaje
        self.muerto = False

    def puede_moverse(self, nx, ny, mapa, modo_juego):
        margen = 0.35
        for ex, ey in [
            (nx, ny),
            (nx-margen, ny-margen),
            (nx+margen, ny-margen),
            (nx-margen, ny+margen),
            (nx+margen, ny+margen),
        ]:
            if ex < 0 or ex >= ancho_mapa or ey < 0 or ey >= alto_mapa:
                return False
            celda = mapa[int(ey)][int(ex)]
            if celda.tipo == muro:
                return False
            
            if celda.tipo == tunel: 
                return False
        return True

    def distancia_jugador(self, jugador):
        return ((self.x - jugador.x)**2 + (self.y - jugador.y)**2) ** 0.5

    def esta_en_rango_patrulla(self):
        cx, cy = self.patrulla_centro
        return (
            abs(self.x - cx) < self.patrulla_rango and 
            abs(self.y - cy) < self.patrulla_rango
        )

    def mover(self, jugador, mapa, modo_juego):
        if self.muerto:
            return

        # CAMBIO DE ESTADO: DETECTAR JUGADOR
        dist = self.distancia_jugador(jugador)

        if self.estado == "patrulla":
            if dist < self.radio_vision:
                self.estado = "perseguir"
        elif self.estado == "perseguir":
            if dist > self.perder_vision:
                self.estado = "patrulla"

        #LÓGICA DE MOVIMIENTO SEGÚN ESTADO
        if self.estado == "patrulla":
            self.mover_patrullando(mapa, modo_juego)

        elif self.estado == "perseguir":
            # Diferencia: Modo 1 (Escapa) persigue, Modo 2 (Cazador) huye.
            if modo_juego == 1:
                self.mover_persiguiendo(jugador, mapa, modo_juego)
            else:
                self.mover_huyendo(jugador, mapa, modo_juego)

    def mover_patrullando(self, mapa, modo_juego):
        self.frames_desde_cambio += 1

        #FUERA DE RANGO: Si se aleja demasiado del centro de patrulla, gira
        if not self.esta_en_rango_patrulla():
            cx, cy = self.patrulla_centro
            # Fuerza el giro hacia el centro
            self.dir_x = 1 if cx > self.x else -1 if cx < self.x else 0
            self.dir_y = 1 if cy > self.y else -1 if cy < self.y else 0
            # Resetea el contador para que siga en esa dirección por un tiempo
            self.frames_desde_cambio = 0
            
        #CAMBIO DE DIRECCIÓN POR TIEMPO: Si ha pasado el tiempo, elige una dirección nueva
        elif self.frames_desde_cambio > self.cambio_cada:
            # Nueva dirección aleatoria (incluyendo quedarse quieto (0,0))
            self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1), (0,0)])
            self.frames_desde_cambio = 0
            # Nuevo tiempo aleatorio para la siguiente patrulla (0.5 a 1.5 seg)
            self.cambio_cada = random.randint(30, 90) 


        #INTENTO DE MOVIMIENTO
        nx = self.x + self.dir_x * self.velocidad
        ny = self.y + self.dir_y * self.velocidad

        #COLISIÓN: Si choca con algo, cambia de dirección inmediatamente
        if not self.puede_moverse(nx, ny, mapa, modo_juego):
            # Elige una dirección nueva aleatoria y resetea el contador para que gire
            self.dir_x, self.dir_y = random.choice([(1,0),(-1,0),(0,1),(0,-1)])
            self.frames_desde_cambio = 0
            return

        #APLICAR MOVIMIENTO
        self.x = nx
        self.y = ny

    def mover_persiguiendo(self, jugador, mapa, modo_juego):
        # Lógica de Búsqueda Voraz Reactiva: Prioriza el movimiento que más acerca al jugador
        v = self.velocidad # La velocidad actual del enemigo

        #Lista de todos los movimientos posibles (4 direcciones)
        movimientos = [
            (v, 0), (-v, 0), (0, v), (0, -v)
        ]

        #Función de puntuación: Distancia al jugador después del movimiento
        def score_move(move):
            mx, my = move
            nx = self.x + mx
            ny = self.y + my
            
            #Distancia al cuadrado (se usa para ordenar, más rápido de calcular)
            dist_sq = (jugador.x - nx)**2 + (jugador.y - ny)**2
            # Queremos el score más PEQUEÑO (menor distancia al jugador = mejor)
            return dist_sq

        #Ordenar los movimientos: el que tenga la menor distancia_cuadrada va primero
        random.shuffle(movimientos)
        movimientos.sort(key=score_move)

        #Intentar los movimientos en orden
        movido = False
        movimiento_exitoso = (0, 0)
        
        for mx, my in movimientos:
            nx = self.x + mx
            ny = self.y + my
            
            if self.puede_moverse(nx, ny, mapa, modo_juego):
                self.x = nx
                self.y = ny
                movido = True
                movimiento_exitoso = (mx, my)
                break 

        #Actualizar dirección para el dibujo
        if movido:
            self.dir_x = 1 if movimiento_exitoso[0] > 0 else -1 if movimiento_exitoso[0] < 0 else 0
            self.dir_y = 1 if movimiento_exitoso[1] > 0 else -1 if movimiento_exitoso[1] < 0 else 0
        else:
            #Si no se pudo mover (bloqueo total), intenta una dirección aleatoria (o eso espero )
            # para el siguiente frame, rompiendo el estancamiento.
            self.dir_x, self.dir_y = random.choice([(v, 0), (-v, 0), (0, v), (0, -v)])
            self.dir_x = 1 if self.dir_x > 0 else -1 if self.dir_x < 0 else 0
            self.dir_y = 1 if self.dir_y > 0 else -1 if self.dir_y < 0 else 0


    def mover_huyendo(self, jugador, mapa, modo_juego):
        # Lógica de Búsqueda para Huida (Modo Cazador)
        #Definición de pesos para Huir/Salida
        salida_x = ancho_mapa - 2.5
        salida_y = alto_mapa - 2.5
        
        peso_huir = 0.5
        peso_salida = 0.5
        dist_jugador_actual = self.distancia_jugador(jugador)
        
        # Ajusta los pesos: más huida si está cerca, a la salida si está lejos
        if dist_jugador_actual < 3:
            peso_huir = 0.8
            peso_salida = 0.2
        elif dist_jugador_actual > 7:
            peso_huir = 0.2
            peso_salida = 0.8

        # 2. Lista de todos los movimientos posibles (4 direcciones)
        v = self.velocidad
        movimientos = [
            (v, 0), (-v, 0), (0, v), (0, -v)
        ]

        #Función de puntuación para huida combinada
        def score_move_flee(move):
            mx, my = move
            nx = self.x + mx
            ny = self.y + my
            
            # Distancia del jugador (queremos MAXIMIZAR)
            dist_jugador = ((jugador.x - nx)**2 + (jugador.y - ny)**2) ** 0.5
            
            # Distancia de la salida (queremos MINIMIZAR)
            dist_salida = ((salida_x - nx)**2 + (salida_y - ny)**2) ** 0.5

            # Puntuación final = (+Distancia del jugador * peso) - (+Distancia de la salida * peso)
            # Un valor más alto significa mejor movimiento de huida Y acercamiento a la salida.
            score = (dist_jugador * peso_huir) - (dist_salida * peso_salida) 
            return score

        #Ordenar los movimientos: el que tenga la MAYOR puntuación va primero
        random.shuffle(movimientos)
        movimientos.sort(key=score_move_flee, reverse=True) # reverse=True para MAXIMIZAR el score

        #Intentar los movimientos en orden
        movido = False
        movimiento_exitoso = (0, 0)
        
        for mx, my in movimientos:
            nx = self.x + mx
            ny = self.y + my
            
            if self.puede_moverse(nx, ny, mapa, modo_juego):
                self.x = nx
                self.y = ny
                movido = True
                movimiento_exitoso = (mx, my)
                break 

        #Actualizar dirección para el dibujo
        if movido:
            self.dir_x = 1 if movimiento_exitoso[0] > 0 else -1 if movimiento_exitoso[0] < 0 else 0
            self.dir_y = 1 if movimiento_exitoso[1] > 0 else -1 if movimiento_exitoso[1] < 0 else 0
        else:
            #Si no se pudo mover (bloqueo total), intenta una dirección aleatoria 
            #para el siguiente frame, rompiendo el estancamiento.
            self.dir_x, self.dir_y = random.choice([(v, 0), (-v, 0), (0, v), (0, -v)])
            self.dir_x = 1 if self.dir_x > 0 else -1 if self.dir_x < 0 else 0
            self.dir_y = 1 if self.dir_y > 0 else -1 if self.dir_y < 0 else 0


    def dibujar(self, pantalla, offset_x, offset_y):
        centro_x = int(self.x * tamanio_celda + offset_x)
        centro_y = int(self.y * tamanio_celda + offset_y)

        color_base = rojo

        # parpadeo cuando persiguen, esta bien bonito, si o que
        if self.estado == "perseguir" and random.random() < 0.2:
            color_base = amarillo

        pygame.draw.circle(
            pantalla,
            color_base,
            (centro_x, centro_y),
            int(tamanio_celda / 2.5)
        )

class Mapa:
    def __init__(self, ancho, alto):
        # se guarda el tamaño y se genera el mapa inicial
        self.ancho = ancho
        self.alto = alto
        self.matriz = []
        self.generar_mapa()

    def generar_mapa(self,):
        """genera el laberinto mezclando exploración, iteración y ajustes aleatorios"""

        # se inicia toda la matriz llena de muros
        self.matriz = [[Muro(x, y) for x in range(self.ancho)] for y in range(self.alto)]

        # Inicializa la pila de celdas a visitar
        pila = [(1, 1)] 
        self.matriz[1][1] = Camino(1, 1) # Marca el inicio como camino
        
        # Direcciones de movimiento (pasos de 2)
        direcciones = [(-2, 0), (0, 2), (2, 0), (0, -2)]

        while pila:
            #Toma la celda actual de la cima de la pila (backtracking)
            y, x = pila[-1] 
            
            #Encuentra vecinos no visitados
            vecinos_validos = []
            random.shuffle(direcciones) # Orden aleatorio para evitar patrones
            
            for dy, dx in direcciones:
                ny, nx = y + dy, x + dx
                
                #Revisa límites
                if 1 <= ny < self.alto - 1 and 1 <= nx < self.ancho - 1:
                    # Revisa si la celda vecina es un Muro (no visitada)
                    if self.matriz[ny][nx].tipo == muro:
                        vecinos_validos.append((ny, nx, y + dy // 2, x + dx // 2))

            #Si hay vecinos no visitados, avanza
            if vecinos_validos:
                # Elige el primer vecino (ya están en orden aleatorio)
                ny, nx, pared_y, pared_x = vecinos_validos[0] 
                
                # Abre la pared intermedia
                self.matriz[pared_y][pared_x] = Camino(pared_x, pared_y)
                
                # Convierte la nueva celda en camino y la añade a la pila
                self.matriz[ny][nx] = Camino(nx, ny)
                pila.append((ny, nx))
            else:
                #Si no hay vecinos vuelve a la celda anterior
                pila.pop() 
                
        #intenta asegurar que haya al menos un camino hacia la salida
        for i in range(1, self.alto - 1):
            if self.matriz[i][self.ancho - 3].tipo == camino:
                self.matriz[i][self.ancho - 2] = Camino(self.ancho - 2, i)

        for i in range(1, self.ancho - 1):
            if self.matriz[self.alto - 3][i].tipo == camino:
                self.matriz[self.alto - 2][i] = Camino(i, self.alto - 2)

        # añade conexiones adicionales en zonas aleatorias
        # esto evita que el laberinto sea demasiado cerrado o lineal
        for intento in range(40):
            y = random.randint(2, self.alto - 3)
            x = random.randint(2, self.ancho - 3)

            if self.matriz[y][x].tipo == muro:
                vecinos_camino = 0

                # cuenta cuántos caminos hay alrededor
                for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < self.alto and 0 <= nx < self.ancho:
                        if self.matriz[ny][nx].tipo == camino:
                            vecinos_camino += 1

                # si hay pasillos a ambos lados, abre un punto extra
                if vecinos_camino == 2:
                    self.matriz[y][x] = Camino(x, y)

        # coloca túneles para el jugador en posiciones válidas y poco visibles
        tuneles_creados = 0
        for y in range(2, self.alto - 2):
            for x in range(2, self.ancho - 2):
                if tuneles_creados < 4 and self.matriz[y][x].tipo == camino:
                    if random.random() < 0.015:
                        # evita esquinas para no romper el inicio ni la salida
                        if not ((y < 4 and x < 4) or (y > self.alto - 5 and x > self.ancho - 5)):
                            self.matriz[y][x] = Tunel(x, y)
                            tuneles_creados += 1

        # coloca lianas para los enemigos en muros que tengan un camino cerca
        lianas_creadas = 0
        for y in range(2, self.alto - 2):
            for x in range(2, self.ancho - 2):
                if lianas_creadas < 8 and self.matriz[y][x].tipo == muro:
                    if random.random() < 0.02:
                        tiene_vecino = False

                        # revisa si hay un pasillo que permita usar esa liana
                        for dy, dx in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < self.alto and 0 <= nx < self.ancho:
                                if self.matriz[ny][nx].tipo in (camino, liana):
                                    tiene_vecino = True
                                    break

                        if tiene_vecino:
                            self.matriz[y][x] = Liana(x, y)
                            lianas_creadas += 1

        # marca la salida en la esquina inferior derecha
        self.matriz[self.alto - 2][self.ancho - 2] = Salida(
            self.ancho - 2, self.alto - 2
        )

    def dibujar(self, pantalla, offset_x, offset_y):
        # recorre toda la matriz y dibuja cada casilla según su tipo
        for fila in self.matriz:
            for casilla in fila:
                casilla.dibujar(pantalla, offset_x, offset_y)

class Juego:
    def __init__(self):
        # crea la ventana del juego y configuraciones iniciales
        self.pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana))
        pygame.display.set_caption("Proyecto de intro de Mari y Junn (❁´◡`❁)")
        self.reloj = pygame.time.Clock()

        # variables principales del estado del juego
        self.nombre_jugador = ""
        self.puntajes = self.cargar_puntajes()
        self.estado = "menu"       # controla qué pantalla se muestra
        self.modo_juego = None     # define si es modo escapa o cazador
        self.dificultad = 1        # 1: Fácil, 2: Normal, 3: Difícil
        self.mostrar_rejugar = False 
        self.mapa = None
        self.jugador = None
        self.enemigos = []
        self.trampas = []
        self.trampa_cooldown = 0   # evita poner trampas repetidamente
        self.max_trampas = 3
        self.tiempo_inicio = 0
        self.tiempo_limite = 60    # Se inicializa, pero se ajustará según la dificultad
        self.num_enemigos = 0      # Se inicializa, pero se ajustará según la dificultad
        self.puntos = 0
        self.enemigos_escapados = 0
        self.offset_x = 50         # posiciona el mapa dentro de la ventana
        self.offset_y = 50
        
        self.musica_urgente_activa = False 

        # carga imágenes y sonidos, si fallan el juego sigue funcionando
        try:
            self.logo = pygame.image.load("owlogo.png")
            self.logo_grande = pygame.transform.scale(self.logo, (400, 230))
            self.sonido_click = pygame.mixer.Sound("pop.wav")
            self.sonido_click.set_volume(0.6)
        except:
            self.logo_grande = None
            self.sonido_click = None

        # musicaaa
        self.sonido_menu = "onewaymenuLOOPED.wav"
        self.sonido_escapa_normal = "oneWayLOOPED.wav"
        self.sonido_escapa_urgente = "notime.wav"
        self.sonido_cazador_normal = "onthehuntLOOPED.wav"
        self.sonido_cazador_urgente = "notimeforhunting.wav"

        # Inicializa la música del menú al inicio
        self.reproducir_musica(self.sonido_menu)

        # botones del menú principal
        self.boton_jugar = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 0,
            300,
            70,
            "JUGAR",
            "#3FD98E",
            "#2FB975",
        )
        self.boton_puntajes = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 90,
            300,
            70,
            "PUNTAJES",
            "#6A7DFF",
            "#5665D6",
        )
        self.boton_salir = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 180,
            300,
            70,
            "SALIR",
            "#FF5E6C",
            "#D94A56",
        )

        # botones del menú de selección de modos
        self.boton_escapa = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 - 50,
            300,
            70,
            "MODO ESCAPA",
            "#3FD98E",
            "#2FB975",
        )
        self.boton_cazador = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 40,
            300,
            70,
            "MODO CAZADOR",
            "#FF5E6C",
            "#D94A56",
        )
        self.boton_volver = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 130,
            300,
            70,
            "VOLVER",
            "#6A7DFF",
            "#5665D6",
        )
        
        # --- BOTONES PARA SELECCIÓN DE DIFICULTAD ---
        self.boton_facil = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 - 80,
            300,
            70,
            "FÁCIL",
            "#3FD98E",
            "#2FB975",
        )
        self.boton_normal = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 10,
            300,
            70,
            "NORMAL",
            "#FFD966",
            "#E6C458",
        )
        self.boton_dificil = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 100,
            300,
            70,
            "DIFÍCIL",
            "#FF5E6C",
            "#D94A56",
        )
        self.boton_dificultad_volver = Boton(
            ancho_ventana / 2 - 150,
            alto_ventana / 2 + 190,
            300,
            70,
            "VOLVER",
            "#6A7DFF",
            "#5665D6",
        )
        # ---------------------------------------------
        
        # Botones para la ventana de puntajes!
        self.boton_rejugar = Boton(
            ancho_ventana / 2 - 150,
            450, # Posición base (será ajustada)
            300,
            70,
            "REJUGAR",
            "#3FD98E",
            "#2FB975",
        )
        self.boton_volver_menu = Boton(
            ancho_ventana / 2 - 150,
            550, # Posición base (será ajustada)
            300,
            70,
            "VOLVER AL MENÚ",
            "#6A7DFF",
            "#5665D6",
        )


    def reproducir_musica(self, archivo, loop=True):
        # Intenta cargar y reproducir el archivo de música
        try:
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.load(archivo)
            pygame.mixer.music.play(-1 if loop else 0)
            self.musica_urgente_activa = False # Se resetea al poner una nueva canción
        except pygame.error as e:
            # Imprime error si no se encuentra el archivo, por si acaso (┬┬﹏┬┬)
            print(f"Error al cargar la música '{archivo}': {e}")
            pass

    def cambiar_a_musica_urgente(self, archivo):
        # Solo reproduce la música de emergencia si no está ya activa
        if not self.musica_urgente_activa:
            try:
                # Detiene la música actual de forma segura antes de cargar la urgente
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                    
                pygame.mixer.music.load(archivo)
                pygame.mixer.music.play(-1)
                self.musica_urgente_activa = True
            except:
                pass

    def cambiar_estado(self, nuevo_estado):
        # Define si se debe detener la música al cambiar de estado
        detener_musica = True
        
        # Guarda el estado actual (antes de cambiar) para la lógica de música
        estado_previo = self.estado 

        #Excepciones: Continuidad de la Música de Menú
        
        # No detener si se pasa del menú a selección de modo
        if estado_previo == "menu" and nuevo_estado == "seleccion_modo":
            detener_musica = False
        # No detener si se pasa de selección de modo a registro o selección de dificultad
        elif estado_previo == "seleccion_modo" and nuevo_estado in ["registro", "seleccion_dificultad"]:
            detener_musica = False
        # No detener si se pasa de registro o selección de modo a menú 
        elif nuevo_estado == "menu" and estado_previo in ["seleccion_modo", "registro", "puntajes", "seleccion_dificultad"]:
            detener_musica = False
        # No detener si se va de la pantalla de registro/seleccion/menu al menú de puntajes
        elif nuevo_estado == "puntajes" and estado_previo in ["menu", "seleccion_modo", "registro", "seleccion_dificultad"]:
            detener_musica = False
        # No detener si se da "volver" desde la seleccion_dificultad 
        elif estado_previo == "seleccion_dificultad" and nuevo_estado in ["menu", "seleccion_modo", "registro", "seleccion_dificultad"]:
            detener_musica = False
        elif estado_previo in ["registro", "seleccion_dificultad"] and nuevo_estado in ["menu", "seleccion_modo", "registro", "seleccion_dificultad"]:
            detener_musica = False
        
        #Detener la música si se requiere (principalmente al entrar a modo de juego)
        if detener_musica and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.musica_urgente_activa = False

        self.estado = nuevo_estado
    
        #musica segun estado:

        if nuevo_estado == "menu":
            # Solo reproduce si la música fue detenida (viene de un modo de juego) 
            # o si no está sonando nada. Si vino de puntajes/seleccion_modo, no la reinicia.
            if detener_musica or not pygame.mixer.music.get_busy():
                self.reproducir_musica(self.sonido_menu)
    
        elif nuevo_estado == "modo1":  # Modo ESCAPA
            self.reproducir_musica(self.sonido_escapa_normal)
    
        elif nuevo_estado == "modo2":  # Modo CAZADOR
            self.reproducir_musica(self.sonido_cazador_normal)

        elif nuevo_estado == "puntajes":
            # Si viene de un modo de juego, la música fue detenida y debe iniciar la del menú.
            if estado_previo in ["modo1", "modo2"]:
                self.reproducir_musica(self.sonido_menu)

    def aplicar_dificultad(self):
        """Ajusta las variables del juego según la dificultad elegida."""
        # Configuración por defecto (Fácil)
        velocidad_enemigo_base = 0.05
        prob_random_enemigo = 0.1
        tiempo_limite_base = 60
        num_enemigos_escapa = 4
        num_enemigos_cazador = 4
        
        if self.dificultad == 1: # FÁCIL
            self.jugador.velocidad_normal = 0.15
            self.jugador.velocidad_correr = 0.25
            self.jugador.consumo_energia = 0.8
            self.jugador.recuperacion_energia = 0.5
            
            self.tiempo_limite = tiempo_limite_base + 30
            self.num_enemigos = num_enemigos_escapa if self.modo_juego == 1 else num_enemigos_cazador
            
        elif self.dificultad == 2: # NORMAL
            self.jugador.velocidad_normal = 0.12
            self.jugador.velocidad_correr = 0.20
            self.jugador.consumo_energia = 1.0
            self.jugador.recuperacion_energia = 0.4
            
            velocidad_enemigo_base = 0.07 
            
            self.tiempo_limite = tiempo_limite_base
            self.num_enemigos = num_enemigos_escapa + 2 if self.modo_juego == 1 else num_enemigos_cazador + 2
            
        elif self.dificultad == 3: # DIFÍCIL
            self.jugador.velocidad_normal = 0.10
            self.jugador.velocidad_correr = 0.15
            self.jugador.consumo_energia = 1.5
            self.jugador.recuperacion_energia = 0.2
            
            velocidad_enemigo_base = 0.10 
            prob_random_enemigo = 0.05 # Menos aleatorio = más "inteligente"
            
            self.tiempo_limite = tiempo_limite_base - 10
            self.num_enemigos = num_enemigos_escapa + 3 if self.modo_juego == 1 else num_enemigos_cazador + 3

        # Aplica velocidad y comportamiento a los enemigos actuales
        for enemigo in self.enemigos:
            enemigo.velocidad = velocidad_enemigo_base
            enemigo.cambio_cada = random.randint(30, 90) 
            
    def reiniciar_juego(self):
        # reinicia todo para comenzar una nueva partida
        self.mapa = Mapa(ancho_mapa, alto_mapa)
        self.jugador = Jugador(1.5, 1.5)
        self.enemigos = []
        self.trampas = []
        self.trampa_cooldown = 0
        self.tiempo_inicio = time.time()
        # self.tiempo_limite y self.num_enemigos se definen en aplicar_dificultad
        self.puntos = 0
        self.enemigos_escapados = 0
        self.musica_urgente_activa = False # Se resetea al iniciar
        self.mostrar_rejugar = False # Se reinicia aquí también, aunque se sobrescribirá si el juego termina.

        # PRIMERO: Aplica la dificultad para configurar variables de jugador y enemigos
        self.aplicar_dificultad()

        # SEGUNDO: crea enemigos usando el número ajustado por dificultad
        for _ in range(self.num_enemigos):
            self.generar_enemigo()
            
        # TERCERO: Vuelve a aplicar la dificultad a los nuevos enemigos creados
        self.aplicar_dificultad()


    def generar_enemigo(self):
        """
        elige una posición válida del mapa para colocar un enemigo,
        evitando que aparezca demasiado cerca del jugador o de la salida
        """
        intentos = 0
        MIN_DIST_JUGADOR = 8 
        MIN_DIST_SALIDA = 12 
        salida_x = ancho_mapa - 2
        salida_y = alto_mapa - 2

        while intentos < 200:
            x = random.randint(3, ancho_mapa - 4)
            y = random.randint(3, alto_mapa - 4)
            casilla = self.mapa.matriz[y][x]
            
            # distancia en pasos (solo sumas, no diagonal)
            dist_jugador = abs(x - self.jugador.x) + abs(y - self.jugador.y)
            dist_salida = abs(x - salida_x) + abs(y - salida_y)
            
            # debe caer sobre un camino y estar lo suficientemente lejos
            if (
                casilla.tipo == camino
                and dist_jugador > MIN_DIST_JUGADOR
                and dist_salida > MIN_DIST_SALIDA
            ):
                # se crea el enemigo justo al centro de la casilla
                self.enemigos.append(Enemigo(x + 0.5, y + 0.5))
                return
            intentos += 1

    def cargar_puntajes(self):
        # lee el archivo de puntajes, si no existe crea una estructura vacía
        try:
            with open("puntajes.json", "r") as f:
                return json.load(f)
        except:
            return {"modo1": [], "modo2": []}

    def guardar_puntajes(self):
        # guarda el estado actual de los mejores puntajes
        with open("puntajes.json", "w") as f:
            json.dump(self.puntajes, f)

    def agregar_puntaje(self, modo, puntos):
        # agrega un nuevo puntaje a la lista del modo seleccionado
        #bonificación por dificultad para el puntaje final
        if self.dificultad == 1:
            multiplicador = 0.8 # Menos puntos por jugar fácil
        elif self.dificultad == 2:
            multiplicador = 1.0
        else:
            multiplicador = 1.2 # Más puntos por jugar difícil
            
        puntos_finales = int(puntos * multiplicador)

        entrada = {
            "nombre": f"{self.nombre_jugador}  ({self.dificultad})", # Se añade la dificultad al nombre
            "puntos": puntos_finales,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }

        lista = self.puntajes[f"modo{modo}"]
        lista.append(entrada)

        # ordena para dejar arriba los mejores puntajes
        lista.sort(key=lambda x: x["puntos"], reverse=True)

        # se guardan solo los mejores 5
        self.puntajes[f"modo{modo}"] = lista[:5]
        self.guardar_puntajes()

    def dibujar_texto(self, texto, x, y, fuente=None, color=None):
        # dibuja cualquier texto en pantalla de forma centralizada
        if fuente is None:
            fuente = fuente1
        if color is None:
            color = negro
        superficie = fuente.render(texto, True, color)
        self.pantalla.blit(superficie, (x, y))

    def dibujar_menu(self):
        """pinta la pantalla del menú principal"""
        self.pantalla.fill(fondo_menu)
        # si el logo está disponible lo muestra, si no usa texto, medida de seguridad (┬┬﹏┬┬)
        if self.logo_grande:
            logo_rect = self.logo_grande.get_rect(
                center=(ancho_ventana / 2, (alto_ventana / 2) - 200)
            )
            self.pantalla.blit(self.logo_grande, logo_rect)
        else:
            self.dibujar_texto("JUEGO ESCAPA/CAZADOR", 200, 150, fuente1, blanco)

        # dibuja los botones principales
        self.boton_jugar.draw(self.pantalla, fuente_boton)
        self.boton_puntajes.draw(self.pantalla, fuente_boton)
        self.boton_salir.draw(self.pantalla, fuente_boton)

    def dibujar_seleccion_modo(self):
        # muestra la pantalla donde se elige el modo de juego
        self.pantalla.fill(fondo_menu)
        self.dibujar_texto(
            "SELECCIONA MODO DE JUEGO", 230, 150, fuente1, blanco
        )
        self.boton_escapa.draw(self.pantalla, fuente_boton)
        self.boton_cazador.draw(self.pantalla, fuente_boton)
        self.boton_volver.draw(self.pantalla, fuente_boton)
        
    def dibujar_seleccion_dificultad(self):
        # Muestra la pantalla donde se elige la dificultad
        self.pantalla.fill(fondo_menu)
        self.dibujar_texto(
            "SELECCIONA DIFICULTAD", 280, 150, fuente1, blanco
        )
        
        # Dibuja los botones de dificultad
        self.boton_facil.draw(self.pantalla, fuente_boton)
        self.boton_normal.draw(self.pantalla, fuente_boton)
        self.boton_dificil.draw(self.pantalla, fuente_boton)
        self.boton_dificultad_volver.draw(self.pantalla, fuente_boton)

    def dibujar_registro(self):
        # pantalla donde el jugador escribe su nombre
        self.pantalla.fill(fondo_menu)
        # Muestra el modo y dificultad seleccionados
        modo_texto = "ESCAPA" if self.modo_juego == 1 else "CAZADOR"
        dificultad_mapa = {1: "FÁCIL", 2: "NORMAL", 3: "DIFÍCIL"}
        dificultad_texto = dificultad_mapa.get(self.dificultad, "NORMAL")
        self.dibujar_texto(f"Modo: {modo_texto} ({dificultad_texto})", 340, 150, fuente_pequeña, amarillo)
        
        self.dibujar_texto("Ingresa tu nombre:", 340, 250, fuente1, blanco)

        # cuadro donde se escribe el nombre
        caja_texto = pygame.Rect(300, 320, 400, 60)
        pygame.draw.rect(self.pantalla, blanco, caja_texto, border_radius=10)
        pygame.draw.rect(self.pantalla, "#3FD98E", caja_texto, 3, border_radius=10)

        self.dibujar_texto(self.nombre_jugador, 320, 335, fuente_input, negro)

        self.dibujar_texto(
            "Presiona ENTER para comenzar", 360, 450, fuente_pequeña, blanco
        )
        self.dibujar_texto("ESC para volver", 430, 490, fuente_pequeña, blanco)

    def dibujar_juego(self):
        self.pantalla.fill(negro)

        # dibuja el mapa completo con su desplazamiento
        self.mapa.dibujar(self.pantalla, self.offset_x, self.offset_y)

        # dibuja las trampas activas
        for trampa in self.trampas:
            trampa.dibujar(self.pantalla, self.offset_x, self.offset_y)

        # dibuja todos los enemigos actuales
        for enemigo in self.enemigos:
            enemigo.dibujar(self.pantalla, self.offset_x, self.offset_y)

        # dibuja al jugador
        self.jugador.dibujar(self.pantalla, self.offset_x, self.offset_y)

        # calcula el tiempo que queda antes de que acabe la partida
        tiempo_transcurrido = int(time.time() - self.tiempo_inicio)
        tiempo_restante = self.tiempo_limite - tiempo_transcurrido
        if tiempo_restante < 0:
            tiempo_restante = 0
        self.dibujar_texto(f"Tiempo: {tiempo_restante}s", 830, 20, fuente_pequeña, blanco)

        #musica cuando se va acabando el tiempo
        if tiempo_restante <= 15:
            if not self.musica_urgente_activa:
                if self.modo_juego == 1:
                    self.cambiar_a_musica_urgente(self.sonido_escapa_urgente)
                elif self.modo_juego == 2:
                    self.cambiar_a_musica_urgente(self.sonido_cazador_urgente)
        
        #REGRESO A MÚSICA NORMAL 
        else:
            if self.musica_urgente_activa:
                if self.modo_juego == 1:
                    self.reproducir_musica(self.sonido_escapa_normal)
                elif self.modo_juego == 2:
                    self.reproducir_musica(self.sonido_cazador_normal)

        # muestra los puntos actuales
        self.dibujar_texto(f"Puntos: {self.puntos}", 830, 50, fuente_pequeña, blanco)

        # barra de energía del jugador
        pygame.draw.rect(self.pantalla, rojo, (50, 620, 200, 20))
        pygame.draw.rect(
            self.pantalla,
            verde_jugador,
            (50, 620, int(200 * self.jugador.energia / 100), 20),
        )
        self.dibujar_texto("Energia", 50, 650, fuente_pequeña, blanco)

        # información adicional según el modo
        if self.modo_juego == 1:
            # en modo escapa, se muestran trampas restantes
            self.dibujar_texto(
                f"Trampas: {self.max_trampas - len(self.trampas)}/3",
                830,
                80,
                fuente_pequeña,
                blanco,
            )
        else:
            # en modo cazador, se muestra cuántos enemigos lograron huir
            self.dibujar_texto(
                f"Escapados: {self.enemigos_escapados}",
                830,
                80,
                fuente_pequeña,
                blanco,
            )

        # Controles del juego
        self.dibujar_texto(
            "WASD/Flechas: Mover | Shift: Correr",
            260,
            650,
            fuente_pequeña,
            blanco,
        )
        if self.modo_juego == 1:
            self.dibujar_texto("Espacio: Trampa", 650, 650, fuente_pequeña, blanco)


    def dibujar_puntajes(self):
        self.pantalla.fill(fondo_menu)

        # pantalla principal del top de puntajes
        self.dibujar_texto("TOP 5 PUNTAJES", 320, 50, fuente1, blanco)

        # puntajes modo escapa
        self.dibujar_texto("Modo Escapa:", 150, 150, fuente_pequeña, "#3FD98E")
        for i, entrada in enumerate(self.puntajes["modo1"]):
            texto = f"{i+1}. {entrada['nombre']}: {entrada['puntos']} pts"
            self.dibujar_texto(texto, 150, 180 + i * 30, fuente_pequeña, blanco)

        # puntajes modo cazador
        self.dibujar_texto("Modo Cazador:", 550, 150, fuente_pequeña, "#FF5E6C")
        for i, entrada in enumerate(self.puntajes["modo2"]):
            texto = f"{i+1}. {entrada['nombre']}: {entrada['puntos']} pts"
            self.dibujar_texto(texto, 550, 180 + i * 30, fuente_pequeña, blanco)

        # POSICION DE BOTONES!
        # Posición base de los botones
        y_rejugar = 450
        y_menu = 550
        
        if not self.mostrar_rejugar:
            # Si NO se puede rejugar, subimos el botón "VOLVER AL MENÚ"
            y_menu = 450 
        
        # Dibujar botón REJUGAR (Solo si se activó la bandera para que no salga cuando no se ha jugado previamente jsjs)
        if self.mostrar_rejugar:
            self.boton_rejugar.rect.y = y_rejugar
            self.boton_rejugar.draw(self.pantalla, fuente_boton)
            
        # Dibujar botón VOLVER AL MENÚ
        self.boton_volver_menu.rect.y = y_menu
        self.boton_volver_menu.draw(self.pantalla, fuente_boton)

    def actualizar_juego(self):
        tiempo_actual = time.time()
        # Recorremos una copia de la lista para poder modificarla (eliminar enemigos)
        for enemigo in self.enemigos[:]:
            # Este bloque asegura que un enemigo recién atrapado sea eliminado y reemplazado.
            if enemigo.muerto:
                if enemigo in self.enemigos:
                    self.enemigos.remove(enemigo)
                    self.generar_enemigo()
                continue

            enemigo.mover(
                self.jugador, self.mapa.matriz, self.modo_juego
            )

            # distancia para verificar colisión entre jugador y enemigo
            distancia = (
                (enemigo.x - self.jugador.x) ** 2
                + (enemigo.y - self.jugador.y) ** 2
            ) ** 0.5

            # si hay colisión
            if distancia < 0.7:
                if self.modo_juego == 1:
                    # Si atrapan al jugador el puntaje siempre = 0 (me parece mejor por como manejamos el puntaje, antes si se atrapaba muy antes dejaba un puntaje muy alto)
                    self.puntos = 0
                    self.agregar_puntaje(1, self.puntos)
                    self.mostrar_rejugar = True
                    self.cambiar_estado("puntajes")
                    return
                else:
                    # modo cazador: jugador atrapa enemigo
                    self.puntos += 100
                    self.enemigos.remove(enemigo)
                    self.generar_enemigo()
                    # Se re-aplica la dificultad para el nuevo enemigo generado
                    self.aplicar_dificultad() 
                    continue

            # si estamos en modo cazador, revisamos si el enemigo llegó a la salida
            if self.modo_juego == 2:
                # Verificación de que el centro del enemigo está en la celda de salida
                if self.mapa.matriz[int(enemigo.y)][int(enemigo.x)].tipo == salida:
                    self.puntos = max(0, self.puntos - 50)
                    self.enemigos_escapados += 1
                    self.enemigos.remove(enemigo)
                    self.generar_enemigo()
                    # Se re-aplica la dificultad para el nuevo enemigo generado
                    self.aplicar_dificultad() 
                    continue

            # LÓGICA DE TRAMPA CORREGIDA
            enemigo_atrapado = False
            for trampa in self.trampas[:]:
                # Colisión: compara la posición central del enemigo con la posición central de la trampa
                if abs(enemigo.x - (trampa.x + 0.5)) < 0.7 and abs(enemigo.y - (trampa.y + 0.5)) < 0.7:
                    
                    # Elimina el enemigo y lo reemplaza (lo hace "desaparecer")
                    if enemigo in self.enemigos:
                        self.enemigos.remove(enemigo)
                        self.generar_enemigo()
                        # Se re-aplica la dificultad para el nuevo enemigo generado
                        self.aplicar_dificultad() 
                    
                    # Elimina la trampa
                    self.trampas.remove(trampa)
                    self.puntos += 50
                    enemigo_atrapado = True
                    break

            if enemigo_atrapado:
                continue
            
        # verificar si el jugador llegó a la salida en modo escapa
        if self.modo_juego == 1:
            if self.mapa.matriz[int(self.jugador.y)][int(self.jugador.x)].tipo == salida:
                # se calcula el puntaje final según tiempo y enemigos restantes
                tiempo_total = int(time.time() - self.tiempo_inicio)
                self.puntos += max(0, 10000 - tiempo_total * 10 + len(self.enemigos) * 500)
                self.agregar_puntaje(1, self.puntos)
                self.mostrar_rejugar = True #FIN DE PARTIDA: SE ACTIVA REJUGAR
                self.cambiar_estado("puntajes")
                return

        # manejo del tiempo límite del nivel
        tiempo_restante = self.tiempo_limite - int(time.time() - self.tiempo_inicio)
        if tiempo_restante <= 0:
            # se guarda puntaje según modo y se termina la partida
            if self.modo_juego == 1:
                self.agregar_puntaje(1, self.puntos)
            else:
                self.agregar_puntaje(2, self.puntos)
            self.mostrar_rejugar = True #FIN DE PARTIDA: SE ACTIVA REJUGAR
            self.cambiar_estado("puntajes")
            return
        
    def ejecutar(self):
        ejecutando = True
        while ejecutando:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    ejecutando = False

                # manejo del menú principal: botones de jugar, puntajes y salir
                if self.estado == "menu":
                    if self.boton_jugar.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        # Pasa a escoger el modo de juego (la música del menú continúa)
                        self.cambiar_estado("seleccion_modo")
                    elif self.boton_puntajes.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        self.mostrar_rejugar = False #ACCESO DESDE MENÚ: SE DESACTIVA REJUGAR
                        # La música del menú continúa por la nueva excepción en cambiar_estado
                        self.cambiar_estado("puntajes")
                    elif self.boton_salir.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        ejecutando = False
                
                # menú donde se escoge entre modo escapa o modo cazador
                elif self.estado == "seleccion_modo":
                    if self.boton_escapa.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        self.modo_juego = 1
                        # Pasa a selección de dificultad
                        self.cambiar_estado("seleccion_dificultad")
                    elif self.boton_cazador.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        self.modo_juego = 2
                        # Pasa a selección de dificultad
                        self.cambiar_estado("seleccion_dificultad")
                    elif self.boton_volver.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        self.cambiar_estado("menu")
                
                # Menú de selección de dificultad
                elif self.estado == "seleccion_dificultad":
                    if self.boton_facil.clicked(evento):
                        if self.sonido_click: self.sonido_click.play()
                        self.dificultad = 1
                        self.cambiar_estado("registro")
                    elif self.boton_normal.clicked(evento):
                        if self.sonido_click: self.sonido_click.play()
                        self.dificultad = 2
                        self.cambiar_estado("registro")
                    elif self.boton_dificil.clicked(evento):
                        if self.sonido_click: self.sonido_click.play()
                        self.dificultad = 3
                        self.cambiar_estado("registro")
                    elif self.boton_dificultad_volver.clicked(evento):
                        if self.sonido_click: self.sonido_click.play()
                        self.dificultad = 1 # Se resetea a fácil por defecto
                        self.cambiar_estado("seleccion_modo")
                
                # --- MANEJO DE BOTONES EN PANTALLA DE PUNTAJES ---
                elif self.estado == "puntajes":
                    if self.mostrar_rejugar and self.boton_rejugar.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        # Reinicia la partida con el mismo nombre y modo
                        self.reiniciar_juego()
                        self.cambiar_estado(f"modo{self.modo_juego}")
                    elif self.boton_volver_menu.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        # Vuelve al menú principal
                        self.cambiar_estado("menu")

                # manejo del teclado
                if evento.type == pygame.KEYDOWN:
                    # pantalla para ingresar nombre
                    if self.estado == "registro":
                        # enter: empieza la partida si ya escribió nombre
                        if evento.key == pygame.K_RETURN and len(self.nombre_jugador) > 0:
                            self.reiniciar_juego()
                            # Aquí sí se detiene la música del menú y se inicia la del juego
                            self.cambiar_estado(f"modo{self.modo_juego}")

                        # borrar último carácter
                        elif evento.key == pygame.K_BACKSPACE:
                            self.nombre_jugador = self.nombre_jugador[:-1]

                        # volver atrás
                        elif evento.key == pygame.K_ESCAPE:
                            self.cambiar_estado("seleccion_dificultad")
                            self.nombre_jugador = ""

                        # escribir caracteres válidos (máx 15)
                        elif len(self.nombre_jugador) < 15 and evento.unicode.isprintable():
                            self.nombre_jugador += evento.unicode

                    # desde la pantalla de puntajes puede volver al menú (por si presionan ESC)
                    elif self.estado == "puntajes":
                        if evento.key == pygame.K_ESCAPE:
                            self.cambiar_estado("menu")

            # si el juego está activo (modo 1 o modo 2)
            if self.estado in ["modo1", "modo2"]:
                keys = pygame.key.get_pressed()

                # correr si mantiene shift y tiene energía
                if keys[pygame.K_LSHIFT] and self.jugador.energia > 0:
                    self.jugador.corriendo = True
                    velocidad = self.jugador.velocidad_correr
                else:
                    self.jugador.corriendo = False
                    velocidad = self.jugador.velocidad_normal

                # guarda la posición por si necesita revertirla
                pos_anterior_x = self.jugador.x
                pos_anterior_y = self.jugador.y

                # movimiento básico del jugador.
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    self.jugador.mover(-velocidad, 0, self.mapa.matriz, self.modo_juego)
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    self.jugador.mover(velocidad, 0, self.mapa.matriz, self.modo_juego)
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    self.jugador.mover(0, -velocidad, self.mapa.matriz, self.modo_juego)
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    self.jugador.mover(0, velocidad, self.mapa.matriz, self.modo_juego)

                # en modo cazador no puede retroceder dentro de la salida
                if self.modo_juego == 2:
                    if self.mapa.matriz[int(self.jugador.y)][int(self.jugador.x)].tipo == salida:
                        self.jugador.x = pos_anterior_x
                        self.jugador.y = pos_anterior_y

                # baja energía si corre
                self.jugador.actualizar_energia()

                # colocar trampa (solo modo 1)
                if keys[pygame.K_SPACE] and self.modo_juego == 1:
                    tiempo_actual = time.time()
                    # Cooldown de 2 segundos (Modificación anterior)
                    if len(self.trampas) < self.max_trampas and tiempo_actual - self.trampa_cooldown >= 2: 
                        self.trampas.append(Trampa(int(self.jugador.x), int(self.jugador.y)))
                        self.trampa_cooldown = tiempo_actual

                # actualiza enemigos, puntos y lógica del juego
                self.actualizar_juego()

            # dibujo de pantallas según el estado actual
            if self.estado == "menu":
                self.dibujar_menu()
            elif self.estado == "seleccion_modo":
                self.dibujar_seleccion_modo()
            elif self.estado == "seleccion_dificultad":
                self.dibujar_seleccion_dificultad()
            elif self.estado == "registro":
                self.dibujar_registro()
            elif self.estado in ["modo1", "modo2"]:
                self.dibujar_juego()
            elif self.estado == "puntajes":
                self.dibujar_puntajes()

            # refresca pantalla
            pygame.display.flip()
            self.reloj.tick(fps)

        pygame.quit()

if __name__ == "__main__":
    juego = Juego()
    juego.ejecutar()