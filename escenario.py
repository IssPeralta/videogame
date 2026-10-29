
import math
import random
 
import pygame
 
 
# ---------------------------
# MEDIDAS
# ---------------------------
 
ANCHO = 800
ALTO = 600
 
TILE = 32            # tamaño de cada bloque del laberinto
COLUMNAS = 25        # 25 * 32 = 800 px
FILAS = 16           # 16 * 32 = 512 px
OFFSET_Y = 80        # espacio arriba para el marcador (HUD)
 
CELDAS_X = (COLUMNAS - 1) // 3   # 8 celdas de ancho
CELDAS_Y = (FILAS - 1) // 3      # 5 celdas de alto
 
 
# ---------------------------
# COLORES
# ---------------------------
 
ROJO_SANGRE = (170, 15, 35)
ROJO_CLARO = (230, 60, 75)
BLANCO_HUESO = (235, 225, 215)
GRIS = (170, 160, 175)
NEGRO_NOCHE = (8, 4, 12)
 
 
# Se llenan en iniciar()
fuentes = {}
cielo = None
niebla = None
vineta = None
brillo_vela = None
brillo_frasco = None
gota_grande = None
gota_chica = None
gota_vacia = None
murcielagos = []
 
 
# ---------------------------
# UTILIDADES
# ---------------------------
 
def crear_brillo(radio, color):
    """Círculo de luz suave para mezclar con BLEND_RGB_ADD."""
 
    superficie = pygame.Surface((radio * 2, radio * 2))
    superficie.fill((0, 0, 0))
 
    for r in range(radio, 0, -1):
        k = 1 - r / radio
        k = k * k
        c = (
            int(color[0] * k),
            int(color[1] * k),
            int(color[2] * k)
        )
        pygame.draw.circle(superficie, c, (radio, radio), r)
 
    return superficie
 
 
def texto_centrado(superficie, texto, fuente, color, centro_x, y, sombra=True):
 
    if sombra:
        imagen_sombra = fuente.render(texto, True, (0, 0, 0))
        rect = imagen_sombra.get_rect(midtop=(centro_x + 2, y + 2))
        superficie.blit(imagen_sombra, rect)
 
    imagen = fuente.render(texto, True, color)
    rect = imagen.get_rect(midtop=(centro_x, y))
    superficie.blit(imagen, rect)
 
    return rect
 
 
def titulo_con_brillo(superficie, texto, fuente, centro_x, y):
 
    # Resplandor rojo alrededor del título
    for dx, dy in ((-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)):
        imagen = fuente.render(texto, True, (120, 0, 15))
        rect = imagen.get_rect(midtop=(centro_x + dx, y + dy))
        superficie.blit(imagen, rect)
 
    imagen = fuente.render(texto, True, BLANCO_HUESO)
    rect = imagen.get_rect(midtop=(centro_x, y))
    superficie.blit(imagen, rect)
 
 
# ---------------------------
# FONDO: CIELO, LUNA Y CASTILLO
# ---------------------------
 
def crear_cielo():
 
    superficie = pygame.Surface((ANCHO, ALTO))
 
    # Degradado de morado oscuro a rojo sangre
    for y in range(ALTO):
        k = y / ALTO
        color = (
            int(14 + 38 * k),
            int(5 + 3 * k),
            int(26 - 6 * k)
        )
        pygame.draw.line(superficie, color, (0, y), (ANCHO, y))
 
    rng = random.Random(7)
 
    # Estrellas
    for _ in range(160):
        x = rng.randint(0, ANCHO)
        y = rng.randint(0, int(ALTO * 0.7))
        b = rng.randint(90, 230)
        if rng.random() < 0.85:
            superficie.set_at((x, y), (b, b, b))
        else:
            pygame.draw.circle(superficie, (b, b - 20, b - 10), (x, y), 2)
 
    # Luna de sangre
    luna_x, luna_y, radio = 640, 170, 62
 
    brillo = crear_brillo(radio * 3, (150, 20, 30))
    superficie.blit(
        brillo,
        (luna_x - radio * 3, luna_y - radio * 3),
        special_flags=pygame.BLEND_RGB_ADD
    )
 
    pygame.draw.circle(superficie, (150, 20, 30), (luna_x, luna_y), radio)
    pygame.draw.circle(superficie, (185, 35, 45), (luna_x - 6, luna_y - 6), radio - 8)
    pygame.draw.circle(superficie, (205, 55, 60), (luna_x - 12, luna_y - 12), radio - 22)
 
    for cx, cy, r in ((-20, 10, 10), (15, -18, 7), (22, 20, 12), (-5, -30, 5), (-30, -10, 6)):
        pygame.draw.circle(superficie, (140, 20, 30), (luna_x + cx, luna_y + cy), r)
 
    # Nubes oscuras cruzando la luna
    nubes = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    for nx, ny, nw, nh in ((520, 175, 260, 26), (590, 205, 200, 18), (430, 120, 180, 14), (60, 90, 240, 20)):
        pygame.draw.ellipse(nubes, (10, 4, 14, 170), (nx, ny, nw, nh))
    superficie.blit(nubes, (0, 0))
 
    # Colinas
    puntos_colina = [(0, ALTO)]
    for x in range(0, ANCHO + 40, 40):
        puntos_colina.append((x, 470 + int(math.sin(x / 90) * 18 + math.sin(x / 37) * 8)))
    puntos_colina.append((ANCHO, ALTO))
    pygame.draw.polygon(superficie, (16, 6, 16), puntos_colina)
 
    # Castillo
    color_castillo = (10, 3, 12)
    base_y = 470
 
    def torre(x, ancho, alto):
        pygame.draw.rect(superficie, color_castillo, (x, base_y - alto, ancho, alto))
        pygame.draw.polygon(
            superficie,
            color_castillo,
            [(x - 6, base_y - alto), (x + ancho // 2, base_y - alto - ancho * 1.4), (x + ancho + 6, base_y - alto)]
        )
 
    pygame.draw.rect(superficie, color_castillo, (110, base_y - 120, 260, 120))
 
    for x in range(110, 370, 20):
        pygame.draw.rect(superficie, color_castillo, (x, base_y - 132, 12, 14))
 
    torre(80, 46, 190)
    torre(190, 40, 240)
    torre(290, 36, 170)
    torre(360, 50, 140)
 
    # Ventanas encendidas
    for wx, wy in ((97, 320), (207, 260), (207, 300), (303, 335), (150, 400), (250, 390), (380, 370)):
        pygame.draw.rect(superficie, (220, 120, 40), (wx, wy, 6, 10))
        pygame.draw.circle(superficie, (220, 120, 40), (wx + 3, wy), 3)
 
    # Árboles secos
    for tx in (520, 600, 735):
        pygame.draw.line(superficie, (12, 4, 12), (tx, 480), (tx, 400), 5)
        pygame.draw.line(superficie, (12, 4, 12), (tx, 430), (tx - 25, 405), 3)
        pygame.draw.line(superficie, (12, 4, 12), (tx, 420), (tx + 22, 392), 3)
        pygame.draw.line(superficie, (12, 4, 12), (tx - 25, 405), (tx - 32, 390), 2)
 
    return superficie
 
 
def crear_niebla():
 
    superficie = pygame.Surface((ANCHO * 2, ALTO), pygame.SRCALPHA)
    rng = random.Random(3)
 
    for _ in range(40):
        w = rng.randint(120, 300)
        h = rng.randint(30, 80)
        x = rng.randint(-w, ANCHO)
        y = rng.randint(100, ALTO - h)
 
        if rng.random() < 0.5:
            color = (120, 20, 40, rng.randint(8, 16))
        else:
            color = (90, 70, 120, rng.randint(6, 12))
 
        # Se dibuja dos veces para que el movimiento se repita sin cortes
        pygame.draw.ellipse(superficie, color, (x, y, w, h))
        pygame.draw.ellipse(superficie, color, (x + ANCHO, y, w, h))
 
    return superficie
 
 
def crear_vineta():
 
    pequena = pygame.Surface((100, 75), pygame.SRCALPHA)
 
    for y in range(75):
        for x in range(100):
            dx = (x - 50) / 50
            dy = (y - 37.5) / 37.5
            d = math.sqrt(dx * dx + dy * dy)
            k = max(0.0, min(1.0, (d - 0.6) / 0.6))
            pequena.set_at((x, y), (0, 0, 0, int(210 * k ** 1.4)))
 
    return pygame.transform.smoothscale(pequena, (ANCHO, ALTO))
 
 
# ---------------------------
# MURCIÉLAGOS
# ---------------------------
 
class Murcielago:
 
    def __init__(self, rng, zona_alto, primera_vez=False):
        self.rng = rng
        self.zona_alto = zona_alto
        self.reiniciar(primera_vez)
 
    def reiniciar(self, primera_vez=False):
        self.tam = self.rng.randint(8, 16)
        self.vel = self.rng.uniform(60, 140) * self.rng.choice((-1, 1))
        self.base_y = self.rng.randint(30, self.zona_alto)
        self.fase = self.rng.uniform(0, 6.28)
        self.amplitud = self.rng.uniform(8, 30)
 
        if primera_vez:
            self.x = self.rng.uniform(0, ANCHO)
        elif self.vel > 0:
            self.x = -40 - self.rng.uniform(0, 400)
        else:
            self.x = ANCHO + 40 + self.rng.uniform(0, 400)
 
    def actualizar(self, dt, t):
        self.x += self.vel * dt
        self.y = self.base_y + math.sin(t * 1.5 + self.fase) * self.amplitud
 
        if self.x < -60 - 400 or self.x > ANCHO + 60 + 400:
            self.reiniciar()
 
    def dibujar(self, superficie, t):
        x = self.x
        y = self.y
        s = self.tam
        aleteo = math.sin(t * 16 + self.fase) * s * 0.7
        color = (12, 4, 14)
 
        ala_izq = [
            (x - 2, y),
            (x - s * 0.6, y - aleteo - s * 0.2),
            (x - s * 1.4, y - aleteo * 0.6),
            (x - s * 1.1, y + s * 0.2),
            (x - s * 0.7, y + s * 0.05),
            (x - s * 0.4, y + s * 0.3)
        ]
        ala_der = [(2 * x - px, py) for px, py in ala_izq]
 
        pygame.draw.polygon(superficie, color, ala_izq)
        pygame.draw.polygon(superficie, color, ala_der)
        pygame.draw.ellipse(superficie, color, (int(x - s * 0.3), int(y - s * 0.3), int(s * 0.6), int(s * 0.75)))
        pygame.draw.polygon(superficie, color, [(x - s * 0.25, y - s * 0.2), (x - s * 0.2, y - s * 0.55), (x - s * 0.05, y - s * 0.25)])
        pygame.draw.polygon(superficie, color, [(x + s * 0.25, y - s * 0.2), (x + s * 0.2, y - s * 0.55), (x + s * 0.05, y - s * 0.25)])
        superficie.set_at((int(x - 2), int(y - 1)), (255, 40, 40))
        superficie.set_at((int(x + 2), int(y - 1)), (255, 40, 40))
 
 
def crear_murcielagos(cantidad, zona_alto):
 
    rng = random.Random()
    return [Murcielago(rng, zona_alto, primera_vez=True) for _ in range(cantidad)]
 
 
def dibujar_murcielagos(superficie, lista, dt, t):
 
    for m in lista:
        m.actualizar(dt, t)
        m.dibujar(superficie, t)
 
 
# ---------------------------
# INICIAR (después de pygame.display.set_mode)
# ---------------------------
 
def iniciar():
 
    global cielo, niebla, vineta, brillo_vela, brillo_frasco, murcielagos
 
    fuentes["titulo"] = pygame.font.SysFont("oldenglishtextmt,chiller,georgia,timesnewroman,serif", 72, bold=False)
    fuentes["titulo_chico"] = pygame.font.SysFont("oldenglishtextmt,chiller,georgia,timesnewroman,serif", 30)
    fuentes["grande"] = pygame.font.SysFont("georgia,timesnewroman,serif", 46, bold=True)
    fuentes["normal"] = pygame.font.SysFont("georgia,timesnewroman,serif", 22)
    fuentes["chica"] = pygame.font.SysFont("arial", 18)
 
    cielo = crear_cielo()
    niebla = crear_niebla()
    vineta = crear_vineta()
    brillo_vela = crear_brillo(40, (140, 80, 20))
    brillo_frasco = crear_brillo(26, (150, 10, 25))
    cargar_gotas()
    murcielagos = crear_murcielagos(6, 330)
 
 
# ---------------------------
# LABERINTO
# ---------------------------
 
def generar_rejilla(rng, aberturas_extra=5):
    """
    Crea un laberinto perfecto (siempre tiene solución) usando
    el algoritmo de 'backtracking'. Cada celda es de 2x2 bloques
    y las paredes son de 1 bloque, así los pasillos son anchos.
    1 = pared, 0 = piso
    """
 
    rejilla = [[1] * COLUMNAS for _ in range(FILAS)]
    conexiones = {}
 
    def abrir_celda(cx, cy):
        for dy in (1, 2):
            for dx in (1, 2):
                rejilla[cy * 3 + dy][cx * 3 + dx] = 0
 
    def romper_pared(cx, cy, dx, dy):
        if dx != 0:
            x = cx * 3 + 3 if dx == 1 else cx * 3
            for dy2 in (1, 2):
                rejilla[cy * 3 + dy2][x] = 0
        else:
            y = cy * 3 + 3 if dy == 1 else cy * 3
            for dx2 in (1, 2):
                rejilla[y][cx * 3 + dx2] = 0
 
        conexiones.setdefault((cx, cy), set()).add((cx + dx, cy + dy))
        conexiones.setdefault((cx + dx, cy + dy), set()).add((cx, cy))
 
    visitadas = {(0, 0)}
    pila = [(0, 0)]
    abrir_celda(0, 0)
 
    while pila:
        cx, cy = pila[-1]
 
        vecinos = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < CELDAS_X and 0 <= ny < CELDAS_Y and (nx, ny) not in visitadas:
                vecinos.append((nx, ny, dx, dy))
 
        if not vecinos:
            pila.pop()
            continue
 
        nx, ny, dx, dy = rng.choice(vecinos)
        romper_pared(cx, cy, dx, dy)
        abrir_celda(nx, ny)
        visitadas.add((nx, ny))
        pila.append((nx, ny))
 
    # Algunas aberturas extra para que haya más de un camino
    intentos = 0
    while aberturas_extra > 0 and intentos < 200:
        intentos += 1
        cx = rng.randrange(CELDAS_X)
        cy = rng.randrange(CELDAS_Y)
        dx, dy = rng.choice(((1, 0), (0, 1)))
        nx, ny = cx + dx, cy + dy
        if nx < CELDAS_X and ny < CELDAS_Y and (nx, ny) not in conexiones.get((cx, cy), set()):
            romper_pared(cx, cy, dx, dy)
            aberturas_extra -= 1
 
    return rejilla, conexiones
 
 
def distancias_desde(conexiones, inicio):
 
    distancias = {inicio: 0}
    cola = [inicio]
 
    while cola:
        actual = cola.pop(0)
        for vecino in conexiones.get(actual, ()):
            if vecino not in distancias:
                distancias[vecino] = distancias[actual] + 1
                cola.append(vecino)
 
    return distancias
 
 
def centro_celda(cx, cy):
 
    return (
        (cx * 3 + 2) * TILE,
        OFFSET_Y + (cy * 3 + 2) * TILE
    )
 
 
class Laberinto:
 
    def __init__(self, semilla=None):
 
        rng = random.Random(semilla)
 
        self.rejilla, conexiones = generar_rejilla(rng)
 
        # Inicio arriba a la izquierda, puerta abajo a la derecha
        celda_inicio = (0, 0)
        celda_puerta = (CELDAS_X - 1, CELDAS_Y - 1)
 
        self.inicio = centro_celda(*celda_inicio)
 
        px, py = centro_celda(*celda_puerta)
        self.puerta = pygame.Rect(0, 0, 44, 56)
        self.puerta.midbottom = (px, py + TILE - 2)
 
        # Frascos de sangre: celdas lejanas y separadas entre sí
        distancias = distancias_desde(conexiones, celda_inicio)
        candidatas = [
            c for c in distancias
            if c not in (celda_inicio, celda_puerta) and distancias[c] >= 3
        ]
        rng.shuffle(candidatas)
        candidatas.sort(key=lambda c: len(conexiones.get(c, ())))  # callejones sin salida primero
 
        elegidas = []
        for c in candidatas:
            if all(abs(c[0] - e[0]) + abs(c[1] - e[1]) >= 3 for e in elegidas):
                elegidas.append(c)
            if len(elegidas) == 3:
                break
 
        for c in candidatas:
            if len(elegidas) == 3:
                break
            if c not in elegidas:
                elegidas.append(c)
 
        self.objetos = []
        for c in elegidas:
            rect = pygame.Rect(0, 0, 22, 26)
            rect.center = centro_celda(*c)
            self.objetos.append(rect)
 
        # Paredes como rectángulos para las colisiones
        self.paredes = []
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if self.rejilla[fila][col] == 1:
                    self.paredes.append(
                        pygame.Rect(col * TILE, OFFSET_Y + fila * TILE, TILE, TILE)
                    )
 
        # Velas sobre las paredes que dan al piso
        posibles_velas = []
        for fila in range(FILAS - 1):
            for col in range(1, COLUMNAS - 1):
                if self.rejilla[fila][col] == 1 and self.rejilla[fila + 1][col] == 0:
                    posibles_velas.append((col * TILE, OFFSET_Y + fila * TILE))
 
        rng.shuffle(posibles_velas)
        self.velas = [(x, y, rng.uniform(0, 6.28)) for x, y in posibles_velas[:10]]
 
        self.superficie = self.dibujar_estatico(rng)
 
    def es_pared(self, col, fila):
 
        if 0 <= col < COLUMNAS and 0 <= fila < FILAS:
            return self.rejilla[fila][col] == 1
        return False
 
    def dibujar_estatico(self, rng):
 
        superficie = cielo.copy()
 
        # Piso de piedra semitransparente (se ve la luna detrás)
        piso = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
 
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if self.rejilla[fila][col] == 0:
                    x = col * TILE
                    y = OFFSET_Y + fila * TILE
                    v = rng.randint(-5, 5)
                    pygame.draw.rect(piso, (26 + v, 18 + v, 32 + v, 185), (x, y, TILE, TILE))
                    pygame.draw.rect(piso, (44, 30, 52, 185), (x, y, TILE, TILE), 1)
 
                    # Grietas
                    if rng.random() < 0.12:
                        x1 = x + rng.randint(4, 28)
                        y1 = y + rng.randint(4, 28)
                        pygame.draw.line(piso, (14, 8, 18, 200), (x1, y1), (x1 + rng.randint(-8, 8), y1 + rng.randint(-8, 8)))
 
                    # Sombra de la pared de arriba
                    if self.es_pared(col, fila - 1):
                        for i in range(10):
                            pygame.draw.line(piso, (0, 0, 0, 120 - i * 12), (x, y + i), (x + TILE, y + i))
 
        superficie.blit(piso, (0, 0))
 
        # Paredes de ladrillo gótico
        for fila in range(FILAS):
            for col in range(COLUMNAS):
                if self.rejilla[fila][col] != 1:
                    continue
 
                x = col * TILE
                y = OFFSET_Y + fila * TILE
 
                pygame.draw.rect(superficie, (34, 26, 40), (x, y, TILE, TILE))
 
                for hilera in range(2):
                    desplaz = 0 if (fila + hilera) % 2 == 0 else TILE // 4
                    for b in range(-1, 3):
                        bx = x + b * (TILE // 2) + desplaz
                        by = y + hilera * (TILE // 2)
                        ladrillo = pygame.Rect(bx + 1, by + 1, TILE // 2 - 2, TILE // 2 - 2)
                        ladrillo = ladrillo.clip(pygame.Rect(x, y, TILE, TILE))
                        if ladrillo.width > 0:
                            v = rng.randint(-8, 8)
                            pygame.draw.rect(superficie, (60 + v, 50 + v, 70 + v), ladrillo)
 
                # Borde iluminado arriba
                if not self.es_pared(col, fila - 1) and fila > 0:
                    pygame.draw.line(superficie, (110, 90, 125), (x, y), (x + TILE - 1, y), 2)
 
                # Sangre escurriendo hacia el piso
                if fila < FILAS - 1 and not self.es_pared(col, fila + 1) and rng.random() < 0.3:
                    gx = x + rng.randint(5, TILE - 6)
                    largo = rng.randint(4, 12)
                    pygame.draw.line(superficie, (120, 8, 22), (gx, y + TILE - 3), (gx, y + TILE + largo), 2)
                    pygame.draw.circle(superficie, (150, 10, 28), (gx, y + TILE + largo), 2)
 
        return superficie
 
 
# ---------------------------
# DIBUJO DEL JUEGO
# ---------------------------
 
def dibujar_fondo_juego(pantalla, laberinto, t):
 
    pantalla.blit(laberinto.superficie, (0, 0))
 
    # Velas con fuego que parpadea
    for x, y, fase in laberinto.velas:
        parpadeo = math.sin(t * 9 + fase) * 0.5 + math.sin(t * 23 + fase * 2) * 0.3
 
        tam = int(68 + parpadeo * 10)
        brillo = pygame.transform.smoothscale(brillo_vela, (tam, tam))
        pantalla.blit(
            brillo,
            (x + 16 - tam // 2, y + 8 - tam // 2),
            special_flags=pygame.BLEND_RGB_ADD
        )
 
        pygame.draw.rect(pantalla, (225, 215, 195), (x + 13, y + 12, 6, 14))
        pygame.draw.rect(pantalla, (190, 180, 160), (x + 17, y + 12, 2, 14))
        pygame.draw.ellipse(pantalla, (255, 170, 40), (x + 13, int(y + 3 - parpadeo * 2), 6, int(10 + parpadeo * 2)))
        pygame.draw.ellipse(pantalla, (255, 240, 180), (x + 15, y + 7, 2, 5))
 
 
def dibujar_frascos(pantalla, objetos, t):
 
    for i, objeto in enumerate(objetos):
        cx = objeto.centerx
        cy = objeto.centery + int(math.sin(t * 3 + i * 2) * 3)
 
        pantalla.blit(
            brillo_frasco,
            (cx - 26, cy - 26),
            special_flags=pygame.BLEND_RGB_ADD
        )
 
        dibujar_icono_frasco(pantalla, cx, cy, lleno=True, grande=True)
 
 
def dibujar_icono_frasco(superficie, cx, cy, lleno=True, grande=False):
 
    # Gota de sangre (assets/objetos/gota.png)
    if gota_grande is not None:
        if lleno:
            imagen = gota_grande if grande else gota_chica
        else:
            imagen = gota_vacia
        superficie.blit(imagen, imagen.get_rect(center=(cx, cy)))
        return
 
    # Si no está la imagen, se dibuja un frasco simple
    if lleno:
        pygame.draw.circle(superficie, (50, 5, 12), (cx, cy + 4), 10)
        pygame.draw.circle(superficie, (190, 15, 35), (cx, cy + 4), 8)
        pygame.draw.rect(superficie, (200, 200, 220), (cx - 3, cy - 8, 6, 8))
        pygame.draw.rect(superficie, (120, 75, 40), (cx - 4, cy - 12, 8, 5))
    else:
        pygame.draw.circle(superficie, (90, 80, 100), (cx, cy + 4), 8, 2)
        pygame.draw.rect(superficie, (90, 80, 100), (cx - 3, cy - 8, 6, 8), 1)
 
 
def cargar_gotas():
 
    global gota_grande, gota_chica, gota_vacia
 
    try:
        gota = pygame.image.load("assets/objetos/gota.png").convert_alpha()
    except (pygame.error, FileNotFoundError) as error:
        print("No se encontró assets/objetos/gota.png, se usará un frasco:", error)
        return
 
    # scale (no smoothscale) para que el pixel art se vea nítido
    gota_grande = pygame.transform.scale(gota, (27, 36))
    gota_chica = pygame.transform.scale(gota, (18, 24))
 
    # Versión apagada para las gotas que aún no recoges
    gota_vacia = gota_chica.copy()
    gota_vacia.fill((70, 60, 80, 255), special_flags=pygame.BLEND_RGBA_MULT)
    gota_vacia.set_alpha(150)
 
 
def dibujar_puerta(pantalla, puerta, abierta, t):
 
    x, y, w, h = puerta
 
    # Marco de piedra
    pygame.draw.rect(pantalla, (75, 65, 85), (x - 5, y + 14, w + 10, h - 12))
    pygame.draw.ellipse(pantalla, (75, 65, 85), (x - 5, y - 5, w + 10, 40))
 
    if abierta:
        pulso = (math.sin(t * 4) + 1) / 2
 
        brillo = crear_brillo(50, (int(90 + 60 * pulso), 20, int(100 + 50 * pulso)))
        pantalla.blit(brillo, (x + w // 2 - 50, y + h // 2 - 50), special_flags=pygame.BLEND_RGB_ADD)
 
        color = (int(60 + 60 * pulso), 10, int(80 + 50 * pulso))
        pygame.draw.rect(pantalla, color, (x, y + 16, w, h - 16))
        pygame.draw.ellipse(pantalla, color, (x, y, w, 34))
 
        # Flecha que salta
        fy = y - 22 + int(math.sin(t * 6) * 4)
        pygame.draw.polygon(pantalla, (120, 255, 150), [(x + w // 2 - 8, fy), (x + w // 2 + 8, fy), (x + w // 2, fy + 10)])
    else:
        madera = (70, 22, 26)
        pygame.draw.rect(pantalla, madera, (x, y + 16, w, h - 16))
        pygame.draw.ellipse(pantalla, madera, (x, y, w, 34))
 
        for i in range(1, 4):
            lx = x + i * w // 4
            pygame.draw.line(pantalla, (45, 12, 16), (lx, y + 4), (lx, y + h - 1), 2)
 
        pygame.draw.rect(pantalla, (40, 40, 48), (x, y + 22, w, 4))
        pygame.draw.rect(pantalla, (40, 40, 48), (x, y + h - 14, w, 4))
 
        # Candado
        pygame.draw.circle(pantalla, (200, 160, 50), (x + w // 2, y + 33), 6, 2)
        pygame.draw.rect(pantalla, (200, 160, 50), (x + w // 2 - 7, y + 34, 14, 11))
        pygame.draw.rect(pantalla, (60, 40, 10), (x + w // 2 - 1, y + 37, 2, 5))
 
 
def dibujar_efectos(pantalla, t, dt):
 
    # Niebla que se mueve
    desplazamiento = int(t * 18) % ANCHO
    pantalla.blit(niebla, (-desplazamiento, 0))
 
    # Algunos murciélagos
    dibujar_murcielagos(pantalla, murcielagos[:2], dt, t)
 
    # Bordes oscuros
    pantalla.blit(vineta, (0, 0))
 
 
def dibujar_hud(pantalla, recogidos, segundos, mensaje):
 
    panel = pygame.Surface((ANCHO, OFFSET_Y), pygame.SRCALPHA)
    panel.fill((8, 3, 12, 215))
    pantalla.blit(panel, (0, 0))
    pygame.draw.line(pantalla, ROJO_SANGRE, (0, OFFSET_Y - 2), (ANCHO, OFFSET_Y - 2), 2)
 
    titulo = fuentes["titulo_chico"].render("Vampire Escape", True, ROJO_CLARO)
    pantalla.blit(titulo, (16, 6))
 
    # Frascos recogidos
    texto = fuentes["chica"].render("Sangre:", True, BLANCO_HUESO)
    pantalla.blit(texto, (330, 14))
    for i in range(3):
        dibujar_icono_frasco(pantalla, 410 + i * 28, 22, lleno=i < recogidos)
 
    # Tiempo
    minutos = int(segundos) // 60
    seg = int(segundos) % 60
    texto_tiempo = fuentes["chica"].render(f"Tiempo: {minutos:02d}:{seg:02d}", True, BLANCO_HUESO)
    pantalla.blit(texto_tiempo, (ANCHO - texto_tiempo.get_width() - 20, 14))
 
    # Mensaje de ayuda
    if recogidos < 3:
        ayuda = "Encuentra las 3 gotas de sangre para abrir la puerta"
        color = GRIS
    else:
        ayuda = "¡La puerta está abierta! Corre hacia la salida"
        color = (120, 255, 150)
 
    texto_centrado(pantalla, ayuda, fuentes["chica"], color, ANCHO // 2, 48)
 
    # Aviso temporal en el centro
    if mensaje:
        caja = fuentes["normal"].render(mensaje, True, BLANCO_HUESO)
        rect = caja.get_rect(center=(ANCHO // 2, ALTO // 2))
        fondo = pygame.Surface((rect.width + 40, rect.height + 20), pygame.SRCALPHA)
        fondo.fill((10, 3, 14, 210))
        pantalla.blit(fondo, (rect.x - 20, rect.y - 10))
        pygame.draw.rect(pantalla, ROJO_SANGRE, (rect.x - 20, rect.y - 10, rect.width + 40, rect.height + 20), 2)
        pantalla.blit(caja, rect)
 
 
# ---------------------------
# PANTALLA DE INICIO
# ---------------------------
 
def dibujar_inicio(pantalla, t, dt, progreso_mano, retrato=None):
 
    pantalla.blit(cielo, (0, 0))
    pantalla.blit(niebla, (-(int(t * 18) % ANCHO), 0))
    dibujar_murcielagos(pantalla, murcielagos, dt, t)
    pantalla.blit(vineta, (0, 0))
 
    titulo_con_brillo(pantalla, "Vampire Escape", fuentes["titulo"], ANCHO // 2, 40)
 
    # Panel con la historia
    panel = pygame.Rect(200, 170, 560, 270)
    fondo = pygame.Surface(panel.size, pygame.SRCALPHA)
    fondo.fill((10, 3, 14, 205))
    pantalla.blit(fondo, panel.topleft)
    pygame.draw.rect(pantalla, ROJO_SANGRE, panel, 2)
 
    lineas = [
        ("El sol está por salir y el Conde quedó", BLANCO_HUESO),
        ("atrapado en el laberinto del castillo.", BLANCO_HUESO),
        ("", None),
        ("Recoge las 3 gotas de sangre para abrir", BLANCO_HUESO),
        ("la puerta y escapa antes del amanecer.", BLANCO_HUESO),
        ("", None),
        ("Controles: flechas del teclado o", GRIS),
        ("mueve tu mano frente a la cámara.", GRIS),
    ]
 
    y = panel.y + 18
    for texto, color in lineas:
        if texto:
            texto_centrado(pantalla, texto, fuentes["normal"], color, panel.centerx, y)
        y += 29
 
    # Retrato del vampiro
    if retrato is not None:
        flotar = int(math.sin(t * 2) * 5)
        pantalla.blit(retrato, (30, 260 + flotar))
 
    # Texto que parpadea
    if int(t * 2) % 2 == 0:
        texto_centrado(
            pantalla,
            "Presiona ESPACIO o levanta la mano para comenzar",
            fuentes["normal"],
            ROJO_CLARO,
            panel.centerx,
            465
        )
 
    # Barra de progreso cuando la mano está arriba
    if progreso_mano > 0:
        barra = pygame.Rect(panel.centerx - 150, 505, 300, 12)
        pygame.draw.rect(pantalla, (40, 20, 40), barra)
        lleno = barra.copy()
        lleno.width = int(barra.width * min(progreso_mano, 1))
        pygame.draw.rect(pantalla, ROJO_SANGRE, lleno)
        pygame.draw.rect(pantalla, BLANCO_HUESO, barra, 1)
 
 
# ---------------------------
# PANTALLA DE VICTORIA
# ---------------------------
 
def dibujar_victoria(pantalla, t, dt, segundos, progreso_mano):
 
    pantalla.blit(cielo, (0, 0))
 
    # Amanecer: el cielo se aclara poco a poco
    amanecer = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    k = min(1, t / 6)
    for y in range(ALTO // 2, ALTO, 4):
        a = int(90 * k * (y - ALTO // 2) / (ALTO // 2))
        pygame.draw.rect(amanecer, (255, 140, 60, a), (0, y, ANCHO, 4))
    pantalla.blit(amanecer, (0, 0))
 
    dibujar_murcielagos(pantalla, murcielagos, dt, t)
    pantalla.blit(vineta, (0, 0))
 
    titulo_con_brillo(pantalla, "¡Escapaste!", fuentes["titulo"], ANCHO // 2, 150)
 
    minutos = int(segundos) // 60
    seg = int(segundos) % 60
    texto_centrado(pantalla, f"Tiempo: {minutos:02d}:{seg:02d}", fuentes["normal"], BLANCO_HUESO, ANCHO // 2, 260)
    texto_centrado(pantalla, "El Conde llegó a su ataúd antes del amanecer.", fuentes["normal"], GRIS, ANCHO // 2, 300)
 
    if int(t * 2) % 2 == 0:
        texto_centrado(pantalla, "Presiona R o levanta la mano para jugar otra vez", fuentes["normal"], ROJO_CLARO, ANCHO // 2, 380)
 
    texto_centrado(pantalla, "ESC para salir", fuentes["chica"], GRIS, ANCHO // 2, 420)
 
    if progreso_mano > 0:
        barra = pygame.Rect(ANCHO // 2 - 150, 455, 300, 12)
        pygame.draw.rect(pantalla, (40, 20, 40), barra)
        lleno = barra.copy()
        lleno.width = int(barra.width * min(progreso_mano, 1))
        pygame.draw.rect(pantalla, ROJO_SANGRE, lleno)
        pygame.draw.rect(pantalla, BLANCO_HUESO, barra, 1)