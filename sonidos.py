import os
 
import numpy as np
import pygame
 
 
# ------------------------------------------------------------
# EFECTOS DE SONIDO
#
# Los sonidos se generan con código (no necesitas archivos).
# Si quieres usar tus propios sonidos, pon un archivo .wav u .ogg
# en assets/sonidos/ con el mismo nombre y se usará ese:
#
#   inicio, recoger, puerta, victoria, choque, paso
#
# La música de fondo va en: assets/sonidos/musica.mp3
# ------------------------------------------------------------
 
FRECUENCIA = 44100
 
sonidos = {}
canal_musica = None
audio_activo = False
 
VOLUMENES = {
    "inicio": 0.6,
    "recoger": 0.6,
    "puerta": 0.7,
    "victoria": 0.7,
    "choque": 0.35,
    "paso": 0.15,
    "ambiente": 0.35,
}
 
 
# ---------------------------
# HERRAMIENTAS DE SÍNTESIS
# ---------------------------
 
def tiempo(duracion):
    return np.linspace(0, duracion, int(FRECUENCIA * duracion), endpoint=False)
 
 
def nota_organo(frecuencia, duracion, ataque=0.02, caida=0.3):
    """Sonido parecido a un órgano de iglesia."""
    t = tiempo(duracion)
    onda = (
        np.sin(2 * np.pi * frecuencia * t)
        + 0.5 * np.sin(2 * np.pi * frecuencia * 2 * t)
        + 0.3 * np.sin(2 * np.pi * frecuencia * 3 * t)
        + 0.15 * np.sin(2 * np.pi * frecuencia * 4 * t)
        + 0.3 * np.sin(2 * np.pi * frecuencia * 0.5 * t)
    )
    env = np.ones_like(t)
    a = int(FRECUENCIA * ataque)
    c = int(FRECUENCIA * caida)
    if a > 0:
        env[:a] = np.linspace(0, 1, a)
    if c > 0:
        env[-c:] *= np.linspace(1, 0, c)
    return onda * env
 
 
def campana(frecuencia, duracion, decaimiento=6):
    t = tiempo(duracion)
    onda = (
        np.sin(2 * np.pi * frecuencia * t)
        + 0.4 * np.sin(2 * np.pi * frecuencia * 2.76 * t)
        + 0.2 * np.sin(2 * np.pi * frecuencia * 5.4 * t)
    )
    return onda * np.exp(-t * decaimiento)
 
 
def ruido_suave(n, ventana):
    ruido = np.random.uniform(-1, 1, n)
    return np.convolve(ruido, np.ones(ventana) / ventana, mode="same")
 
 
def concatenar(*partes):
    return np.concatenate(partes)
 
 
def mezclar(*ondas):
    largo = max(len(o) for o in ondas)
    total = np.zeros(largo)
    for o in ondas:
        total[:len(o)] += o
    return total
 
 
def normalizar(onda, volumen=0.9):
    pico = np.max(np.abs(onda))
    if pico > 0:
        onda = onda / pico * volumen
    return onda
 
 
# ---------------------------
# SONIDOS
# ---------------------------
 
def crear_inicio():
    # Acorde dramático de órgano (estilo película de Drácula)
    motivo = concatenar(
        nota_organo(880.00, 0.12, caida=0.03),
        nota_organo(783.99, 0.12, caida=0.03),
        nota_organo(880.00, 0.45, caida=0.15),
        np.zeros(int(FRECUENCIA * 0.08)),
    )
    acorde = mezclar(
        nota_organo(146.83, 1.8, caida=1.0),
        nota_organo(174.61, 1.8, caida=1.0),
        nota_organo(220.00, 1.8, caida=1.0),
        nota_organo(293.66, 1.8, caida=1.0),
    )
    return normalizar(concatenar(motivo, acorde))
 
 
def crear_recoger():
    notas = [880, 1174.66, 1567.98, 2349.32]
    partes = []
    for i, f in enumerate(notas):
        partes.append(np.pad(campana(f, 0.6, 9), (int(FRECUENCIA * 0.07 * i), 0)))
    return normalizar(mezclar(*partes), 0.8)
 
 
def crear_puerta():
    # Chirrido de puerta vieja
    t = tiempo(0.9)
    tono = 180 + 60 * np.sin(2 * np.pi * 3 * t) + 40 * np.random.uniform(-1, 1, len(t))
    fase = 2 * np.pi * np.cumsum(tono) / FRECUENCIA
    chirrido = np.sign(np.sin(fase)) * 0.25 * np.sin(np.pi * t / 0.9)
 
    # Golpe grave tipo gong
    gong = mezclar(
        campana(73.42, 2.5, 1.8),
        0.6 * campana(110.0, 2.5, 2.2),
        0.4 * campana(146.83, 2.5, 2.6),
    )
    return normalizar(mezclar(chirrido, np.pad(gong, (int(FRECUENCIA * 0.6), 0))))
 
 
def crear_victoria():
    # Arpegio en re menor que termina en re mayor
    notas = [293.66, 349.23, 440.00, 587.33]
    partes = [nota_organo(f, 0.18, caida=0.05) for f in notas]
    final = mezclar(
        nota_organo(293.66, 1.6, caida=0.9),
        nota_organo(369.99, 1.6, caida=0.9),
        nota_organo(440.00, 1.6, caida=0.9),
        nota_organo(587.33, 1.6, caida=0.9),
    )
    return normalizar(concatenar(*partes, final))
 
 
def crear_choque():
    t = tiempo(0.15)
    golpe = np.sin(2 * np.pi * 70 * t) * np.exp(-t * 30)
    ruido = ruido_suave(len(t), 20) * np.exp(-t * 40) * 3
    return normalizar(golpe + ruido, 0.8)
 
 
def crear_paso():
    t = tiempo(0.07)
    ruido = ruido_suave(len(t), 12) * np.exp(-t * 60)
    return normalizar(ruido, 0.6)
 
 
def crear_ambiente():
    # Música de fondo tenebrosa que se repite sin cortes (8 segundos)
    duracion = 8.0
    t = tiempo(duracion)
 
    # Las frecuencias son múltiplos de 1/8 Hz para que el bucle sea perfecto
    dron = (
        np.sin(2 * np.pi * 73.375 * t)
        + 0.6 * np.sin(2 * np.pi * 110.0 * t)
        + 0.35 * np.sin(2 * np.pi * 174.625 * t)
        + 0.2 * np.sin(2 * np.pi * 73.5 * t)
    )
    dron *= 0.6 + 0.4 * np.sin(2 * np.pi * 0.25 * t)
 
    # Viento: ruido filtrado (con FFT para que también sea cíclico)
    ruido = np.random.uniform(-1, 1, len(t))
    espectro = np.fft.rfft(ruido)
    frecuencias = np.fft.rfftfreq(len(t), 1 / FRECUENCIA)
    espectro[(frecuencias < 200) | (frecuencias > 900)] = 0
    viento = np.fft.irfft(espectro, len(t))
    viento = normalizar(viento, 1) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.375 * t)) * 0.35
 
    # Campanadas lejanas
    campanas = np.zeros(len(t))
    for inicio in (0.5, 4.5):
        c = campana(220, 3.0, 1.5) * 0.25
        i = int(FRECUENCIA * inicio)
        campanas[i:i + len(c)] += c[:len(t) - i]
 
    return normalizar(dron * 0.5 + viento + campanas, 0.7)
 
 
GENERADORES = {
    "inicio": crear_inicio,
    "recoger": crear_recoger,
    "puerta": crear_puerta,
    "victoria": crear_victoria,
    "choque": crear_choque,
    "paso": crear_paso,
    "ambiente": crear_ambiente,
}
 
 
# ---------------------------
# CONVERTIR A SONIDO DE PYGAME
# ---------------------------
 
def onda_a_sonido(onda):
 
    frecuencia, formato, canales = pygame.mixer.get_init()
 
    if frecuencia != FRECUENCIA:
        # Ajustar a la frecuencia real del mezclador
        x_viejo = np.linspace(0, 1, len(onda))
        x_nuevo = np.linspace(0, 1, int(len(onda) * frecuencia / FRECUENCIA))
        onda = np.interp(x_nuevo, x_viejo, onda)
 
    if formato in (-16, 16):
        datos = (onda * 32767).astype(np.int16)
    elif formato == 8:
        datos = ((onda + 1) * 127.5).astype(np.uint8)
    elif formato == -8:
        datos = (onda * 127).astype(np.int8)
    else:
        datos = onda.astype(np.float32)
 
    if canales > 1:
        datos = np.repeat(datos[:, None], canales, axis=1)
 
    return pygame.sndarray.make_sound(np.ascontiguousarray(datos))
 
 
def cargar_archivo(nombre):
 
    for extension in (".wav", ".ogg", ".mp3"):
        ruta = os.path.join("assets", "sonidos", nombre + extension)
        if os.path.exists(ruta):
            try:
                return pygame.mixer.Sound(ruta)
            except pygame.error:
                pass
    return None
 
 
# ---------------------------
# FUNCIONES PARA main.py
# ---------------------------
 
def iniciar_audio():
 
    global audio_activo, canal_musica
 
    # Intentamos abrir el audio; si falla con la configuración
    # normal, probamos con la que elija la computadora.
    for intento in ((FRECUENCIA, -16, 2, 1024), None):
        try:
            if not pygame.mixer.get_init():
                if intento:
                    pygame.mixer.init(*intento)
                else:
                    pygame.mixer.init()
            break
        except pygame.error as error:
            print("Audio: no se pudo abrir con", intento, "->", error)
 
    if not pygame.mixer.get_init():
        print("Audio: DESACTIVADO (no se encontró una salida de sonido)")
        audio_activo = False
        return
 
    print("Audio: iniciado", pygame.mixer.get_init())
 
    pygame.mixer.set_num_channels(16)
    pygame.mixer.set_reserved(1)   # el canal 0 queda solo para la música
    canal_musica = pygame.mixer.Channel(0)
    audio_activo = True
 
    for nombre, generador in GENERADORES.items():
        sonido = cargar_archivo(nombre)
 
        if sonido is None:
            try:
                sonido = onda_a_sonido(generador())
            except Exception as error:
                print(f"Audio: no se pudo crear el sonido '{nombre}':", error)
                continue
 
        sonido.set_volume(VOLUMENES.get(nombre, 0.5))
        sonidos[nombre] = sonido
 
    print("Audio: sonidos listos ->", ", ".join(sonidos))
 
 
# ---------------------------
# MÚSICA DE FONDO
#
# Si existe assets/sonidos/musica.mp3 (o .ogg / .wav) se usa
# como música de fondo. Si no, se usa la música generada.
# ---------------------------
 
VOLUMEN_MUSICA = 0.5
 
 
def buscar_musica():
 
    for extension in (".mp3", ".ogg", ".wav"):
        ruta = os.path.join("assets", "sonidos", "musica" + extension)
        if os.path.exists(ruta):
            return ruta
    return None
 
 
def iniciar_musica():
 
    if not audio_activo:
        return
 
    ruta = buscar_musica()
 
    if ruta:
        if pygame.mixer.music.get_busy():
            return
        try:
            pygame.mixer.music.load(ruta)
            pygame.mixer.music.set_volume(VOLUMEN_MUSICA)
            pygame.mixer.music.play(loops=-1, fade_ms=1500)
            print("Audio: música de fondo ->", ruta)
            return
        except pygame.error as error:
            print("Audio: no se pudo reproducir", ruta, "->", error)
 
    if "ambiente" in sonidos and not canal_musica.get_busy():
        canal_musica.play(sonidos["ambiente"], loops=-1, fade_ms=1500)
 
 
def detener_musica():
 
    if not audio_activo:
        return
 
    pygame.mixer.music.fadeout(800)
 
    if canal_musica is not None:
        canal_musica.fadeout(800)
 
 
def reproducir(nombre):
 
    if audio_activo and nombre in sonidos:
        sonidos[nombre].play()