from fastapi import FastAPI
from fretboardgtr.fretboard import Guitar   # ✅ Import correto p/ versão 0.2.7

app = FastAPI()

# 🚀 Teste simples — confirma se o pacote está funcionando
@app.get("/test")
def test_fretboard():
    gtr = Guitar(tuning="EADGBE")
    diagram = gtr.plot("C major scale", position=5)
    return {"status": "ok", "diagram": str(diagram)}

# 👇 Mantém uma rota base pra garantir que o app está vivo
@app.get("/")
def root():
    return {"message": "TGL API rodando com sucesso 🚀"}
