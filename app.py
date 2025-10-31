from fastapi.security import HTTPBearer
from fastapi.openapi.utils import get_openapi

security = HTTPBearer()

from fastapi import FastAPI, HTTPException, Header, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Dict
import os

from tgl_core import (
    generate_triad_voicing,
    render_svg_fretboard,
    render_ascii_grid,
    MODES, QUALITY_INTERVALS
)

API_KEY = os.getenv("RENDER_API_KEY", "changeme")

app = FastAPI(title="TGL Render API", version="1.0.0")

# CORS – ajuste origins para seu domínio
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # troque para ['https://seu-dominio.com'] em produção
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TriadPayload(BaseModel):
    root: str = Field("C", description="Tônica: C, C#, D, ... (sustenidos preferidos)")
    quality: str = Field("maj", description="maj|min|dim|aug")
    strings: Tuple[int, int, int] = Field((1,2,3), description="Grupo de cordas (1=E aguda ... 6=E grave)")
    inversion: int = Field(0, ge=0, le=2, description="0=fundamental, 1=1ª, 2=2ª")
    spread: Optional[str] = Field(None, description="None|drop2|drop3")
    start_fret: int = Field(0, ge=0, le=18, description="Traste inicial da janela (0..18)")
    scale_mode: Optional[str] = Field(None, description=f"Modo escala origem. Opções: {', '.join(MODES.keys())}. None=default pela qualidade")
    highlight_scale: bool = True
    show_all_scale: bool = False
    output: str = Field("svg", description="svg|png|ascii")
    width: int = Field(420, description="Largura SVG/PNG em px")
    height: int = Field(520, description="Altura SVG/PNG em px")

def check_auth(auth: Optional[str]):
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(401, "Missing Authorization header")
    token = auth.split(" ",1)[1].strip()
    if token != API_KEY:
        raise HTTPException(403, "Invalid API key")

@app.post("/render/triad")
def render_triad(
    payload: TriadPayload,
    Authorization: Optional[str] = Header(None)
):
    check_auth(Authorization)

    # validações básicas
    if payload.quality not in QUALITY_INTERVALS:
        raise HTTPException(400, "quality deve ser: maj|min|dim|aug")
    if payload.scale_mode and payload.scale_mode not in MODES:
        raise HTTPException(400, f"scale_mode inválido. Use: {', '.join(MODES.keys())}")

    try:
        voicing = generate_triad_voicing(
            root=payload.root,
            quality=payload.quality,
            strings=payload.strings,
            inversion=payload.inversion,
            spread=payload.spread,
            start_fret=payload.start_fret
        )
    except ValueError as e:
        raise HTTPException(422, str(e))

    if payload.output == "ascii":
        ascii_text = render_ascii_grid(
            voicing=voicing,
            start_fret=payload.start_fret,
            chord_root=payload.root,
            quality=payload.quality,
            scale_mode=payload.scale_mode,
            highlight_scale=payload.highlight_scale,
            show_all_scale=payload.show_all_scale
        )
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
        width=payload.width, height=payload.height
    )

    if payload.output == "svg":
        return Response(content=svg, media_type="image/svg+xml")

    if payload.output == "png":
        try:
            import cairosvg
        except Exception:
            raise HTTPException(500, "PNG requer CairoSVG. Instale com: pip install cairosvg")
        png_bytes = cairosvg.svg2png(bytestring=svg.encode("utf-8"), output_width=payload.width, output_height=payload.height)
        return Response(content=png_bytes, media_type="image/png")

    raise HTTPException(400, "output inválido. Use: svg|png|ascii")
