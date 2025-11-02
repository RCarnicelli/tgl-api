from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from fretboardgtr import Fretboard
import matplotlib.pyplot as plt
import io
import base64

app = FastAPI(
    title="Guitar Diagram API",
    description="API para gerar diagramas de guitarra com escalas e acordes.",
    version="1.0.0"
)

# ---------- Função auxiliar ----------
def generate_diagram(img_func):
    """Gera o gráfico, converte pra base64 e retorna"""
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", bbox_inches="tight", dpi=200)
    plt.close()
    buf.seek(0)
    encoded = base64.b64encode(buf.read()).decode("utf-8")
    return encoded


# ---------- Rota principal: Escalas ----------
@app.get("/fretboard/scale")
def get_scale(
    tonic: str = Query("C", description="Nota tônica (ex: C, D#, F, G...)"),
    mode: str = Query("major", description="Modo ou tipo de escala (major, minor, dorian, mixolydian etc.)"),
    start_fret: int = Query(0, description="Traste inicial (0-12)")
):
    try:
        fb = Fretboard(tuning="EADGBE", start_fret=start_fret)
        fb.scale(f"{tonic} {mode}")
        fb.show()
        img = generate_diagram(fb.show)
        return JSONResponse(content={"scale": f"{tonic} {mode}", "start_fret": start_fret, "image_base64": img})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ---------- Rota para acordes ----------
@app.get("/fretboard/chord")
def get_chord(
    chord: str = Query("Cmaj7", description="Nome do acorde (ex: Cmaj7, Gm7, D9...)"),
    position: int = Query(0, description="Traste inicial (0-12)")
):
    try:
        fb = Fretboard(tuning="EADGBE", start_fret=position)
        fb.chord(chord)
        fb.show()
        img = generate_diagram(fb.show)
        return JSONResponse(content={"chord": chord, "position": position, "image_base64": img})
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ---------- Home ----------
@app.get("/")
def root():
    return {"message": "🎸 Guitar Diagram API ativa! Use /fretboard/scale ou /fretboard/chord."}
