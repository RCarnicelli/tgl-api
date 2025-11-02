from fastapi import FastAPI
from fretboardgtr.fretboard import Guitar as Fretboard

app = FastAPI()

@app.get("/test")
def test_fretboard():
    fb = Fretboard(tuning="EADGBE")
    diagram = fb.plot("C major scale", position=5)
    return {"status": "ok", "diagram": str(diagram)}
