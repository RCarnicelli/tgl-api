from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import matplotlib.pyplot as plt
import io, base64

app = FastAPI(
    title="Guitar Diagram API (Render Safe)",
    description="Gera diagramas simples do braço da guitarra via Matplotlib",
    version="1.1.0"
)

# Afinação padrão
TUNING = ['E', 'A', 'D', 'G', 'B', 'E']

@app.get("/")
def root():
    return {"message": "🎸 API ativa! Use /diagram?note=A&fret=5"}

@app.get("/diagram")
def diagram(note: str = Query("C"), fret: int = Query(3)):
    """Desenha uma nota no braço da guitarra"""
    fig, ax = plt.subplots(figsize=(6, 2))

    # Desenha 6 cordas e 7 trastes
    for s in range(6):
        ax.plot([0, 6], [s, s], color='black', linewidth=0.8)
    for f in range(7):
        ax.plot([f, f], [0, 5], color='gray', linewidth=0.6)

    # Posição da nota
    ax.scatter(fret, 2, s=300, color='orange', zorder=3)
    ax.text(fret, 2.1, note, ha='center', va='bottom', fontsize=11, fontweight='bold')

    ax.set_xlim(-0.2, 6.2)
    ax.set_ylim(-0.5, 5.5)
    ax.set_yticks(range(6))
    ax.set_yticklabels(reversed(TUNING))
    ax.axis('off')

    # Converter para base64
    buf = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format="png", dpi=200)
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")

    return JSONResponse(content={
        "note": note,
        "fret": fret,
        "image_base64": img_b64
    })
