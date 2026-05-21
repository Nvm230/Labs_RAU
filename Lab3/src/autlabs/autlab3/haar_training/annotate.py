#!/usr/bin/env python3
"""
Actividad 3 - Paso 3: Anotar las imágenes positivas
Dibuja el rectángulo de la región del objeto en cada foto
y genera el archivo positives.txt requerido por opencv_createsamples.

Uso:
    python3 annotate.py

Controles:
    - Clic izquierdo + arrastrar → dibujar rectángulo sobre el objeto
    - ENTER → guardar anotación y pasar a la siguiente foto
    - R     → reiniciar el rectángulo actual
    - Q     → salir (guarda el progreso)

Formato del archivo positives.txt:
    ruta_imagen.jpg  1  x y w h
    (el "1" indica que hay 1 objeto en la imagen)
"""
import cv2
import os

# ---- Rutas ----
BASE     = os.path.dirname(__file__)
RAW_DIR  = os.path.join(BASE, 'positives', 'raw')
ANN_FILE = os.path.join(BASE, 'positives.txt')

# Cargamos las fotos que aún no están anotadas
imagenes  = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('.jpg')])
anotadas  = set()
if os.path.exists(ANN_FILE):
    with open(ANN_FILE, 'r') as f:
        for linea in f:
            partes = linea.strip().split()
            if partes:
                anotadas.add(os.path.basename(partes[0]))

pendientes = [im for im in imagenes if im not in anotadas]
print(f'📝 {len(pendientes)} fotos pendientes de anotar (de {len(imagenes)} total)')

if not pendientes:
    print('✅ Todas las fotos ya están anotadas.')
    exit(0)

# ---- Variables globales para el callback del ratón ----
dibujando   = False
punto_ini   = (-1, -1)
punto_fin   = (-1, -1)
rect_listo  = False

def cb_raton(evento, x, y, flags, param):
    global dibujando, punto_ini, punto_fin, rect_listo
    if evento == cv2.EVENT_LBUTTONDOWN:
        dibujando  = True
        rect_listo = False
        punto_ini  = (x, y)
        punto_fin  = (x, y)
    elif evento == cv2.EVENT_MOUSEMOVE and dibujando:
        punto_fin = (x, y)
    elif evento == cv2.EVENT_LBUTTONUP:
        dibujando  = False
        punto_fin  = (x, y)
        rect_listo = True

# ---- Abrir el archivo de anotaciones en modo append ----
with open(ANN_FILE, 'a') as f_out:

    for nombre in pendientes:
        ruta = os.path.join(RAW_DIR, nombre)
        img_original = cv2.imread(ruta)

        if img_original is None:
            print(f'  ⚠️  No se pudo leer: {nombre}')
            continue

        ventana = f'Anotando: {nombre}'
        cv2.namedWindow(ventana)
        cv2.setMouseCallback(ventana, cb_raton)

        # Reset de variables
        punto_ini  = (-1, -1)
        punto_fin  = (-1, -1)
        rect_listo = False

        print(f'\n  Foto: {nombre}')
        print('  Dibuja un rectángulo alrededor del objeto → ENTER para guardar')

        guardado = False
        while True:
            img_display = img_original.copy()

            # Instrucciones sobre la imagen
            cv2.putText(img_display, 'Dibuja rect. → ENTER=guardar  R=reiniciar  Q=salir',
                        (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)

            # Dibujar el rectángulo actual
            if punto_ini != (-1, -1) and punto_fin != (-1, -1):
                color = (0, 255, 0) if rect_listo else (0, 200, 255)
                cv2.rectangle(img_display, punto_ini, punto_fin, color, 2)

            cv2.imshow(ventana, img_display)
            tecla = cv2.waitKey(20) & 0xFF

            if tecla == 13:  # ENTER → guardar
                if rect_listo:
                    x1 = min(punto_ini[0], punto_fin[0])
                    y1 = min(punto_ini[1], punto_fin[1])
                    x2 = max(punto_ini[0], punto_fin[0])
                    y2 = max(punto_ini[1], punto_fin[1])
                    w  = x2 - x1
                    h  = y2 - y1

                    if w > 10 and h > 10:  # rectángulo mínimo válido
                        ruta_rel = os.path.join('positives', 'raw', nombre)
                        linea    = f'{ruta_rel}  1  {x1} {y1} {w} {h}\n'
                        f_out.write(linea)
                        print(f'  ✅ Anotado: x={x1} y={y1} w={w} h={h}')
                        guardado = True
                        break
                    else:
                        print('  ⚠️  Rectángulo muy pequeño, dibuja de nuevo')
                else:
                    print('  ⚠️  Primero dibuja un rectángulo')

            elif tecla == ord('r'):  # R → reiniciar
                punto_ini  = (-1, -1)
                punto_fin  = (-1, -1)
                rect_listo = False

            elif tecla in [ord('q'), 27]:  # Q o ESC → salir
                print('\n  Guardando progreso y saliendo...')
                cv2.destroyAllWindows()
                exit(0)

        cv2.destroyWindow(ventana)

print(f'\n✅ Anotación completa. Archivo guardado: {ANN_FILE}')
print('   Siguiente paso: ejecuta train_cascade.sh')
