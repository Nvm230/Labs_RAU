#!/usr/bin/env python3
import os

# Ruta a la carpeta raw
CARPETA = 'positives/raw'
ARCHIVOS = sorted([f for f in os.listdir(CARPETA) if f.endswith('.jpg')])

txt_path = 'positives.txt'

# Basado en la geometría actual:
# - El FOV es de 45.8° a 1m de distancia.
# - El robot ocupa aprox 224x105 píxeles en el centro.
# Coordenadas con un ligero margen de seguridad: x=180, y=160, ancho=280, alto=160

with open(txt_path, 'w') as f:
    for img in ARCHIVOS:
        ruta_relativa = os.path.join(CARPETA, img)
        # Formato: ruta num_objetos x y ancho alto
        f.write(f'{ruta_relativa} 1 180 160 280 160\n')

print(f'✅ Generado automáticamente {txt_path} con {len(ARCHIVOS)} imágenes.')
print('¡Te has saltado hacer los clics manuales!')
