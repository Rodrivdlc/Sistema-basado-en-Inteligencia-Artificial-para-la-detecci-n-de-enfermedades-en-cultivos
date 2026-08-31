from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

from src.predict import predecir_imagen


app = FastAPI(
    title="API de detección de enfermedades en tomate",
    description="API para clasificar enfermedades en hojas de tomate mediante IA.",
    version="1.0.0"
)


# CORS
# Permite que el frontend pueda comunicarse con FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Traducción de nombres técnicos a nombres legibles
NOMBRES_ENFERMEDADES = {
    "Tomato_Bacterial_spot": "Mancha bacteriana",
    "Tomato_Early_blight": "Tizón temprano",
    "Tomato_Late_blight": "Tizón tardío",
    "Tomato_Leaf_Mold": "Moho de la hoja",
    "Tomato_Septoria_leaf_spot": "Mancha foliar por Septoria",
    "Tomato_Spider_mites_Two_spotted_spider_mite": "Ácaro de dos manchas",
    "Tomato__Target_Spot": "Mancha objetivo",
    "Tomato__Tomato_YellowLeaf__Curl_Virus": "Virus del rizado amarillo de la hoja",
    "Tomato__Tomato_mosaic_virus": "Virus del mosaico del tomate",
    "Tomato_healthy": "Sano"
}


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente",
        "modelo": "MobileNetV2 Fine-Tuned",
        "cultivo": "Tomate"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    # Tipos MIME permitidos
    tipos_permitidos = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail="El archivo debe ser una imagen JPG, JPEG, PNG o WEBP."
        )

    # Extensión original
    extension = Path(file.filename).suffix.lower()

    extensiones_permitidas = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp"
    }

    if extension not in extensiones_permitidas:
        raise HTTPException(
            status_code=400,
            detail="Extensión de archivo no permitida."
        )

    # Crear nombre temporal único
    nombre_temporal = f"{uuid.uuid4()}{extension}"

    ruta_temporal = Path(nombre_temporal)

    try:

        # Guardar temporalmente la imagen recibida
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        # Ejecutar predicción
        resultado = predecir_imagen(
            ruta_temporal
        )

        clase_tecnica = resultado["clase"]
        confianza = resultado["confianza"]

        enfermedad = NOMBRES_ENFERMEDADES.get(
            clase_tecnica,
            clase_tecnica
        )

        return {
            "cultivo": "Tomate",
            "enfermedad": enfermedad,
            "clase_tecnica": clase_tecnica,

            "confianza": round(
                confianza,
                4
            ),

            "confianza_porcentaje": round(
                confianza * 100,
                2
            )
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Error al procesar la imagen: {str(e)}"
        )

    finally:

        # Eliminar imagen temporal
        if ruta_temporal.exists():
            ruta_temporal.unlink()