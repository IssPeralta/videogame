
import pygame
 
from camara import obtener_direccion_mano, cerrar_camara
 
import escenario
import sonidos
 
 
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.init()
 
ancho = escenario.ANCHO
alto = escenario.ALTO
 
pantalla = pygame.display.set_mode((ancho, alto))
pygame.display.set_caption("Vampire Escape")
 
reloj = pygame.time.Clock()
 
escenario.iniciar()
sonidos.iniciar_audio()
 
 
# ---------------------------
# JUGADOR
# ---------------------------
 
velocidad = 3
 
# Tamaño con el que se dibuja el vampiro
ancho_sprite = 56
alto_sprite = 70
 
# La colisión se calcula solo con los pies,
# así el vampiro cabe bien por los pasillos
ancho_pies = 26
alto_pies = 18
 
 
# ---------------------------
# CARGAR ANIMACIONES
# ---------------------------
 
def ajustar_frame(frame, ancho_final, alto_final):
 
    rectangulo_visible = frame.get_bounding_rect()
 
    if rectangulo_visible.width > 0 and rectangulo_visible.height > 0:
        frame = frame.subsurface(rectangulo_visible).copy()
 
    ancho_original = frame.get_width()
    alto_original = frame.get_height()
 
    escala = min(
        ancho_final / ancho_original,
        alto_final / alto_original
    )
 
    nuevo_ancho = int(ancho_original * escala)
    nuevo_alto = int(alto_original * escala)
 
    frame = pygame.transform.smoothscale(
        frame,
        (nuevo_ancho, nuevo_alto)
    )
 
    lienzo = pygame.Surface(
        (ancho_final, alto_final),
        pygame.SRCALPHA
    )
 
    x = (ancho_final - nuevo_ancho) // 2
    y = alto_final - nuevo_alto
 
    lienzo.blit(
        frame,
        (x, y)
    )
 
    return lienzo
 
 
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
 
        frames.append(
            ajustar_frame(frame, ancho_sprite, alto_sprite)
        )
 
    return frames
 
 
# ---------------------------
# IMAGEN DEFAULT
# ---------------------------
 
imagen_default = pygame.image.load(
    "assets/vampiro/default.png"
).convert_alpha()
 
jugador_default = ajustar_frame(imagen_default, ancho_sprite, alto_sprite)
 
# Versión grande para la pantalla de inicio
retrato_vampiro = ajustar_frame(imagen_default, 150, 190)
 
 
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
 
velocidad_animacion = 7
 
 
# ---------------------------
# NUEVA PARTIDA
# ---------------------------
 
def nueva_partida():
 
    global laberinto, paredes, objetos, puerta
    global pies, objetos_recogidos, direccion
    global frame_actual, contador_animacion
    global tiempo_inicio, tiempo_final
    global mensaje, mensaje_hasta
 
    # Cada partida genera un laberinto diferente
    laberinto = escenario.Laberinto()
 
    paredes = laberinto.paredes
    objetos = laberinto.objetos
    puerta = laberinto.puerta
 
    pies = pygame.Rect(0, 0, ancho_pies, alto_pies)
    pies.center = laberinto.inicio
 
    objetos_recogidos = 0
 
    direccion = "abajo"
    frame_actual = 0
    contador_animacion = 0
 
    tiempo_inicio = pygame.time.get_ticks()
    tiempo_final = 0
 
    mensaje = "¡Encuentra las 3 gotas de sangre!"
    mensaje_hasta = pygame.time.get_ticks() + 2500
 
 
def mostrar_mensaje(texto, duracion_ms=2000):
 
    global mensaje, mensaje_hasta
 
    mensaje = texto
    mensaje_hasta = pygame.time.get_ticks() + duracion_ms
 
 
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
 
nueva_partida()
 
estado = "inicio"          # "inicio", "jugando" o "victoria"
progreso_mano = 0          # para empezar levantando la mano
tiempo_pantalla = 0        # segundos desde que se abrió la pantalla actual
 
ultimo_choque = 0
contador_pasos = 0
 
sonidos.iniciar_musica()
 
ejecutando = True
 
 
while ejecutando:
 
    dt = reloj.tick(60) / 1000
    t = pygame.time.get_ticks() / 1000
    tiempo_pantalla += dt
 
    empezar = False
 
    for evento in pygame.event.get():
 
        if evento.type == pygame.QUIT:
 
            ejecutando = False
 
        elif evento.type == pygame.KEYDOWN:
 
            if evento.key == pygame.K_ESCAPE:
                ejecutando = False
 
            elif estado == "inicio" and evento.key in (pygame.K_SPACE, pygame.K_RETURN):
                empezar = True
 
            elif estado == "victoria" and evento.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                empezar = True
 
 
    # -----------------------
    # CONTROLES
    # -----------------------
 
    teclas = pygame.key.get_pressed()
 
    direccion_mano = obtener_direccion_mano()
 
 
    # -----------------------
    # PANTALLA DE INICIO / VICTORIA
    # -----------------------
 
    if estado in ("inicio", "victoria"):
 
        # Mantener la mano arriba 1 segundo también sirve para empezar
        if direccion_mano == "arriba":
            progreso_mano += dt
        else:
            progreso_mano = max(0, progreso_mano - dt * 2)
 
        if progreso_mano >= 1:
            empezar = True
 
        if empezar:
 
            if estado == "victoria":
                nueva_partida()
            else:
                tiempo_inicio = pygame.time.get_ticks()
                mostrar_mensaje("¡Encuentra las 3 gotas de sangre!", 2500)
 
            estado = "jugando"
            progreso_mano = 0
            tiempo_pantalla = 0
 
            sonidos.reproducir("inicio")
            sonidos.iniciar_musica()
 
        elif estado == "inicio":
 
            escenario.dibujar_inicio(
                pantalla,
                t,
                dt,
                progreso_mano,
                retrato_vampiro
            )
 
        else:
 
            escenario.dibujar_victoria(
                pantalla,
                tiempo_pantalla,
                dt,
                tiempo_final,
                progreso_mano
            )
 
        pygame.display.update()
 
        continue
 
 
    # -----------------------
    # MOVIMIENTO
    # -----------------------
 
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
 
 
    choco = False
 
    # -----------------------
    # COLISIÓN HORIZONTAL
    # -----------------------
 
    nuevo_rect = pies.move(movimiento_x, 0)
 
    if not hay_colision(nuevo_rect):
 
        pies = nuevo_rect
 
    elif movimiento_x != 0:
 
        choco = True
 
 
    # -----------------------
    # COLISIÓN VERTICAL
    # -----------------------
 
    nuevo_rect = pies.move(0, movimiento_y)
 
    if not hay_colision(nuevo_rect):
 
        pies = nuevo_rect
 
    elif movimiento_y != 0:
 
        choco = True
 
 
    # -----------------------
    # SONIDOS DE MOVIMIENTO
    # -----------------------
 
    ahora = pygame.time.get_ticks()
 
    if choco and ahora - ultimo_choque > 500:
 
        sonidos.reproducir("choque")
 
        ultimo_choque = ahora
 
    if moviendo and not choco:
 
        contador_pasos += 1
 
        if contador_pasos >= 16:
 
            sonidos.reproducir("paso")
 
            contador_pasos = 0
 
 
    # -----------------------
    # RECOGER OBJETOS
    # -----------------------
 
    for objeto in objetos[:]:
 
        if pies.colliderect(objeto.inflate(10, 20)):
 
            objetos.remove(objeto)
 
            objetos_recogidos += 1
 
            if objetos_recogidos == 3:
 
                sonidos.reproducir("puerta")
 
                mostrar_mensaje("¡La puerta se abrió! Busca la salida", 2500)
 
            else:
 
                sonidos.reproducir("recoger")
 
                mostrar_mensaje(f"Gota de sangre {objetos_recogidos}/3", 1200)
 
 
    # -----------------------
    # PUERTA
    # -----------------------
 
    if pies.colliderect(puerta):
 
        if objetos_recogidos == 3:
 
            tiempo_final = (ahora - tiempo_inicio) / 1000
 
            sonidos.reproducir("victoria")
 
            estado = "victoria"
            tiempo_pantalla = 0
            progreso_mano = 0
 
            continue
 
        elif ahora > mensaje_hasta:
 
            mostrar_mensaje("La puerta está cerrada... faltan gotas", 1500)
 
 
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
 
    escenario.dibujar_fondo_juego(pantalla, laberinto, t)
 
    escenario.dibujar_puerta(pantalla, puerta, objetos_recogidos == 3, t)
 
    escenario.dibujar_frascos(pantalla, objetos, t)
 
 
    # SOMBRA Y JUGADOR
 
    sombra = pygame.Surface((36, 12), pygame.SRCALPHA)
    pygame.draw.ellipse(sombra, (0, 0, 0, 110), (0, 0, 36, 12))
    pantalla.blit(sombra, (pies.centerx - 18, pies.bottom - 8))
 
    pantalla.blit(
        imagen_jugador,
        (
            pies.centerx - ancho_sprite // 2,
            pies.bottom + 2 - alto_sprite
        )
    )
 
 
    # EFECTOS (niebla, murciélagos, bordes oscuros)
 
    escenario.dibujar_efectos(pantalla, t, dt)
 
 
    # -----------------------
    # INTERFAZ
    # -----------------------
 
    segundos = (pygame.time.get_ticks() - tiempo_inicio) / 1000
 
    texto_mensaje = mensaje if pygame.time.get_ticks() < mensaje_hasta else None
 
    escenario.dibujar_hud(
        pantalla,
        objetos_recogidos,
        segundos,
        texto_mensaje
    )
 
 
    pygame.display.update()
 
 
cerrar_camara()
 
pygame.quit()