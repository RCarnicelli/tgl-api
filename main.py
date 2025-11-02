from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from tgl_core import generate_ascii_fretboard, generate_scale_svg

app = FastAPI(
    title="The Guitar Lab API",
    description="Gera diagramas ASCII e SVG de guitarra (triads, drops, escalas).",
    version="1.0.0"
)

@app.get("/")
def home():
    return {
        "message": "🎸 The Guitar Lab API está online!",
        "endpoints": ["/ascii", "/svg"]
    }

@app.get("/ascii")
def ascii_diagram(
    note: str = Query("C", description="Nota raiz (ex: C, D#, F...)"),
    scale: str = Query("major", description="Tipo de escala (major, minor, dorian, mixolydian...)")
):
    """
    Retorna um diagrama ASCII simples do braço com as notas da escala.
    """
    ascii_map = generate_ascii_fretboard(note, scale)
    return JSONResponse(content={
        "note": note,
        "scale": scale,
        "diagram_ascii": ascii_map
    })


@app.get("/svg")
def svg_scale(
    note: str = Query("C", description="Nota raiz (ex: C, D#, F...)"),
    scale: str = Query("major", description="Tipo de escala (major, minor, dorian, mixolydian...)")
):
    """
    Retorna um SVG com o braço da guitarra e as notas da escala.
    """
    svg_data = generate_scale_svg(note, scale)
    return JSONResponse(content={
        "note": note,
        "scale": scale,
        "svg": svg_data
    })
