from fastapi import FastAPI
from fretboardgtr import Fretboard   # ✅ Import correto para a versão 0.2.7

app = FastAPI()

# 🚀 Endpoint de teste simples pra verificar se o Fretboard está funcionando
@app.get("/test")
def test_fretboard():
    fb = Fretboard(tuning="EADGBE")
    diagram = fb.plot("C major scale", position=5)
    return {"status": "ok", "diagram": str(diagram)}

# 👇 Aqui você pode manter ou adicionar suas rotas originais do projeto
# Exemplo:
# @app.get("/")
# def root():
#     return {"message": "TGL API funcionando!"}
