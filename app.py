import re
import tempfile
from pathlib import Path

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(page_title="Archivo → Markdown", page_icon="📄", layout="centered")

st.title("📄 Archivo → Markdown")
st.markdown(
    "Sube un **PDF, Word (.docx) o PowerPoint (.pptx)** y conviértelo a Markdown. "
    "Conversión con [MarkItDown de Microsoft](https://github.com/microsoft/markitdown.git). "
    "**No necesitas ninguna API ni clave.**"
)

# Solo formatos que funcionan en local con los extras instalados.
# Se excluyen .doc/.xls (formatos legacy) e imágenes (sin LLM solo devuelven metadatos).
SUPPORTED = ["pdf", "docx", "pptx", "xlsx", "csv", "txt", "md", "html", "htm"]
MAX_MB = 50
MAX_BYTES = MAX_MB * 1024 * 1024
MAX_PREVIEW_CHARS = 50_000


def sanear_nombre(nombre: str, fallback: str = "documento") -> str:
    """Limpia el stem para usarlo como nombre de descarga."""
    limpio = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", nombre)
    limpio = re.sub(r"\s+", " ", limpio).strip().strip(".")
    limpio = limpio[:100]
    return limpio or fallback


uploaded = st.file_uploader(
    "Sube tu archivo",
    type=SUPPORTED,
    accept_multiple_files=False,
    help=f"Formatos: PDF, DOCX, PPTX, XLSX, CSV, TXT, MD, HTML. Máximo {MAX_MB} MB.",
)

@st.cache_resource
def get_converter() -> MarkItDown:
    return MarkItDown()

if uploaded is not None:
    if uploaded.size is not None and uploaded.size > MAX_BYTES:
        st.error(
            f"Archivo demasiado grande ({uploaded.size / 1024 / 1024:.1f} MB). "
            f"Máximo {MAX_MB} MB."
        )
        st.stop()

    ext = Path(uploaded.name).suffix.lower().lstrip(".")
    if ext not in SUPPORTED:
        st.error(f"Formato no soportado: .{ext}. Usa: {', '.join(SUPPORTED)}.")
        st.stop()
    suffix = f".{ext}"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    with st.spinner(f"Convirtiendo {uploaded.name}..."):
        try:
            converter = get_converter()
            result = converter.convert(tmp_path)
            md_text = result.text_content or ""
        except Exception:
            # Mensaje genérico: no exponer rutas /tmp ni trazas internas.
            st.error(
                "No se pudo convertir el archivo. Prueba con otro formato "
                "o revisa si es un PDF escaneado sin texto."
            )
            st.stop()
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass

    if not md_text.strip():
        st.warning(
            "El archivo se procesó pero no se extrajo texto. "
            "¿Es un PDF escaneado o una imagen sin OCR?"
        )
    else:
        chars = len(md_text)
        words = len(md_text.split())
        lines = md_text.count("\n") + 1
        c1, c2, c3 = st.columns(3)
        c1.metric("Caracteres", f"{chars:,}")
        c2.metric("Palabras", f"{words:,}")
        c3.metric("Líneas", f"{lines:,}")

        st.subheader("Vista previa")
        if chars > MAX_PREVIEW_CHARS:
            st.info(
                f"Vista previa truncada a {MAX_PREVIEW_CHARS:,} caracteres "
                f"de {chars:,}. La descarga contiene el texto completo."
            )
            preview = md_text[:MAX_PREVIEW_CHARS]
        else:
            preview = md_text
        st.text_area("Markdown generado", preview, height=350)

        st.download_button(
            label="⬇️ Descargar .md",
            data=md_text.encode("utf-8"),
            file_name=f"{sanear_nombre(Path(uploaded.name).stem)}.md",
            mime="text/markdown",
        )
else:
    st.info("👆 Sube un archivo para empezar. Ejemplo: `informe.pdf`, `tesis.docx`, `slides.pptx`.")

with st.expander("¿Necesito alguna API?"):
    st.markdown(
        "- **No.** Con esta configuración MarkItDown funciona sin internet ni claves.\n"
        "- Solo necesitas: `pip install -r requirements.txt`.\n"
        "- Nota: en Streamlit Cloud la conversión corre en el servidor, no en tu navegador. "
        "El archivo no se envía a APIs de terceros.\n"
        "- Opcional (solo si quieres OCR avanzado o audio): Azure Document Intelligence, OpenAI Whisper, etc. "
        "Para PDF/Word/PowerPoint normales no hace falta.\n"
        "- Imágenes sueltas y formatos legacy (.doc/.xls) no están soportados en esta app."
    )
