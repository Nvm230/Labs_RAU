# Labs de Robótica Autónoma - UTEC

Repositorio de los laboratoriosde Robótica Autónoma. 

workspaces de ROS 2 y los reportes en PDF de las prácticas desarrolladas a lo largo del curso. Los temas abarcan desde el control y lectura de sensores de un robot, hasta la implementación de visión computacional y el procesamiento de nubes de puntos en 3D.

## Estructura del repositorio

El repositorio está dividido por laboratorios. Cada carpeta es un workspace independiente de ROS 2 configurado con Python. A continuación, un resumen de lo que incluye cada uno, por ahora:

### [Lab 2: Control y Sensores](./Lab2/)
En este laboratorio exploramos las bases de ROS 2 para establecer la comunicación con el robot.
* **Componentes principales:** 
  * `newRobot_cmd.py`: Nodo encargado de enviar comandos de movimiento al robot.
  * `newRobot_sensors.py`: Nodo para procesar la lectura de los sensores.
  * `moteus_bridge.py`: Puente de comunicación con los controladores de motores moteus.
* **Reportes:** `Lab2_RAu.pdf`, `Act2_RAu.pdf`

### [Lab 3: Visión Computacional](./Lab3/)
En esta sección implementamos técnicas de visión computacional usando OpenCV para procesar imágenes de la cámara en tiempo real.
* **Componentes principales:**
  * `detect_ball.py`: Algoritmo para detectar y seguir una pelota basándose en su color.
  * `detect_haar.py`: Uso de cascadas de Haar para la detección de objetos o rostros.
  * `show_image.py` y `fotobot.py`: Nodos para suscribirse a los tópicos de la cámara y visualizar el entorno.
* **Reportes:** `Lab3_RAu.pdf`, `Act3_RAu.pdf`

### [Lab 4: Nubes de Puntos 3D (Point Clouds)](./Lab4/)
Este laboratorio se centra en la percepción 3D utilizando cámaras de profundidad (RGB-D) en entornos simulados de Gazebo, procesando la información con la librería PCL mediante Python.
* **Componentes principales:**
  * `nodo_depth.py` / `nodo_depth_pcl.py`: Nodos para capturar la data de la cámara de profundidad.
  * `submuestreo.py`: Filtro VoxelGrid para reducir la densidad de la nube de puntos.
  * `pass-through.py`: Filtro para recortar el espacio y conservar únicamente la zona de interés.
  * `segmentacion.py`: Uso de RANSAC para la detección de planos (como el piso o una mesa).
  * `clustering.py`: Segmentación y agrupación de objetos utilizando distancia Euclidiana.
  * `remocion-ruido.py`: Eliminación de ruido y puntos atípicos de la nube de puntos.
* **Reportes:** `Sem8_Lab4_RAu.pdf`, `Sem8_Act4_RAu.pdf`

## Stack Tecnológico
* ROS 2
* Python 3
* Gazebo (Simulación)
* OpenCV (Procesamiento de imágenes)
* PCL (Point Cloud Library)

## ¿Cómo ejecutar el código?

Dado que cada laboratorio cuenta con su propio workspace de ROS 2, para compilar y ejecutar los nodos (tomando como ejemplo el Lab 4) solo debes seguir estos pasos en tu terminal:

1. Ingresa a la carpeta del laboratorio:
   ```bash
   cd Lab4/
   ```
2. Compila el workspace utilizando colcon:
   ```bash
   colcon build
   ```
3. Ejecuta el archivo setup para que la terminal reconozca los paquetes:
   ```bash
   source install/setup.bash
   ```
4. Corre el nodo que deseas probar (por ejemplo, el de detección del Lab 3):
   ```bash
   ros2 run autlab3 detect_ball
   ```

---
*Desarrollado para el curso de Robótica Autónoma en UTEC.*
