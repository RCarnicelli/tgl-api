from fastapi import FastAPI
from fretboardgtr.fretboard import Fretboard   # ✅ Import correto para 0.2.7

app = FastAPI()

@app.get("/test")
def test_fretboard():
    fb = Fretboard(tuning="EADGBE")
    diagram = fb.plot("C major scale", position=5)
    return {"status": "ok", "diagram": str(diagram)}

@app.get("/")
def root():
    return {"message": "TGL API rodando com sucesso 🚀"}
