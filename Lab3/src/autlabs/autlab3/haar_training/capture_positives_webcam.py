#!/usr/bin/env python3
"""
Actividad 3 - Paso 2: Capturar 30 imágenes POSITIVAS del objeto
desde la WEBCAM (vida real) o desde un archivo de video.

El script muestra la imagen en vivo y te permite:
  - ESPACIO → guardar la foto actual
  - Q / ESC → salir

Las fotos se guardan en positives/raw/ para luego anotarlas.

Uso:
    python3 capture_positives_webcam.py

IMPORTANTE: 
    - Coloca el objeto frente a la cámara y muévelo ligeramente
      entre fotos para tener variedad (distancia, ángulo, luz).
    - Con 30 fotos variadas el clasificador será más robusto.
"""
import cv2
import os

CARPETA_RAW = os.path.join(os.path.dirname(__file__), 'positives', 'raw')
META        = 30

os.makedirs(CARPETA_RAW, exist_ok=True)

# Intentamos abrir la webcam (índice 0 = primera cámara disponible)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print('❌ No se encontró webcam. Prueba con índice 1 o 2:')
    print('   cap = cv2.VideoCapture(1)')
    exit(1)

print('📷 Webcam abierta correctamente')
print(f'🎯 Objetivo: capturar {META} imágenes del objeto')
print('   ESPACIO → guardar foto')
print('   Q / ESC → salir')

contador = 0

# Cuántas fotos ya tenemos de sesiones anteriores
existentes = len([f for f in os.listdir(CARPETA_RAW) if f.endswith('.jpg')])
if existentes > 0:
    print(f'   Ya hay {existentes} fotos de sesiones anteriores')
    contador = existentes

while True:
    ret, frame = cap.read()
    if not ret:
        print('❌ Error leyendo frame')
        break

    # Overlay informativo en la imagen
    texto = f'Fotos: {contador}/{META}  |  ESPACIO=guardar  Q=salir'
    cv2.putText(frame, texto, (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    # Resalta el centro con una guía para centrar el objeto
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2
    cv2.rectangle(frame, (cx-100, cy-100), (cx+100, cy+100), (0, 255, 255), 2)
    cv2.putText(frame, 'Centra el objeto aqui', (cx-95, cy-110),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)

    cv2.imshow('Captura de Positivos — Actividad 3', frame)

    tecla = cv2.waitKey(1) & 0xFF

    if tecla == ord(' '):  # ESPACIO → guardar
        nombre = os.path.join(CARPETA_RAW, f'pos_{contador:03d}.jpg')
        # Guardamos el frame SIN los overlays (el frame original)
        ret2, frame2 = cap.read()
        cv2.imwrite(nombre, frame2 if ret2 else frame)
        contador += 1
        print(f'  ✅ Foto {contador}/{META} guardada → {nombre}')

        if contador >= META:
            print(f'\n🎉 ¡{META} fotos capturadas! Ahora ejecuta annotate.py')
            break

    elif tecla in [ord('q'), ord('Q'), 27]:  # Q o ESC → salir
        print(f'\nSaliendo. Fotos capturadas: {contador}')
        break

cap.release()
cv2.destroyAllWindows()
