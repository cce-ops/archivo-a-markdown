# Archivo → Markdown

Sube un **PDF, Word (.docx) o PowerPoint (.pptx)** y conviértelo a Markdown. Conversión con [MarkItDown](https://github.com/microsoft/markitdown.git) sin APIs ni claves. En Streamlit Cloud la conversión corre en el servidor, no se envía a terceros.

https://archivo-a-markdown.streamlit.app/

## Uso

```bash
pip install -r requirements.txt
streamlit run app.py
```

Abre http://localhost:8501

## Formatos

Principales: `pdf`, `docx`, `pptx`. También: `xlsx`, `csv`, `txt`, `md`, `html`. Límite: 50 MB.

No soportados: `doc`/`xls` legacy ni imágenes sueltas (sin LLM solo devuelven metadatos).
