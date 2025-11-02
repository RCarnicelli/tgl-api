from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import matplotlib.pyplot as plt
import io
import base64

# Cria o app principal
app = FastAPI(
    title="Guitar Diagram API",
    description="API simples para gerar diagramas do braço da guitarra via Matplotlib",
    version="1.0.0"
)

# Afinação padrão da guitarra (de baixo para cima)
TUNING = ['E', 'A', 'D', 'G', 'B', 'E']


@app.get("/")
def home():
    """
    Endpoint raiz para verificar se a API está no ar.
    """
    return {"message": "🎸 Guitar Diagram API ativa! Use /diagram?note=C&fret=3"}


@app.get("/diagram")
def diagram(
    note: str = Query("C", description="Nota que será destacada"),
    fret: int = Query(3, description="Traste onde a nota será exibida (0–12)")
):
    """
    Gera um diagrama simples do braço da guitarra,
    destacando uma nota específica em uma posição.
    """

    # Cria figura e eixos
    fig, ax = plt.subplots(figsize=(6, 2))

    # Desenha cordas (linhas horizontais)
    for s in range(6):
        ax.plot([0, 6], [s, s], color='black', linewidth=0.8)

    # Desenha trastes (linhas verticais)
    for f in range(7):
        ax.plot([f, f], [0, 5], color='gray', linewidth=0.6)

    # Adiciona marcador da nota
    ax.scatter(fret, 2, s=300, color='orange', zorder=3)
    ax.text(fret, 2.1, note, ha='center', va='bottom', fontsize=11, fontweight='bold')

    # Ajustes visuais
    ax.set_xlim(-0.2, 6.2)
    ax.set_ylim(-0.5, 5.5)
    ax.set_yticks(range(6))
    ax.set_yticklabels(reversed(TUNING))
    ax.axis('off')

    # Converter para imagem base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=200)
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")

    # Retornar JSON com a imagem
    return JSONResponse(content={
        "note": note,
        "fret": fret,
        "image_base64": img_b64
    })
