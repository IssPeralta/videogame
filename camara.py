import cv2
import mediapipe as mp
import time

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(
        model_asset_path="hand_landmarker.task"
    ),
    running_mode=VisionRunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)

camara = cv2.VideoCapture(0)

detector = HandLandmarker.create_from_options(options)


def obtener_direccion_mano():

    exito, imagen = camara.read()

    if not exito:
        return "quieto"

    imagen = cv2.flip(imagen, 1)

    imagen_rgb = cv2.cvtColor(
        imagen,
        cv2.COLOR_BGR2RGB
    )

    imagen_mp = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=imagen_rgb
    )

    tiempo_ms = int(time.time() * 1000)

    resultado = detector.detect_for_video(
        imagen_mp,
        tiempo_ms
    )

    alto, ancho, _ = imagen.shape

    centro_x = ancho // 2
    centro_y = alto // 2

    margen_x = 100
    margen_y = 80

    direccion = "quieto"

    if resultado.hand_landmarks:

        mano = resultado.hand_landmarks[0]

        muñeca = mano[0]

        mano_x = int(muñeca.x * ancho)
        mano_y = int(muñeca.y * alto)

        if mano_x < centro_x - margen_x:
            direccion = "izquierda"

        elif mano_x > centro_x + margen_x:
            direccion = "derecha"

        elif mano_y < centro_y - margen_y:
            direccion = "arriba"

        elif mano_y > centro_y + margen_y:
            direccion = "abajo"

    cv2.imshow(
        "Control por mano",
        imagen
    )

    cv2.waitKey(1)

    return direccion


def cerrar_camara():

    camara.release()
    detector.close()
    cv2.destroyAllWindows()