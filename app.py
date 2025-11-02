from fastapi import FastAPI, Response
from fretboardgtr.fretboard import Fretboard
import io
import matplotlib.pyplot as plt

app = FastAPI(title="🎸 TGL API - Fretboard v0.2.4")

@app.get("/")
def root():
    return {
        "message": "🎸 TGL API rodando com fretboardgtr 0.2.4!",
        "rotas": {
            "/plot/C_major_scale": "Exemplo: gera escala maior de C",
            "/plot/A_minor_pentatonic": "Exemplo: escala pentatônica de A",
            "/plot/E7": "Exemplo: acorde E7"
        }
    }

@app.get("/plot/{modulo}")
def plot_modulo(modulo: str):
    fb = Fretboard(tuning="EADGBE")

    try:
        fig = fb.plot(modulo.replace("_", " "))
    except Exception as e:
        return {"erro": str(e)}

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return Response(content=buf.read(), media_type="image/png")
