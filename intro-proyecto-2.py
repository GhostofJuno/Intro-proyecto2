import pygame
import random

pygame.init()

# Constantes
fondo_menu = "#12382C"
ancho_ventana = 1000
alto_ventana = 700
ancho_mapa = 25
alto_mapa = 20
tamanio_celda = 30
fps = 60
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
                            tamanio_celda, tamanio_celda), 1) #a usted no le molesta que salga roja la identacion? a mi si jajsj


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
        # dibuja la casilla y coloca la letra 'E' al centro para marcar la salida  #pq "E"? de "escape"?
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

class Boton: #yo no voy a estar haciendo los botones uno por uno ~_~
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
        
    def mover(self, dx, dy, mapa):
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
            if not mapa[int(ey)][int(ex)].puede_pasar_jugador(): #revisa tipo de casilla
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
    
    def dibujar(self, pantalla, offset_x, offset_y):#TODO: lo podemos cambiar luego, si quieras un bichito o lo dejamos como bolita, cuando lo corramos vemos :3
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

# JUNOO, lo que hce fue compltar más y acomodarlo, las funciones de la interfaz las ponemos luego para mantener el ordeen ✌️✌️  #okss

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
            # 1. Toma la celda actual de la cima de la pila
            y, x = pila[-1] 
            
            # 2. Encuentra vecinos no visitados
            vecinos_validos = []
            random.shuffle(direcciones) # Orden aleatorio para evitar patrones
            
            for dy, dx in direcciones:
                ny, nx = y + dy, x + dx
                
                # Revisa los límites
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
                # 4. Si no hay vecinos, hace vuelve a la celda anterior
                pila.pop() 

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

        # coloca túneles para el jugador en posiciones válidas
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
        self.matriz[self.alto - 2][self.ancho - 2] = Salida(self.ancho - 2, self.alto - 2)

    def dibujar(self, pantalla, offset_x, offset_y):
        # recorre toda la matriz y dibuja cada casilla según su tipo :3333
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

        # carga imágenes y sonidos, si fallan el juego sigue funcionando
        try:
            self.logo = pygame.image.load("oneway.png")
            self.logo_grande = pygame.transform.scale(self.logo, (400, 230))
            self.sonido_click = pygame.mixer.Sound("pop.wav")
            self.sonido_click.set_volume(0.6)
        except:
            self.logo_grande = None
            self.sonido_click = None

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
# perdón, se me había olvidado subirlo. Por si acaso, faltan algunas cosillas que estoy terminando :))



