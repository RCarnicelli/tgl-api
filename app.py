from fastapi import FastAPI
from fretboardgtr.fretboard import FretBoard
from fretboardgtr.notes_creators import ScaleFromName

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API da guitarra está rodando 🎸"}


@app.get("/test")
def test_fretboard():
    # Cria o braço da guitarra padrão
    fb = FretBoard()

    # Cria escala de Dó maior (C Ionian)
    scale = ScaleFromName(root="C", mode="Ionian").build()

    # Adiciona as notas da escala ao braço
    fb.add_notes(scale=scale)

    # Exporta o diagrama para string (SVG)
    diagram_svg = fb.export("fretboard.svg", format="svg")

    return {
        "status": "ok",
        "scale": "C major (Ionian)",
        "diagram": str(diagram_svg)
    }
