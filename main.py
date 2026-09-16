import pygame

from camara import obtener_direccion_mano, cerrar_camara

pygame.init()

ancho = 800
alto = 600

pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Mi videojuego")

reloj = pygame.time.Clock()

jugador_x = 375
jugador_y = 275

velocidad = 5


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

            frame = frame.subsurface(
                rectangulo_visible
            ).copy()

        ancho_original = frame.get_width()
        alto_original = frame.get_height()

        escala = min(
            100 / ancho_original,
            125 / alto_original
        )

        nuevo_ancho = int(
            ancho_original * escala
        )

        nuevo_alto = int(
            alto_original * escala
        )

        frame = pygame.transform.scale(
            frame,
            (nuevo_ancho, nuevo_alto)
        )

        lienzo = pygame.Surface(
            (100, 125),
            pygame.SRCALPHA
        )

        x = (
            100 - nuevo_ancho
        ) // 2

        y = (
            125 - nuevo_alto
        )

        lienzo.blit(
            frame,
            (x, y)
        )

        frames.append(
            lienzo
        )

    return frames


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

nuevo_ancho = int(
    ancho_original * escala
)

nuevo_alto = int(
    alto_original * escala
)

jugador_default = pygame.transform.scale(
    jugador_default,
    (
        nuevo_ancho,
        nuevo_alto
    )
)

lienzo_default = pygame.Surface(
    (100, 125),
    pygame.SRCALPHA
)

x_default = (
    100 - nuevo_ancho
) // 2

y_default = (
    125 - nuevo_alto
)

lienzo_default.blit(
    jugador_default,
    (
        x_default,
        y_default
    )
)

jugador_default = lienzo_default


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


ancho_jugador = 100
alto_jugador = 125

direccion = "abajo"

frame_actual = 0

contador_animacion = 0

velocidad_animacion = 7


ejecutando = True


while ejecutando:

    reloj.tick(60)

    for evento in pygame.event.get():

        if evento.type == pygame.QUIT:
            ejecutando = False


    teclas = pygame.key.get_pressed()

    direccion_mano = obtener_direccion_mano()

    moviendo = False


    if (
        teclas[pygame.K_LEFT]
        or direccion_mano == "izquierda"
    ):

        jugador_x -= velocidad

        direccion = "izquierda"

        moviendo = True


    elif (
        teclas[pygame.K_RIGHT]
        or direccion_mano == "derecha"
    ):

        jugador_x += velocidad

        direccion = "derecha"

        moviendo = True


    elif (
        teclas[pygame.K_UP]
        or direccion_mano == "arriba"
    ):

        jugador_y -= velocidad

        direccion = "arriba"

        moviendo = True


    elif (
        teclas[pygame.K_DOWN]
        or direccion_mano == "abajo"
    ):

        jugador_y += velocidad

        direccion = "abajo"

        moviendo = True


    if jugador_x < 0:
        jugador_x = 0


    if jugador_x > ancho - ancho_jugador:
        jugador_x = ancho - ancho_jugador


    if jugador_y < 0:
        jugador_y = 0


    if jugador_y > alto - alto_jugador:
        jugador_y = alto - alto_jugador


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


    pantalla.fill(
        (0, 0, 0)
    )

    pantalla.blit(
        imagen_jugador,
        (
            jugador_x,
            jugador_y
        )
    )

    pygame.display.update()


cerrar_camara()

pygame.quit()