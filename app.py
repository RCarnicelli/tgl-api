from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
from fretboardgtr.fretboard import FretBoard
from fretboardgtr.notes_creators import ScaleFromName
import os

app = FastAPI(
    title="TGL Guitar Diagram API",
    description="Gera diagramas reais de acordes e escalas usando fretboardgtr 🎸",
    version="1.0.0",
)

# === Funções utilitárias ====================================

def export_diagram(fb: FretBoard, filename: str) -> str:
    """Exporta o diagrama e retorna o caminho"""
    file_path = f"{filename}.svg"
    fb.export(file_path, format="svg")
    return file_path

# === Endpoints ==============================================

@app.get("/")
def root():
    return {"message": "🎸 API da guitarra está rodando — by The Advancing Guitarist Lab"}


@app.get("/diagram")
def diagram(chord: str = Query(..., description="Nome do acorde (ex: C, G, Dm)")):
    """Gera diagrama real do acorde informado"""
    fb = FretBoard()

    shapes = {
        "C": [
            {"string": 6, "fret": "X"},
            {"string": 5, "fret": 3},
            {"string": 4, "fret": 2},
            {"string": 3, "fret": 0},
            {"string": 2, "fret": 1},
            {"string": 1, "fret": 0},
        ],
        "G": [
            {"string": 6, "fret": 3},
            {"string": 5, "fret": 2},
            {"string": 4, "fret": 0},
            {"string": 3, "fret": 0},
            {"string": 2, "fret": 0},
            {"string": 1, "fret": 3},
        ],
        "D": [
            {"string": 6, "fret": "X"},
            {"string": 5, "fret": "X"},
            {"string": 4, "fret": 0},
            {"string": 3, "fret": 2},
            {"string": 2, "fret": 3},
            {"string": 1, "fret": 2},
        ],
    }

    if chord not in shapes:
        return JSONResponse(
            status_code=404,
            content={"error": f"Acorde '{chord}' ainda não cadastrado."},
        )

    fb.add_notes(chord=shapes[chord])
    file_path = export_diagram(fb, f"{chord}_chord")

    return FileResponse(file_path, media_type="image/svg+xml", filename=f"{chord}_chord.svg")


@app.get("/scale")
def scale(
    root: str = Query(..., description="Nota raiz (ex: C, D#, F)"),
    mode: str = Query(..., description="Modo/escala (ex: Ionian, Dorian, Mixolydian, Minor)"),
):
    """Gera diagrama da escala ou modo informado"""
    fb = FretBoard()
    try:
        scale_obj = ScaleFromName(root=root, mode=mode).build()
        fb.add_notes(scale=scale_obj)
        file_path = export_diagram(fb, f"{root}_{mode}_scale")
        return FileResponse(file_path, media_type="image/svg+xml", filename=f"{root}_{mode}_scale.svg")
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

# ============================================================

@app.get("/cleanup")
def cleanup():
    """Remove arquivos SVG antigos do diretório"""
    deleted = []
    for f in os.listdir():
        if f.endswith(".svg"):
            os.remove(f)
            deleted.append(f)
    return {"deleted": deleted, "message": "🧹 Diretório limpo!"}
