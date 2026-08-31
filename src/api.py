from fastapi import FastAPI, UploadFile, File
from pathlib import Path
import shutil
import uuid

from src.predict import predecir_imagen


app = FastAPI(
    title="API de detección de enfermedades en tomate",
    version="1.0"
)


@app.get("/")
def inicio():
    return {
        "mensaje": "API funcionando correctamente"
    }


@app.post("/predict")
async def predict(file: UploadFile = File(...)):

    extension = Path(file.filename).suffix

    nombre_temporal = f"{uuid.uuid4()}{extension}"
    ruta_temporal = Path(nombre_temporal)

    with open(ruta_temporal, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        resultado = predecir_imagen(ruta_temporal)

        return {
            "archivo": file.filename,
            "clase": resultado["clase"],
            "confianza": resultado["confianza"]
        }

    finally:
        if ruta_temporal.exists():
            ruta_temporal.unlink()