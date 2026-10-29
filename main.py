import pygame

from camara import obtener_direccion_mano, cerrar_camara

pygame.init()

ancho = 800
alto = 600

pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Vampire Escape")

reloj = pygame.time.Clock()

fuente = pygame.font.SysFont("arial", 24)
fuente_grande = pygame.font.SysFont("arial", 45)


# ---------------------------
# JUGADOR
# ---------------------------

jugador_x = 100
jugador_y = 400

velocidad = 5

ancho_jugador = 100
alto_jugador = 125


# ---------------------------
# CARGAR ANIMACIONES
# ---------------------------

def cargar_frames(ruta, cantidad_frames):

    hoja = pygame.image.load(ruta).convert_alpha()

    ancho_hoja = hoja.get_width()
    alto_hoja = hoja.get_height()

    ancho_frame = ancho_hoja // cantidad_frames

    frames = []

    for i in range(cantidad_frames):

        frame = hoja.subsurface(
            (
                i * ancho_frame,
                0,
                ancho_frame,
                alto_hoja
            )
        ).copy()

        rectangulo_visible = frame.get_bounding_rect()

        if rectangulo_visible.width > 0 and rectangulo_visible.height > 0:
            frame = frame.subsurface(rectangulo_visible).copy()

        ancho_original = frame.get_width()
        alto_original = frame.get_height()

        escala = min(
            100 / ancho_original,
            125 / alto_original
        )

        nuevo_ancho = int(ancho_original * escala)
        nuevo_alto = int(alto_original * escala)

        frame = pygame.transform.scale(
            frame,
            (nuevo_ancho, nuevo_alto)
        )

        lienzo = pygame.Surface(
            (100, 125),
            pygame.SRCALPHA
        )

        x = (100 - nuevo_ancho) // 2
        y = 125 - nuevo_alto

        lienzo.blit(
            frame,
            (x, y)
        )

        frames.append(lienzo)

    return frames


# ---------------------------
# IMAGEN DEFAULT
# ---------------------------

jugador_default = pygame.image.load(
    "assets/vampiro/default.png"
).convert_alpha()

rect_default = jugador_default.get_bounding_rect()

jugador_default = jugador_default.subsurface(
    rect_default
).copy()

ancho_original = jugador_default.get_width()
alto_original = jugador_default.get_height()

escala = min(
    100 / ancho_original,
    125 / alto_original
)

nuevo_ancho = int(ancho_original * escala)
nuevo_alto = int(alto_original * escala)

jugador_default = pygame.transform.scale(
    jugador_default,
    (nuevo_ancho, nuevo_alto)
)

lienzo_default = pygame.Surface(
    (100, 125),
    pygame.SRCALPHA
)

x_default = (100 - nuevo_ancho) // 2
y_default = 125 - nuevo_alto

lienzo_default.blit(
    jugador_default,
    (x_default, y_default)
)

jugador_default = lienzo_default


# ---------------------------
# SPRITES
# ---------------------------

frames_arriba = cargar_frames(
    "assets/vampiro/arriba.png",
    6
)

frames_abajo = cargar_frames(
    "assets/vampiro/abajo.png",
    6
)

frames_izquierda = cargar_frames(
    "assets/vampiro/izquierda.png",
    6
)

frames_derecha = cargar_frames(
    "assets/vampiro/derecha.png",
    6
)


# ---------------------------
# ANIMACIÓN
# ---------------------------

direccion = "abajo"

frame_actual = 0
contador_animacion = 0
velocidad_animacion = 7


# ---------------------------
# ESCENARIO
# ---------------------------

paredes = [

    pygame.Rect(
        0,
        0,
        800,
        30
    ),

    pygame.Rect(
        0,
        570,
        800,
        30
    ),

    pygame.Rect(
        0,
        0,
        30,
        600
    ),

    pygame.Rect(
        770,
        0,
        30,
        600
    ),

    pygame.Rect(
        200,
        120,
        30,
        300
    ),

    pygame.Rect(
        400,
        250,
        250,
        30
    ),

    pygame.Rect(
        520,
        400,
        30,
        150
    )
]


# ---------------------------
# OBJETOS
# ---------------------------

objetos = [

    pygame.Rect(
        100,
        100,
        25,
        25
    ),

    pygame.Rect(
        350,
        450,
        25,
        25
    ),

    pygame.Rect(
        680,
        150,
        25,
        25
    )
]

objetos_recogidos = 0


# ---------------------------
# PUERTA
# ---------------------------

puerta = pygame.Rect(
    700,
    500,
    50,
    70
)


# ---------------------------
# FUNCIÓN DE COLISIÓN
# ---------------------------

def hay_colision(rectangulo):

    for pared in paredes:

        if rectangulo.colliderect(pared):

            return True

    return False


# ---------------------------
# JUEGO
# ---------------------------

ejecutando = True
ganaste = False


while ejecutando:

    reloj.tick(60)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:

            ejecutando = False


    # -----------------------
    # CONTROLES
    # -----------------------

    teclas = pygame.key.get_pressed()

    direccion_mano = obtener_direccion_mano()

    movimiento_x = 0
    movimiento_y = 0

    moviendo = False


    if (
        teclas[pygame.K_LEFT]
        or direccion_mano == "izquierda"
    ):

        movimiento_x = -velocidad

        direccion = "izquierda"

        moviendo = True


    elif (
        teclas[pygame.K_RIGHT]
        or direccion_mano == "derecha"
    ):

        movimiento_x = velocidad

        direccion = "derecha"

        moviendo = True


    elif (
        teclas[pygame.K_UP]
        or direccion_mano == "arriba"
    ):

        movimiento_y = -velocidad

        direccion = "arriba"

        moviendo = True


    elif (
        teclas[pygame.K_DOWN]
        or direccion_mano == "abajo"
    ):

        movimiento_y = velocidad

        direccion = "abajo"

        moviendo = True


    # -----------------------
    # COLISIÓN HORIZONTAL
    # -----------------------

    nuevo_rect = pygame.Rect(
        jugador_x + movimiento_x,
        jugador_y,
        ancho_jugador,
        alto_jugador
    )

    if not hay_colision(nuevo_rect):

        jugador_x += movimiento_x


    # -----------------------
    # COLISIÓN VERTICAL
    # -----------------------

    nuevo_rect = pygame.Rect(
        jugador_x,
        jugador_y + movimiento_y,
        ancho_jugador,
        alto_jugador
    )

    if not hay_colision(nuevo_rect):

        jugador_y += movimiento_y


    # -----------------------
    # RECTÁNGULO DEL JUGADOR
    # -----------------------

    jugador_rect = pygame.Rect(
        jugador_x,
        jugador_y,
        ancho_jugador,
        alto_jugador
    )


    # -----------------------
    # RECOGER OBJETOS
    # -----------------------

    for objeto in objetos[:]:

        if jugador_rect.colliderect(objeto):

            objetos.remove(objeto)

            objetos_recogidos += 1


    # -----------------------
    # PUERTA
    # -----------------------

    if objetos_recogidos == 3:

        if jugador_rect.colliderect(puerta):

            ganaste = True


    # -----------------------
    # ANIMACIÓN
    # -----------------------

    if moviendo:

        contador_animacion += 1

        if contador_animacion >= velocidad_animacion:

            frame_actual += 1

            contador_animacion = 0

            if frame_actual >= 6:

                frame_actual = 0

    else:

        frame_actual = 0
        contador_animacion = 0


    if moviendo:

        if direccion == "arriba":

            imagen_jugador = frames_arriba[
                frame_actual
            ]

        elif direccion == "abajo":

            imagen_jugador = frames_abajo[
                frame_actual
            ]

        elif direccion == "izquierda":

            imagen_jugador = frames_izquierda[
                frame_actual
            ]

        elif direccion == "derecha":

            imagen_jugador = frames_derecha[
                frame_actual
            ]

    else:

        imagen_jugador = jugador_default


    # -----------------------
    # DIBUJAR ESCENARIO
    # -----------------------

    pantalla.fill(
        (25, 20, 30)
    )


    # PAREDES

    for pared in paredes:

        pygame.draw.rect(
            pantalla,
            (70, 60, 80),
            pared
        )


    # OBJETOS

    for objeto in objetos:

        pygame.draw.rect(
            pantalla,
            (180, 30, 50),
            objeto
        )

        pygame.draw.circle(
            pantalla,
            (255, 80, 100),
            objeto.center,
            7
        )


    # PUERTA

    if objetos_recogidos == 3:

        pygame.draw.rect(
            pantalla,
            (80, 180, 100),
            puerta
        )

    else:

        pygame.draw.rect(
            pantalla,
            (100, 40, 40),
            puerta
        )


    # JUGADOR

    pantalla.blit(
        imagen_jugador,
        (
            jugador_x,
            jugador_y
        )
    )


    # -----------------------
    # INTERFAZ
    # -----------------------

    texto_objetos = fuente.render(
        f"Objetos: {objetos_recogidos}/3",
        True,
        (255, 255, 255)
    )

    pantalla.blit(
        texto_objetos,
        (40, 40)
    )


    if objetos_recogidos < 3:

        texto_puerta = fuente.render(
            "Encuentra los 3 objetos para abrir la puerta",
            True,
            (255, 255, 255)
        )

    else:

        texto_puerta = fuente.render(
            "La puerta está abierta",
            True,
            (100, 255, 120)
        )

    pantalla.blit(
        texto_puerta,
        (250, 40)
    )


    # -----------------------
    # PANTALLA DE VICTORIA
    # -----------------------

    if ganaste:

        pantalla.fill(
            (20, 15, 25)
        )

        texto_ganar = fuente_grande.render(
            "¡ESCAPASTE!",
            True,
            (255, 255, 255)
        )

        pantalla.blit(
            texto_ganar,
            (280, 240)
        )

        texto_salir = fuente.render(
            "Cierra la ventana para salir",
            True,
            (200, 200, 200)
        )

        pantalla.blit(
            texto_salir,
            (285, 310)
        )


    pygame.display.update()


cerrar_camara()

pygame.quit()
