# app.py — TGL Render API (FastAPI)
# ---------------------------------
# - /render/triad: gera SVG/PNG/ASCII de tríades (maj/min/dim/aug),
#   com inversões, drop2/drop3, grupo de cordas, start_fret e destaque de escala.
# - Swagger com botão 🔒 Authorize (HTTP Bearer).
# - CORS liberado (ajuste origins para produção).
# - PNG opcional via CairoSVG.

import os
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, Header, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Swagger security (para exibir o botão "Authorize")
from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

# Núcleo musical/visual
from tgl_core import (
    generate_triad_voicing,
    generate_tetrad_voicing,   # <--- novo
    render_svg_fretboard,
    render_ascii_grid,
    MODES,
    QUALITY_INTERVALS,
)

# -------- Config --------
API_KEY = os.getenv("RENDER_API_KEY", "changeme")

security = HTTPBearer()

app = FastAPI(
    title="TGL Render API",
    version="1.0.0",
    openapi_tags=[{"name": "default", "description": "Render triads and chords"}],
)

# CORS (ajuste para o domínio do seu app em produção)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # ex.: ["https://seu-dominio.com"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- OpenAPI com esquema de segurança (mostra 🔒 Authorize) --------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})
    openapi_schema["components"]["securitySchemes"]["HTTPBearer"] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
    }
    # segurança global: todas as rotas exigem Bearer
    openapi_schema["security"] = [{"HTTPBearer": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi


# -------- Models --------
class TriadPayload(BaseModel):
    root: str = Field("C", description="Tônica: C, C#, D, ... (sustenidos preferidos)")
    quality: str = Field("maj", description="maj|min|dim|aug")
    strings: Tuple[int, int, int] = Field(
        (1, 2, 3),
        description="Grupo de cordas (1=E aguda ... 6=E grave) na ordem topo→base",
    )
    inversion: int = Field(0, ge=0, le=2, description="0=fundamental, 1=1ª, 2=2ª")
    spread: Optional[str] = Field(None, description="None|drop2|drop3")
    start_fret: int = Field(0, ge=0, le=18, description="Traste inicial da janela (0..18)")
    scale_mode: Optional[str] = Field(
        None,
        description=f"Modo da escala origem (None usa padrão pela qualidade). Opções: {', '.join(MODES.keys())}",
    )
    highlight_scale: bool = True
    show_all_scale: bool = False
    output: str = Field("svg", description="svg|png|ascii")
    width: int = Field(420, description="Largura SVG/PNG em px")
    height: int = Field(520, description="Altura SVG/PNG em px")


# -------- Auth helper --------
def check_auth(auth: Optional[str]):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing Authorization header")
    token = auth.split(" ", 1)[1].strip()
    if token != API_KEY:
        raise HTTPException(403, "Invalid API key")


# -------- Routes --------

@app.get("/health/auth", tags=["default"])
def health_auth():
    key = API_KEY or ""
    masked = (key[:1] + "*"*(len(key)-2) + key[-1:]) if key else ""
    return {"ok": True, "env_var_present": bool(key), "key_length": len(key), "preview": masked}
    
@app.post("/render/triad", tags=["default"])
def render_triad(payload: TriadPayload, Authorization: Optional[str] = Header(None)):
    # auth
    check_auth(Authorization)

    # validações simples
    if payload.quality not in QUALITY_INTERVALS:
        raise HTTPException(400, "quality deve ser: maj|min|dim|aug")
    if payload.scale_mode and payload.scale_mode not in MODES:
        raise HTTPException(400, f"scale_mode inválido. Use: {', '.join(MODES.keys())}")

    # gerar voicing
    try:
        voicing = generate_triad_voicing(
            root=payload.root,
            quality=payload.quality,
            strings=payload.strings,
            inversion=payload.inversion,
            spread=payload.spread,
            start_fret=payload.start_fret,
        )
    except ValueError as e:
        raise HTTPException(422, str(e))

    # ASCII
    if payload.output == "ascii":
        ascii_text = render_ascii_grid(
            voicing=voicing,
            start_fret=payload.start_fret,
            chord_root=payload.root,
            quality=payload.quality,
            scale_mode=payload.scale_mode,
            highlight_scale=payload.highlight_scale,
            show_all_scale=payload.show_all_scale,
        )
        # retorna JSON para facilitar consumo em apps
        return {"ok": True, "content_type": "text/plain", "ascii": ascii_text}

    # SVG
    svg = render_svg_fretboard(
        voicing=voicing,
        start_fret=payload.start_fret,
        chord_root=payload.root,
        quality=payload.quality,
        scale_mode=payload.scale_mode,
        highlight_scale=payload.highlight_scale,
        show_all_scale=payload.show_all_scale,
        width=payload.width,
        height=payload.height,
    )

    if payload.output == "svg":
        return Response(content=svg, media_type="image/svg+xml")

    if payload.output == "png":
        try:
            import cairosvg  # opcional
        except Exception:
            raise HTTPException(500, "PNG requer CairoSVG. Instale com: pip install cairosvg")
        png_bytes = cairosvg.svg2png(
            bytestring=svg.encode("utf-8"),
            output_width=payload.width,
            output_height=payload.height,
        )
        return Response(content=png_bytes, media_type="image/png")

    raise HTTPException(400, "output inválido. Use: svg|png|ascii")


# Execução local (opcional)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)
