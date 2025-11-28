#mari a mi esto ya me corre al 100, confirmalo si puedes. No se te olvide descargarle las cosas que subi
#voy a ver si puedo cambiarle cosas del funcionamiento luego, esa gente actua rarillo
import pygame
import random
import json
import time 
from datetime import datetime #esto es para los puntajes tmb ya habia puesto el archivo :3

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

# La inicialización de fuentes debe ir después de pygame.init()
fuente1 = pygame.font.SysFont("Arial", 48)
fuente_boton = pygame.font.SysFont("Arial", 40)
fuente_pequeña = pygame.font.SysFont("Arial", 24)
fuente_input = pygame.font.SysFont("Arial", 32)

# Colores
negro          = "#000000"
blanco         = "#FFFFFF"
gris_oscuro    = "#323232"
verde_liana    = "#228B22"
verde          = "#3B5431"
azul_tunel     = "#6495ED"
azul_oscuro    = "#251870"
rojo           = "#FF0000"
verde_jugador  = "#00FF00"
amarillo       = "#FFFF00"
naranja        = "#FFA500"

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
            
            # Lógica especial de paso para el jugador (Modo Escapa 1)
            # En modo Escapa, el jugador NO puede pasar por Lianas (actúan como Muro)
            if modo_juego == 1 and casilla.tipo == liana:
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
        pygame.draw.circle(pantalla, verde_jugador,  
                          (int(self.x * tamanio_celda + tamanio_celda/2 + offset_x), #x del circulo
                           int(self.y * tamanio_celda + tamanio_celda/2 + offset_y)), #y del circulo
                            int(tamanio_celda/2.5)) #radio
class Enemigo:
    def __init__(self, x, y):
        # posición como float para permitir movimiento suave
        self.x = float(x)
        self.y = float(y)

        # velocidad base del enemigo
        self.velocidad = 0.05

        # dirección inicial elegida al azar
        self.dir_x, self.dir_y = random.choice(
            [(1, 0), (-1, 0), (0, 1), (0, -1)]
        )

        # probabilidad de moverse aleatoriamente para evitar rutas predecibles
        self.prob_random = 0.1 

        # control de cada cuántos frames puede cambiar dirección
        self.frames_desde_cambio = 0
        self.cambio_cada = random.randint(10, 30)

        # estado de muerte y respawn
        self.muerto = False
        self.tiempo_muerte = 0
        self.tiempo_respawn = 10

    def _puede_moverse_a_pos(self, nx, ny, mapa, modo_juego):
        # si sale del mapa, movimiento bloqueado
        if not (0 <= int(nx) < ancho_mapa and 0 <= int(ny) < alto_mapa):
            return False
            
        casilla = mapa[int(ny)][int(nx)]
        
        # muros siempre bloquean
        if casilla.tipo == muro:
            return False

        # túneles solo permitidos si el enemigo es "escaper"
        if casilla.tipo == tunel and modo_juego == 1:
            return False
        
        # lianas solo permitidas si el enemigo es "cazador"
        if casilla.tipo == liana and modo_juego == 2:
            return False
            
        return True

    def _direcciones_validas(self, mapa, modo_juego):
        # devuelve una lista de direcciones posibles según el tipo de casilla
        dirs = []
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx_celda = int(self.x + dx)
            ny_celda = int(self.y + dy)
            
            # fuera del mapa se ignora
            if not (0 <= nx_celda < ancho_mapa and 0 <= ny_celda < alto_mapa):
                continue

            casilla = mapa[ny_celda][nx_celda]
                
            # misma lógica de bloqueo usada en el movimiento
            if casilla.tipo == muro:
                continue            
            if casilla.tipo == tunel and modo_juego == 1:
                continue           
            if casilla.tipo == liana and modo_juego == 2:
                continue

            dirs.append((dx, dy))

        return dirs

    def _escoger_direccion_hacia(self, objetivo_x, objetivo_y, mapa, modo_juego, amenaza_x=None, amenaza_y=None):
        # obtiene direcciones que cumplen reglas del mapa y del rol
        dirs_validas = self._direcciones_validas(mapa, modo_juego) 
        if not dirs_validas:
            return

        # ocasionalmente se mueve al azar para crear comportamiento menos predecible
        if random.random() < self.prob_random:
            self.dir_x, self.dir_y = random.choice(dirs_validas)
            return

        # modo 1: el enemigo es cazador y persigue al jugador
        if modo_juego == 1: 
            # calcula la distancia al jugador para decidir la dirección
            vx = objetivo_x - self.x
            vy = objetivo_y - self.y

            # intenta priorizar el eje con mayor diferencia
            mover_horizontal = abs(vx) > abs(vy)
            preferidas = []

            # crea una lista ordenada de direcciones preferidas
            if mover_horizontal:
                preferidas.append((1, 0) if vx > 0 else (-1, 0))
                preferidas.append((0, 1) if vy > 0 else (0, -1))
            else:
                preferidas.append((0, 1) if vy > 0 else (0, -1))
                preferidas.append((1, 0) if vx > 0 else (-1, 0))

            # si una preferida es válida, la usa
            for d in preferidas:
                if d in dirs_validas:
                    self.dir_x, self.dir_y = d
                    return
            
            # si no, elige cualquiera válida para evitar quedarse trabado
            self.dir_x, self.dir_y = random.choice(dirs_validas)

        # modo 2: el enemigo es presa, huye del jugador y busca la salida
        elif modo_juego == 2: 
            best_score = -float('inf')
            best_dir = None
            
            # si no se pasó amenaza explícita, usa el jugador como amenaza
            if amenaza_x is None: 
                amenaza_x, amenaza_y = self.x, self.y

            # revisa cada dirección posible
            for dx, dy in dirs_validas:
                nx = self.x + dx
                ny = self.y + dy
                
                # heurística: prefiere alejarse de la amenaza y acercarse a la salida
                dist_a_objetivo = ((nx - objetivo_x)**2 + (ny - objetivo_y)**2)**0.5
                dist_a_amenaza = ((nx - amenaza_x)**2 + (ny - amenaza_y)**2)**0.5
                
                # peso mayor en huir para dar efecto "presa"
                score = dist_a_amenaza * 2.5 - dist_a_objetivo 

                if score > best_score:
                    best_score = score
                    best_dir = (dx, dy)
            
            # si encontró una dirección buena, la usa
            if best_dir:
                self.dir_x, self.dir_y = best_dir
            else:
                # si no, toma cualquier válida
                self.dir_x, self.dir_y = random.choice(dirs_validas)
    
    def mover_hacia(self, objetivo_x, objetivo_y, mapa, perseguir=True, modo_juego=1):
        # si está muerto, no se mueve
        if self.muerto:
            return

        amenaza_x, amenaza_y = None, None
        
        # modo 2: se convierte en presa y debe escapar hacia la salida
        if not perseguir and modo_juego == 2:
            # jugador es la amenaza
            amenaza_x, amenaza_y = objetivo_x, objetivo_y
            # salida siempre en la esquina final
            salida_x = ancho_mapa - 2
            salida_y = alto_mapa - 2
            # el objetivo del movimiento ahora es la salida
            objetivo_x, objetivo_y = salida_x + 0.5, salida_y + 0.5
        
        # controla cada cuántos frames reconsidera su dirección
        self.frames_desde_cambio += 1

        if self.frames_desde_cambio >= self.cambio_cada:
            self.frames_desde_cambio = 0
            self._escoger_direccion_hacia(objetivo_x, objetivo_y, mapa, modo_juego, amenaza_x, amenaza_y)

        # calcula la posición tentativa
        nx = self.x + self.dir_x * self.velocidad
        ny = self.y + self.dir_y * self.velocidad

        # se valida el movimiento considerando reglas del rol
        if self._puede_moverse_a_pos(nx, ny, mapa, modo_juego):
            self.x = nx
            self.y = ny
        else:
            # si choca, intenta cambiar a una dirección que sí pueda tomar
            dirs_validas = self._direcciones_validas(mapa, modo_juego)
            if dirs_validas:
                self.dir_x, self.dir_y = random.choice(dirs_validas)
            else:
                # si no hay salida posible, se queda quieto
                self.dir_x, self.dir_y = 0, 0

    def dibujar(self, pantalla, offset_x, offset_y):
        # dibuja el enemigo solo si no está muerto
        pygame.draw.circle(
            pantalla,
            rojo,
            (
                int(self.x * tamanio_celda + tamanio_celda / 2 + offset_x),
                int(self.y * tamanio_celda + tamanio_celda / 2 + offset_y),
            ),
            int(tamanio_celda / 2.5),
        )

    def actualizar(self, tiempo_actual):
        # revisa si ya pasó suficiente tiempo para revivir
        if self.muerto and tiempo_actual - self.tiempo_muerte >= self.tiempo_respawn:
            self.muerto = False
            return True
        return False


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

        # --- REEMPLAZO DE RECURSIÓN POR BACKTRACKING ITERATIVO ---
        
        # Inicializa la pila de celdas a visitar
        pila = [(1, 1)] 
        self.matriz[1][1] = Camino(1, 1) # Marca el inicio como camino
        
        # Direcciones de movimiento (pasos de 2)
        direcciones = [(-2, 0), (0, 2), (2, 0), (0, -2)]

        while pila:
            # 1. Toma la celda actual de la cima de la pila (backtracking)
            y, x = pila[-1] 
            
            # 2. Encuentra vecinos no visitados
            vecinos_validos = []
            random.shuffle(direcciones) # Orden aleatorio para evitar patrones
            
            for dy, dx in direcciones:
                ny, nx = y + dy, x + dx
                
                # Revisa límites
                if 1 <= ny < self.alto - 1 and 1 <= nx < self.ancho - 1:
                    # Revisa si la celda vecina es un Muro (no visitada)
                    if self.matriz[ny][nx].tipo == muro:
                        vecinos_validos.append((ny, nx, y + dy // 2, x + dx // 2))

            # 3. Si hay vecinos no visitados, avanza
            if vecinos_validos:
                # Elige el primer vecino (ya están en orden aleatorio)
                ny, nx, pared_y, pared_x = vecinos_validos[0] 
                
                # Abre la pared intermedia
                self.matriz[pared_y][pared_x] = Camino(pared_x, pared_y)
                
                # Convierte la nueva celda en camino y la añade a la pila
                self.matriz[ny][nx] = Camino(nx, ny)
                pila.append((ny, nx))
            else:
                # 4. Si no hay vecinos, hace 'backtrack' (vuelve a la celda anterior)
                pila.pop() 
                
        # ------------------- FIN DEL ALGORITMO ITERATIVO -------------------

        # intenta asegurar que haya al menos un camino hacia la salida
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
        self.mapa = None
        self.jugador = None
        self.enemigos = []
        self.trampas = []
        self.trampa_cooldown = 0   # evita poner trampas repetidamente
        self.max_trampas = 3
        self.tiempo_inicio = 0
        self.puntos = 0
        self.enemigos_escapados = 0
        self.offset_x = 50         # posiciona el mapa dentro de la ventana
        self.offset_y = 50
        
        # --- Nueva variable para control de música urgente ---
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

        # --- Modificación para cargar nombres de archivos de música ---
        self.sonido_menu = "onewaymenu.wav"
        self.sonido_escapa_normal = "oneWay.wav"
        self.sonido_escapa_urgente = "notime.wav"
        self.sonido_cazador_normal = "onthehunt.wav"
        self.sonido_cazador_urgente = "notimeforhunting.wav"
        # -------------------------------------------------------------

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

    def reproducir_musica(self, archivo, loop=True):
        # Intenta cargar y reproducir el archivo de música
        try:
            pygame.mixer.music.set_volume(0.6)
            pygame.mixer.music.load(archivo)
            pygame.mixer.music.play(-1 if loop else 0)
            self.musica_urgente_activa = False # Se resetea al poner una nueva canción
        except pygame.error as e:
            # Imprime error si no se encuentra el archivo
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
        # No detener si se pasa de selección de modo a registro
        elif estado_previo == "seleccion_modo" and nuevo_estado == "registro":
            detener_musica = False
        # No detener si se pasa de registro o selección de modo a menú 
        elif nuevo_estado == "menu" and estado_previo in ["seleccion_modo", "registro", "puntajes"]:
            detener_musica = False
        # No detener si se va de la pantalla de registro/seleccion/menu al menú de puntajes
        elif nuevo_estado == "puntajes" and estado_previo in ["menu", "seleccion_modo", "registro"]:
            detener_musica = False
        
        # --- Detener la música si se requiere (principalmente al entrar a modo de juego) ---
        if detener_musica and pygame.mixer.music.get_busy():
            pygame.mixer.music.stop()
            self.musica_urgente_activa = False

        self.estado = nuevo_estado
    
        # --- Lógica para INICIAR la Música según estado (se supone que cambia si hay poco tiempo)---

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

    def reiniciar_juego(self):
        # reinicia todo para comenzar una nueva partida
        self.mapa = Mapa(ancho_mapa, alto_mapa)
        self.jugador = Jugador(1.5, 1.5)
        self.enemigos = []
        self.trampas = []
        self.trampa_cooldown = 0
        self.tiempo_inicio = time.time()
        self.tiempo_limite = 60
        self.puntos = 0
        self.enemigos_escapados = 0
        self.musica_urgente_activa = False # Se resetea al iniciar

        # crea enemigos dependiendo del modo de juego
        num_enemigos = 3 if self.modo_juego == 1 else 2
        for _ in range(num_enemigos):
            self.generar_enemigo()

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
        entrada = {
            "nombre": self.nombre_jugador,
            "puntos": puntos,
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
        # si el logo está disponible lo muestra, si no usa texto
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

    def dibujar_registro(self):
        # pantalla donde el jugador escribe su nombre
        self.pantalla.fill(fondo_menu)
        self.dibujar_texto("Ingresa tu nombre:", 280, 250, fuente1, blanco)

        # cuadro donde se escribe el nombre
        caja_texto = pygame.Rect(300, 320, 400, 60)
        pygame.draw.rect(self.pantalla, blanco, caja_texto, border_radius=10)
        pygame.draw.rect(self.pantalla, "#3FD98E", caja_texto, 3, border_radius=10)

        self.dibujar_texto(self.nombre_jugador, 320, 335, fuente_input, negro)

        self.dibujar_texto(
            "Presiona ENTER para continuar", 250, 450, fuente_pequeña, blanco
        )
        self.dibujar_texto("ESC para volver", 380, 490, fuente_pequeña, blanco)

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
        self.dibujar_texto(f"Tiempo: {tiempo_restante}s", 800, 20, fuente_pequeña, blanco)

        # --- Lógica de música urgente (FIXED) ---
        # 1. MÚSICA URGENTE TEMPRANA (31 segundos transcurridos)
        # Si han pasado entre 31 y 50 segundos, activa la música urgente.
        if 31 <= tiempo_transcurrido <= 50:
            if not self.musica_urgente_activa:
                if self.modo_juego == 1:
                    self.cambiar_a_musica_urgente(self.sonido_escapa_urgente)
                elif self.modo_juego == 2:
                    self.cambiar_a_musica_urgente(self.sonido_cazador_urgente)
        
        # 2. MÚSICA URGENTE FINAL (10 segundos restantes)
        # Si quedan 10 segundos o menos, asegura que la música urgente esté activa.
        elif tiempo_restante <= 10:
            if not self.musica_urgente_activa:
                if self.modo_juego == 1:
                    self.cambiar_a_musica_urgente(self.sonido_escapa_urgente)
                elif self.modo_juego == 2:
                    self.cambiar_a_musica_urgente(self.sonido_cazador_urgente)
        
        # 3. REGRESO A MÚSICA NORMAL 
        # Si la música urgente está activa, pero el tiempo ha vuelto a una zona "segura", cambia a normal.
        else:
            if self.musica_urgente_activa:
                if self.modo_juego == 1:
                    self.reproducir_musica(self.sonido_escapa_normal)
                elif self.modo_juego == 2:
                    self.reproducir_musica(self.sonido_cazador_normal)
        # -------------------------------

        # muestra los puntos actuales
        self.dibujar_texto(f"Puntos: {self.puntos}", 800, 50, fuente_pequeña, blanco)

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
                800,
                80,
                fuente_pequeña,
                blanco,
            )
        else:
            # en modo cazador, se muestra cuántos enemigos lograron huir
            self.dibujar_texto(
                f"Escapados: {self.enemigos_escapados}",
                800,
                80,
                fuente_pequeña,
                blanco,
            )

        # controles del juego mostrados en pantalla
        self.dibujar_texto(
            "WASD/Flechas: Mover | Shift: Correr",
            260,
            670,
            fuente_pequeña,
            blanco,
        )
        if self.modo_juego == 1:
            self.dibujar_texto("Espacio: Trampa", 420, 650, fuente_pequeña, blanco)


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

        # mensaje para volver al menú
        self.dibujar_texto("Presiona ESC para volver", 320, 550, fuente_pequeña, blanco)


    def actualizar_juego(self):
        tiempo_actual = time.time()

        # actualiza el comportamiento de todos los enemigos uno por uno
        for enemigo in self.enemigos[:]:

            # si el enemigo está muerto, revisa si ya debe revivir
            if enemigo.muerto:
                if enemigo.actualizar(tiempo_actual):
                    # si revive, se genera uno nuevo y este se elimina
                    self.generar_enemigo()
                    self.enemigos.remove(enemigo)

            else:
                # movimiento según el modo
                if self.modo_juego == 1:
                    # modo escapa: el enemigo persigue al jugador
                    enemigo.mover_hacia(
                        self.jugador.x, self.jugador.y, self.mapa.matriz, True, self.modo_juego
                    )
                else:
                    # modo cazador: huye del jugador y busca la salida
                    enemigo.mover_hacia(
                        self.jugador.x, self.jugador.y, self.mapa.matriz, False, self.modo_juego
                    )

                # distancia para verificar colisión entre jugador y enemigo
                distancia = (
                    (enemigo.x - self.jugador.x) ** 2
                    + (enemigo.y - self.jugador.y) ** 2
                ) ** 0.5

                # si hay colisión
                if distancia < 0.7:
                    if self.modo_juego == 1:
                        # modo escapa: perder
                        tiempo_total = int(time.time() - self.tiempo_inicio)
                        # puntaje depende del tiempo que tardó el enemigo en atraparte
                        self.puntos += max(0, 10000 - tiempo_total * 10)
                        self.agregar_puntaje(1, self.puntos)
                        self.cambiar_estado("puntajes") # Usa la nueva función
                        return
                    else:
                        # modo cazador: jugador atrapa enemigo
                        self.puntos += 100
                        self.enemigos.remove(enemigo)
                        self.generar_enemigo()
                        continue

                # si estamos en modo cazador, revisamos si el enemigo llegó a la salida
                if self.modo_juego == 2:
                    if self.mapa.matriz[int(enemigo.y)][int(enemigo.x)].tipo == salida:
                        self.puntos = max(0, self.puntos - 50) #retorna el maximo, entonces nunca va a ser menor que 0, yupi!!
                        self.enemigos_escapados += 1
                        self.enemigos.remove(enemigo)
                        self.generar_enemigo()

                # revisa si el enemigo cayó en una trampa
                for trampa in self.trampas[:]:
                    if abs(enemigo.x - trampa.x) < 0.7 and abs(enemigo.y - trampa.y) < 0.7:
                        enemigo.muerto = True
                        enemigo.tiempo_muerte = tiempo_actual
                        self.trampas.remove(trampa)
                        self.puntos += 50

        # verificar si el jugador llegó a la salida en modo escapa
        if self.modo_juego == 1:
            if self.mapa.matriz[int(self.jugador.y)][int(self.jugador.x)].tipo == salida:
                # se calcula el puntaje final según tiempo y enemigos restantes
                tiempo_total = int(time.time() - self.tiempo_inicio)
                self.puntos += max(0, 10000 - tiempo_total * 10 + len(self.enemigos) * 500)
                self.agregar_puntaje(1, self.puntos)
                self.cambiar_estado("puntajes") # Usa la nueva función
                return

        # manejo del tiempo límite del nivel
        tiempo_restante = self.tiempo_limite - int(time.time() - self.tiempo_inicio)
        if tiempo_restante <= 0:
            # se guarda puntaje según modo y se termina la partida
            if self.modo_juego == 1:
                self.agregar_puntaje(1, self.puntos)
            else:
                self.agregar_puntaje(2, self.puntos)
            self.cambiar_estado("puntajes") # Usa la nueva función
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
                        # Pasa a pantalla para escribir nombre (la música del menú continúa)
                        self.cambiar_estado("registro")
                    elif self.boton_cazador.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
                        self.modo_juego = 2
                        self.cambiar_estado("registro")
                    elif self.boton_volver.clicked(evento):
                        if self.sonido_click:
                            self.sonido_click.play()
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
                            self.cambiar_estado("seleccion_modo")
                            self.nombre_jugador = ""

                        # escribir caracteres válidos (máx 15)
                        elif len(self.nombre_jugador) < 15 and evento.unicode.isprintable():
                            self.nombre_jugador += evento.unicode

                    # desde la pantalla de puntajes puede volver al menú
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
                    # limita trampas y tiene un tiempo de espera entre trampas
                    if len(self.trampas) < self.max_trampas and tiempo_actual - self.trampa_cooldown >= 5:
                        self.trampas.append(Trampa(int(self.jugador.x), int(self.jugador.y)))
                        self.trampa_cooldown = tiempo_actual

                # actualiza enemigos, puntos y lógica del juego
                self.actualizar_juego()

            # dibujo de pantallas según el estado actual
            if self.estado == "menu":
                self.dibujar_menu()
            elif self.estado == "seleccion_modo":
                self.dibujar_seleccion_modo()
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