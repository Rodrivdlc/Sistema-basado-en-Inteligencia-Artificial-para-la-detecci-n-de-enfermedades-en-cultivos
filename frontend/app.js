const inputImagen = document.getElementById("imagen");
const preview = document.getElementById("preview");
const boton = document.getElementById("analizar");

const resultado = document.getElementById("resultado");

const cultivo = document.getElementById("cultivo");
const enfermedad = document.getElementById("enfermedad");
const confianza = document.getElementById("confianza");

const error = document.getElementById("error");


inputImagen.addEventListener("change", () => {

    const archivo = inputImagen.files[0];

    resultado.classList.add("hidden");
    error.textContent = "";

    if (!archivo) {
        preview.classList.add("hidden");
        return;
    }

    const url = URL.createObjectURL(archivo);

    preview.src = url;
    preview.classList.remove("hidden");
});


boton.addEventListener("click", async () => {

    const archivo = inputImagen.files[0];

    if (!archivo) {
        error.textContent = "Selecciona una imagen.";
        return;
    }

    boton.disabled = true;
    boton.textContent = "Analizando...";

    error.textContent = "";
    resultado.classList.add("hidden");

    const formData = new FormData();

    formData.append("file", archivo);

    try {

        const respuesta = await fetch(
            "http://127.0.0.1:8000/predict",
            {
                method: "POST",
                body: formData
            }
        );

        const datos = await respuesta.json();

        if (!respuesta.ok) {
            throw new Error(
                datos.detail || "Error al analizar la imagen."
            );
        }

        cultivo.textContent = datos.cultivo;
        enfermedad.textContent = datos.enfermedad;

        confianza.textContent =
            datos.confianza_porcentaje + "%";

        resultado.classList.remove("hidden");

    } catch (err) {

        error.textContent = err.message;

    } finally {

        boton.disabled = false;
        boton.textContent = "Analizar imagen";

    }

});