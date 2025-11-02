from fastapi import FastAPI, Response
from fretboardgtr.fretboard import Fretboard
import io
import matplotlib.pyplot as plt

app = FastAPI(title="🎸 TGL API - Fretboard Generator")

@app.get("/")
def home():
    return {
        "message": "🎸 TGL API rodando com sucesso!",
        "rotas": {
            "/plot/{modulo}": "Gera a imagem da escala/acorde/modo especificado. Ex: /plot/C major scale",
            "/plot/{modulo}?posicao=5": "Escolhe a posição no braço (1–12).",
        },
    }

@app.get("/test")
def test_fretboard():
    fb = Fretboard(tuning="EADGBE")
    diagram = fb.plot("C major scale", position=5)
    return {"status": "ok", "diagram": str(diagram)}

@app.get("/plot/{modulo}")
def plot_fretboard(modulo: str, posicao: int = 5):
    """
    Exemplo de uso:
      /plot/C major scale
      /plot/A minor pentatonic?posicao=8
      /plot/G7?posicao=3
    """
    fb = Fretboard(tuning="EADGBE")

    try:
        fig = fb.plot(modulo, position=posicao)
    except Exception as e:
        return {"erro": f"Não foi possível gerar o diagrama para '{modulo}': {e}"}

    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)

    return Response(content=buf.read(), media_type="image/png")
