#!/usr/bin/env python3
"""
Actividad 3 - Paso 1: Generar 30 imágenes NEGATIVAS
Las imágenes negativas son fondos SIN el objeto que queremos detectar.

Genera texturas variadas: colores sólidos, degradados, ruido,
y patrones simples para que el clasificador aprenda que esas
texturas NO son el objeto.

Uso:
    python3 gen_negatives.py

Resultado:
    Crea la carpeta negatives/ con 30 imágenes .jpg
    y el archivo negatives.txt que necesita opencv_traincascade
"""
import cv2
import numpy as np
import os

CARPETA = os.path.join(os.path.dirname(__file__), 'negatives')
ANCHO, ALTO = 640, 480
TOTAL = 30

os.makedirs(CARPETA, exist_ok=True)

def guardar(imagen, i):
    nombre = os.path.join(CARPETA, f'neg_{i:03d}.jpg')
    cv2.imwrite(nombre, imagen)
    print(f'  Guardada: {nombre}')
    return nombre

archivos = []
i = 0

# ------------------------------------------------------------------
# 1. Colores sólidos (6 imágenes)
colores = [
    (60, 60, 60),     # gris oscuro
    (200, 200, 200),  # gris claro
    (30, 80, 40),     # verde oliva
    (80, 40, 30),     # marrón
    (40, 40, 80),     # azul oscuro
    (200, 180, 160),  # beige
]
for color in colores:
    img = np.full((ALTO, ANCHO, 3), color, dtype=np.uint8)
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# 2. Degradados horizontales (5 imágenes)
for c in range(5):
    img = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
    for x in range(ANCHO):
        val = int(x / ANCHO * 255)
        img[:, x] = [val, (c * 50 + val) % 256, (255 - val)]
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# 3. Degradados verticales (5 imágenes)
for c in range(5):
    img = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
    for y in range(ALTO):
        val = int(y / ALTO * 255)
        img[y, :] = [(val + c * 40) % 256, val, 255 - val]
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# 4. Ruido aleatorio (5 imágenes) — simula superficies rugosas
for _ in range(5):
    img = np.random.randint(80, 180, (ALTO, ANCHO, 3), dtype=np.uint8)
    # Suavizamos un poco para que no sea demasiado ruidoso
    img = cv2.GaussianBlur(img, (5, 5), 0)
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# 5. Cuadrícula / patrón de tablero (4 imágenes)
for tam in [20, 40, 60, 80]:
    img = np.zeros((ALTO, ANCHO, 3), dtype=np.uint8)
    for y in range(0, ALTO, tam):
        for x in range(0, ANCHO, tam):
            if ((y // tam) + (x // tam)) % 2 == 0:
                img[y:y+tam, x:x+tam] = [180, 180, 180]
            else:
                img[y:y+tam, x:x+tam] = [60, 60, 60]
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# 6. Líneas diagonales (5 imágenes) — simula piso/textura
for c in range(5):
    img = np.full((ALTO, ANCHO, 3), 150, dtype=np.uint8)
    separacion = 30 + c * 10
    for k in range(-ALTO, ANCHO + ALTO, separacion):
        cv2.line(img, (k, 0), (k + ALTO, ALTO), (100, 100, 100), 2)
    archivos.append(guardar(img, i)); i += 1

# ------------------------------------------------------------------
# Crear el archivo negatives.txt
txt = os.path.join(os.path.dirname(__file__), 'negatives.txt')
with open(txt, 'w') as f:
    for archivo in archivos:
        # La ruta debe ser relativa al directorio de haar_training/
        relativa = os.path.relpath(archivo, os.path.dirname(__file__))
        f.write(relativa + '\n')

print(f'\n✅ Generadas {len(archivos)} imágenes negativas en {CARPETA}/')
print(f'✅ Archivo de lista: {txt}')
