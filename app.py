from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from fretboardgtr import Fretboard
import io, base64
import matplotlib.pyplot as plt

app = FastAPI(
    title="ADV Guitar Lab",
    description="API para geração de diagramas de acordes e escalas de guitarra."
)

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <h2>🎸 ADV Guitar Lab API</h2>
    <p>Use os endpoints:</p>
    <ul>
      <li><a href='/scale?root=C&mode=major'>/scale?root=C&mode=major</a></li>
      <li><a href='/chord?name=Cmaj7'>/chord?name=Cmaj7</a></li>
    </ul>
    """

@app.get("/scale", response_class=HTMLResponse)
def scale_diagram(root: str = Query("C"), mode: str = Query("major")):
    fb = Fretboard(scale=f"{root} {mode}")
    buf = io.BytesIO()
    fb.plot(show=False)
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"<h3>Escala {root} {mode}</h3><img src='data:image/png;base64,{img_b64}'/>"

@app.get("/chord", response_class=HTMLResponse)
def chord_diagram(name: str = Query("Cmaj7")):
    fb = Fretboard(chord=name)
    buf = io.BytesIO()
    fb.plot(show=False)
    plt.savefig(buf, format="png", bbox_inches="tight")
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode("utf-8")
    return f"<h3>Acorde {name}</h3><img src='data:image/png;base64,{img_b64}'/>"
