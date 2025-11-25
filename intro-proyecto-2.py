import pygame

pygame.init()

# Constantes
ancho_ventana = 1000
alto_ventana = 700
ancho_mapa = 25
alto_mapa = 20
tamanio_celda = 30
fps = 60

#fuentes
fuente1 = pygame.font.Font(None,48)
fuente_boton = pygame.font.Font(None,40) #TODO: buscar fuentes bonitas ＞︿＜

# Colores (mari los cambie a hex por el cuadrito que sale, yo creo que es mas facil manejar los colores asi :-])
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

# INTERFAZ
pantalla = pygame.display.set_mode((ancho_ventana, alto_ventana))
pygame.display.set_caption("Proyecto de intro de Mari y Junn (❁´◡`❁)")

#IMAGENES
logo = pygame.image.load("oneway.png")
logo_grande = pygame.transform.scale(logo, (400, 230))
logo_rect = logo_grande.get_rect(center=(ancho_ventana/2, (alto_ventana/2)-200))

#SONIDO
sonido_click = pygame.mixer.Sound("pop.wav")
sonido_click.set_volume(0.6)

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
        self.x = float(x)
        self.y = float(y)
        self.velocidad = 0.04
        self.path = []
        self.muerto = False
        self.tiempo_muerte = 0
        self.tiempo_respawn = 10

#TODO: movimiento de los enemigos, intentar que sigan al jugador/ que busquen la salida
    def dibujar(self, pantalla, offset_x, offset_y):
        if not self.muerto:
            pygame.draw.circle(pantalla, rojo, 
                              (int(self.x * tamanio_celda + tamanio_celda/2 + offset_x),
                               int(self.y * tamanio_celda + tamanio_celda/2 + offset_y)),
                              int(tamanio_celda/2.5))
    
    def actualizar(self, tiempo_actual):
        if self.muerto and tiempo_actual - self.tiempo_muerte >= self.tiempo_respawn:
            self.muerto = False
            return True
        return False

#BOTONES EN PANTALLA PRINCIPAL (TODO: ver donde los puedo acomodar mas bonito)
boton_jugar = Boton(ancho_ventana/2 - 150, alto_ventana/2 + 0,
                    300, 70, "JUGAR",
                    "#3FD98E", "#2FB975")

boton_puntaje = Boton(ancho_ventana/2 - 150, alto_ventana/2 + 90,
                    300, 70, "OPCIONES",
                    "#6A7DFF", "#5665D6")

boton_salir = Boton(ancho_ventana/2 - 150, alto_ventana/2 + 180,
                    300, 70, "SALIR",
                    "#FF5E6C", "#D94A56")

#BUCLE PRINCIPAL!!
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if boton_jugar.clicked(event):
            sonido_click.play()
            print("FUNCIONA EL BOTON DE JUGAR!!!")

        if boton_puntaje.clicked(event):
            sonido_click.play()
            print("FUNCIONA EL BOTON DE puntaje!")

        if boton_salir.clicked(event):
            sonido_click.play()
            running = False

    pantalla.fill("#12382C") #TODO: quiza lo cambie esto por una imagen, no me convence la vdd :<
    pantalla.blit(logo_grande, logo_rect)

    boton_jugar.draw(pantalla, fuente_boton)
    boton_puntaje.draw(pantalla, fuente_boton)
    boton_salir.draw(pantalla, fuente_boton)

    pygame.display.flip()

pygame.quit()