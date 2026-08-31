import json
import numpy as np
import tensorflow as tf
from tensorflow import keras
from pathlib import Path


# Rutas relativas al proyecto
BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = BASE_DIR / "models" / "modelo_tomate_mobilenetv2_finetuned.keras"
CLASSES_PATH = BASE_DIR / "models" / "class_names.json"


# Cargar modelo
model = keras.models.load_model(MODEL_PATH)

# Cargar nombres de clases
with open(CLASSES_PATH, "r", encoding="utf-8") as f:
    class_names = json.load(f)


def predecir_imagen(ruta_imagen):
    img = tf.keras.utils.load_img(
        ruta_imagen,
        target_size=(224, 224)
    )

    img_array = tf.keras.utils.img_to_array(img)
    img_array = tf.expand_dims(img_array, axis=0)

    predicciones = model.predict(img_array, verbose=0)

    indice = int(np.argmax(predicciones[0]))
    confianza = float(predicciones[0][indice])

    return {
        "clase": class_names[indice],
        "confianza": confianza
    }


if __name__ == "__main__":
    ruta = BASE_DIR / "pruebas" / "1-29.png"

    resultado = predecir_imagen(ruta)

    print("Predicción:", resultado["clase"])
    print(f"Confianza: {resultado['confianza'] * 100:.2f}%")