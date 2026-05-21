#!/usr/bin/env python3
import pcl
import sys

# Cargar la nube de puntos sin color para evitar que se vea negro
cloud = pcl.load('mesa_downsampled.pcd')

# 1. Filtro: Eje Z (Profundidad respecto a la cámara)
passthrough_z = cloud.make_passthrough_filter()
passthrough_z.set_filter_field_name('z')
passthrough_z.set_filter_limits(0.5, 2.0)
cloud_z = passthrough_z.filter()

# 2. Filtro: Eje Y (Cortar el piso de abajo y arriba)
passthrough_y = cloud_z.make_passthrough_filter()
passthrough_y.set_filter_field_name('y')
passthrough_y.set_filter_limits(-0.4, 0.2)
cloud_y = passthrough_y.filter()

# 3. Filtro: Eje X (Cortar el piso de los lados)
passthrough_x = cloud_y.make_passthrough_filter()
passthrough_x.set_filter_field_name('x')
passthrough_x.set_filter_limits(-0.4, 0.4)
cloud_final = passthrough_x.filter()

# Grabar el resultado en disco
filename = 'mesa_pass.pcd'
pcl.save(cloud_final, filename)
print(f"Filtro de caja aplicado (X, Y, Z). Guardado como {filename} con {cloud_final.size} puntos.")