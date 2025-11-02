from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
import math

app = FastAPI(title="TGL API", description="API para diagramas de guitarra (ASCII e SVG)")

# Afinação padrão (6 cordas EADGBE)
TUNING = ['E', 'A', 'D', 'G', 'B', 'E']
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

SCALE_INTERVALS = {
    "major": [2, 2, 1, 2, 2, 2, 1],
    "minor": [2, 1, 2, 2, 1, 2, 2],
    "dorian": [2, 1, 2, 2, 2, 1, 2],
    "mixolydian": [2, 2, 1, 2, 2, 1, 2],
    "lydian": [2, 2, 2, 1, 2, 2, 1],
    "phrygian": [1, 2, 2, 2, 1, 2, 2],
    "locrian": [1, 2, 2, 1, 2, 2, 2]
}


def build_scale(root_note: str, scale_type: str) -> list:
    """Retorna uma lista de notas da escala."""
    if root_note not in NOTES:
        raise ValueError(f"Nota inválida: {root_note}")
    if scale_type not in SCALE_INTERVALS:
        raise ValueError(f"Escala inválida: {scale_type}")

    root_idx = NOTES.index(root_note)
    intervals = SCALE_INTERVALS[scale_type]
    scale = [root_note]
    pos = root_idx
    for step in intervals:
        pos = (pos + step) % 12
        scale.append(NOTES[pos])
    return sc
