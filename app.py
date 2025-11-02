from fastapi import FastAPI
from fretboardgtr import Fretboard

app = FastAPI()


@app.get("/")
def root():
    return {"message": "API da guitarra está rodando 🎸"}


@app.get("/test")
def test_fretboard():
    fb = Fretboard(tuning="EADGBE")
    diagram = fb.plot("C major scale", position=5)
    return {
        "status": "ok",
        "scale": "C major",
        "position": 5,
        "diagram": str(diagram)
    }
