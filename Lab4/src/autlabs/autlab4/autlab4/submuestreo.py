#!/usr/bin/env python3
import pcl
import sys

# Tamaño de voxel por defecto
voxel_size = 0.01

if len(sys.argv) > 1:
    voxel_size = float(sys.argv[1])

print(f"Usando voxel size: {voxel_size}")

# Cargar la nube de puntos sin color para evitar que se vea negro
cloud = pcl.load('camara_depth.pcd')

# Crear un filtro VoxelGrid para la nube de puntos
fvox = cloud.make_voxel_grid_filter()
fvox.set_leaf_size(voxel_size, voxel_size, voxel_size)

# Ejecutar el filtro
cloud_filtered = fvox.filter()

# Grabar el resultado en disco
filename = f'mesa_downsampled.pcd'
pcl.save(cloud_filtered, filename)
print(f"Guardado como: {filename} con {cloud_filtered.size} puntos.")
