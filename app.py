import tempfile
from pathlib import Path

import streamlit as st
from markitdown import MarkItDown

st.set_page_config(page_title="Archivo → Markdown", page_icon="📄", layout="centered")

st.title("📄 Archivo → Markdown")
st.markdown(
    "Sube un **PDF, Word (.docx) o PowerPoint (.pptx)** y conviértelo a Markdown. "
    "Conversión **100% local y gratis** con [MarkItDown de Microsoft](https://github.com/microsoft/markitdown.git). "
    "**No necesitas ninguna API ni clave.**"
)

SUPPORTED = ["pdf", "docx", "doc", "pptx", "xlsx", "xls", "csv", "txt", "md", "html", "htm", "png", "jpg", "jpeg"]

uploaded = st.file_uploader(
    "Sube tu archivo",
    type=SUPPORTED,
    accept_multiple_files=False,
    help="Formatos principales: PDF, DOCX, PPTX. También: XLSX, CSV, TXT, HTML, imágenes.",
)

@st.cache_resource
def get_converter() -> MarkItDown:
    return MarkItDown()

if uploaded is not None:
    suffix = Path(uploaded.name).suffix or ".tmp"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded.getbuffer())
        tmp_path = tmp.name

    with st.spinner(f"Convirtiendo {uploaded.name}..."):
        try:
            converter = get_converter()
            result = converter.convert(tmp_path)
            md_text = result.text_content or ""
        except Exception as e:
            st.error(f"No se pudo convertir: {e}")
            st.stop()
        finally:
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass

    if not md_text.strip():
        st.warning("El archivo se procesó pero no se extrajo texto.")
    else:
        chars = len(md_text)
        words = len(md_text.split())
        lines = md_text.count("\n") + 1
        c1, c2, c3 = st.columns(3)
        c1.metric("Caracteres", f"{chars:,}")
        c2.metric("Palabras", f"{words:,}")
        c3.metric("Líneas", f"{lines:,}")

        st.subheader("Vista previa")
        st.text_area("Markdown generado", md_text, height=350)

        st.download_button(
            label="⬇️ Descargar .md",
            data=md_text.encode("utf-8"),
            file_name=f"{Path(uploaded.name).stem}.md",
            mime="text/markdown",
        )
else:
    st.info("👆 Sube un archivo para empezar. Ejemplo: `informe.pdf`, `tesis.docx`, `slides.pptx`.")

with st.expander("¿Necesito alguna API?"):
    st.markdown(
        "- **No.** MarkItDown funciona en local, sin internet ni claves.\n"
        "- Solo necesitas: `pip install markitdown[pdf,docx,pptx]`.\n"
        "- Opcional (solo si quieres OCR avanzado o audio): Azure Document Intelligence, OpenAI Whisper, etc. "
        "Para PDF/Word/PowerPoint normales no hace falta."
    )
