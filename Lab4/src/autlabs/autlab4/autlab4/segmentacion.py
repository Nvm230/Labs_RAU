#!/usr/bin/env python3
import pcl
import sys

# Cargar la nube de puntos filtrada sin color
cloud = pcl.load('mesa_pass.pcd')

# Crear el objeto para la segmentación
seg = cloud.make_segmenter()

# Asignar el modelo que se desea ajustar
seg.set_model_type(pcl.SACMODEL_PLANE)
# Uso de RANSAC
seg.set_method_type(pcl.SAC_RANSAC)

# Máxima distancia
max_distance = 0.01
if len(sys.argv) > 1:
    max_distance = float(sys.argv[1])

print(f"Usando max_distance: {max_distance}")

seg.set_distance_threshold(max_distance)
# Función de segmentación con RANSAC para obtener los índices de los inliers
inliers, coefficients = seg.segment()

if len(inliers) == 0:
    print("No se encontraron inliers para el modelo de plano.")
    sys.exit(0)

# Extracción de inliers (la mesa plana)
cloud_inliers = cloud.extract(inliers, negative=False)
pcl.save(cloud_inliers, 'mesa_inliers.pcd')
print(f"Inliers guardados en mesa_inliers.pcd con {cloud_inliers.size} puntos.")

# Extracción de outliers (objetos sobre la mesa)
cloud_outliers = cloud.extract(inliers, negative=True)
pcl.save(cloud_outliers, 'mesa_outliers.pcd')
print(f"Outliers guardados en mesa_outliers.pcd con {cloud_outliers.size} puntos.")
