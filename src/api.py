from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import uuid

from src.predict import predecir_imagen


app = FastAPI(
    title="API de detección de enfermedades en cultivos",
    description=(
        "Sistema basado en inteligencia artificial para "
        "identificar enfermedades en cultivos mediante imágenes."
    ),
    version="2.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


CLASES_INFO = {

    # PIMIENTO

    "Pepper__bell___Bacterial_spot": {
        "cultivo": "Pimiento",
        "enfermedad": "Mancha bacteriana"
    },

    "Pepper__bell___healthy": {
        "cultivo": "Pimiento",
        "enfermedad": "Sano"
    },


    # PATATA

    "Potato___Early_blight": {
        "cultivo": "Patata",
        "enfermedad": "Tizón temprano"
    },

    "Potato___Late_blight": {
        "cultivo": "Patata",
        "enfermedad": "Tizón tardío"
    },

    "Potato___healthy": {
        "cultivo": "Patata",
        "enfermedad": "Sano"
    },


    # TOMATE

    "Tomato_Bacterial_spot": {
        "cultivo": "Tomate",
        "enfermedad": "Mancha bacteriana"
    },

    "Tomato_Early_blight": {
        "cultivo": "Tomate",
        "enfermedad": "Tizón temprano"
    },

    "Tomato_Late_blight": {
        "cultivo": "Tomate",
        "enfermedad": "Tizón tardío"
    },

    "Tomato_Leaf_Mold": {
        "cultivo": "Tomate",
        "enfermedad": "Moho de la hoja"
    },

    "Tomato_Septoria_leaf_spot": {
        "cultivo": "Tomate",
        "enfermedad": "Mancha foliar por Septoria"
    },

    "Tomato_Spider_mites_Two_spotted_spider_mite": {
        "cultivo": "Tomate",
        "enfermedad": "Ácaro de dos manchas"
    },

    "Tomato__Target_Spot": {
        "cultivo": "Tomate",
        "enfermedad": "Mancha objetivo"
    },

    "Tomato__Tomato_YellowLeaf__Curl_Virus": {
        "cultivo": "Tomate",
        "enfermedad": "Virus del rizado amarillo de la hoja"
    },

    "Tomato__Tomato_mosaic_virus": {
        "cultivo": "Tomate",
        "enfermedad": "Virus del mosaico del tomate"
    },

    "Tomato_healthy": {
        "cultivo": "Tomate",
        "enfermedad": "Sano"
    }
}


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente",
        "modelo": "MobileNetV2 multicultivo Fine-Tuned",
        "cultivos": [
            "Tomate",
            "Patata",
            "Pimiento"
        ]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    tipos_permitidos = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }

    if file.content_type not in tipos_permitidos:
        raise HTTPException(
            status_code=400,
            detail=(
                "El archivo debe ser una imagen "
                "JPG, JPEG, PNG o WEBP."
            )
        )

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

    nombre_temporal = (
        f"{uuid.uuid4()}{extension}"
    )

    ruta_temporal = Path(nombre_temporal)

    try:
        with open(ruta_temporal, "wb") as buffer:
            shutil.copyfileobj(
                file.file,
                buffer
            )

        resultado = predecir_imagen(
            ruta_temporal
        )

        clase = resultado["clase"]
        confianza = resultado["confianza"]

        info = CLASES_INFO.get(clase)

        if info is None:
            raise HTTPException(
                status_code=500,
                detail=(
                    f"La clase '{clase}' "
                    "no está configurada en la API."
                )
            )

        return {
            "cultivo": info["cultivo"],
            "enfermedad": info["enfermedad"],
            "clase_tecnica": clase,
            "confianza": round(
                confianza,
                4
            ),
            "confianza_porcentaje": round(
                confianza * 100,
                2
            )
        }

    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()