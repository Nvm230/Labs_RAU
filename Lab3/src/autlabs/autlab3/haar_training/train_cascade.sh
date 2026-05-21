#!/usr/bin/env bash
# =============================================================================
# Actividad 3 - Paso 4: Entrenar el clasificador Haar Cascade
# =============================================================================
# Ejecutar DESDE la carpeta haar_training/:
#     cd haar_training/
#     chmod +x train_cascade.sh
#     ./train_cascade.sh
#
# Requiere tener previamente:
#   - positives/raw/*.jpg  → 30 fotos del objeto
#   - positives.txt        → generado por annotate.py
#   - negatives/           → generado por gen_negatives.py
#   - negatives.txt        → generado por gen_negatives.py
# =============================================================================

set -e   # parar si algún comando falla

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================="
echo " ENTRENAMIENTO HAAR CASCADE — Lab 3 Act 3"
echo "============================================="

# ---- Verificar dependencias ----
if ! command -v docker &> /dev/null; then
    echo ""
    echo "❌ docker no encontrado."
    echo "   Se requiere Docker para ejecutar OpenCV 3.4."
    echo ""
    exit 1
fi

# ---- Parámetros del entrenamiento ----
NUM_POS=25         # imágenes positivas para entrenar (<=30, dejamos margen)
NUM_NEG=30         # imágenes negativas
NUM_STAGES=10      # número de etapas (más etapas = más preciso pero más lento)
W=24               # ancho de la ventana de detección (en píxeles)
H=24               # alto de la ventana de detección
SALIDA="cascade_output"

mkdir -p "$SALIDA"

echo ""
echo "📦 Paso 1: Crear muestras de entrenamiento (positivos.vec)..."
echo "   NUM_POS=$NUM_POS | Tamaño=$W x $H"

docker run --rm -u $(id -u):$(id -g) -v "$(pwd):/data" -w /data valian/docker-python-opencv-ffmpeg:py3 \
    opencv_createsamples \
    -info positives.txt \
    -num $NUM_POS \
    -w $W \
    -h $H \
    -vec positivos.vec

echo ""
echo "🧠 Paso 2: Entrenar el clasificador ($NUM_STAGES etapas)..."
echo "   Esto puede tardar varios minutos..."

docker run --rm -u $(id -u):$(id -g) -v "$(pwd):/data" -w /data valian/docker-python-opencv-ffmpeg:py3 \
    opencv_traincascade \
    -data "$SALIDA" \
    -vec positivos.vec \
    -bg negatives.txt \
    -numPos $NUM_POS \
    -numNeg $NUM_NEG \
    -numStages $NUM_STAGES \
    -w $W \
    -h $H \
    -featureType HAAR \
    -minHitRate 0.999 \
    -maxFalseAlarmRate 0.5

echo ""
echo "============================================="
echo "✅ Entrenamiento completado!"
echo "   Clasificador: $SALIDA/cascade.xml"
echo ""
echo "   Siguiente paso:"
echo "   ros2 run autlab3 detect_haar"
echo "============================================="
