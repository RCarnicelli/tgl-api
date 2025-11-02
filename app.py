from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, PlainTextResponse

app = FastAPI(title="TGL API", description="API para diagramas de guitarra (escalas e acordes)")

# Afinação padrão (6 cordas EADGBE)
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

# Fórmulas de acordes em intervalos (semitons)
CHORD_FORMULAS = {
    "": [0, 4, 7],           # major
    "m": [0, 3, 7],          # minor
    "7": [0, 4, 7, 10],      # dominant 7th
    "maj7": [0, 4, 7, 11],   # major 7th
    "m7": [0, 3, 7, 10],     # minor 7th
    "dim": [0, 3, 6],        # diminished
    "aug": [0, 4, 8],        # augmented
    "m7b5": [0, 3, 6, 10],   # half diminished
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
    return scale


def generate_ascii_fretboard(root: str, scale: str) -> str:
    """Gera diagrama ASCII simples do braço (0–12)."""
    scale_notes = build_scale(root, scale)
    ascii_lines = []
    for string_note in TUNING:
        line = []
        base_idx = NOTES.index(string_note)
        for fret in range(13):
            note = NOTES[(base_idx + fret) % 12]
            line.append("●" if note in scale_notes else "—")
        ascii_lines.append(" ".join(line))
    ascii_repr = "\n".join(ascii_lines)
    return f"Escala {root} {scale}\n" + ascii_repr


def generate_svg(notes_to_show: list, label: str) -> str:
    """Gera SVG genérico (usado para escalas e acordes)."""
    width, height = 700, 200
    fret_width = width / 13
    string_height = height / 6
    circles = []
    for s, string_note in enumerate(TUNING):
        base_idx = NOTES.index(string_note)
        y = s * string_height + string_height / 2
        for fret in range(13):
            note = NOTES[(base_idx + fret) % 12]
            if note in notes_to_show:
                x = fret * fret_width + fret_width / 2
                circles.append(
                    f'<circle cx="{x}" cy="{y}" r="8" fill="orange" stroke="black" stroke-width="1"/>'
                )

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
      <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="2"/>
      <text x="10" y="20" font-size="16" font-family="Arial" fill="black">{label}</text>
      <!-- Cordas -->
      {''.join([f'<line x1="0" y1="{i*string_height + string_height/2}" x2="{width}" y2="{i*string_height + string_height/2}" stroke="gray" stroke-width="1"/>' for i in range(6)])}
      <!-- Trastes -->
      {''.join([f'<line x1="{i*fret_width}" y1="0" x2="{i*fret_width}" y2="{height}" stroke="lightgray" stroke-width="1"/>' for i in range(13)])}
      <!-- Notas -->
      {''.join(circles)}
    </svg>
    """
    return svg.strip()


def build_chord(root: str, chord_type: str) -> list:
    """Monta as notas de um acorde a partir do tipo."""
    if root not in NOTES:
        raise ValueError(f"Nota inválida: {root}")
    if chord_type not in CHORD_FORMULAS:
        raise ValueError(f"Acorde inválido: {chord_type}")

    root_idx = NOTES.index(root)
    intervals = CHORD_FORMULAS[chord_type]
    chord_notes = [NOTES[(root_idx + i) % 12] for i in intervals]
    return chord_notes


@app.get("/ascii", response_class=PlainTextResponse)
def ascii_scale(root: str = Query("C"), scale: str = Query("major")):
    """Retorna escala em ASCII."""
    return generate_ascii_fretboard(root, scale)


@app.get("/svg", response_class=HTMLResponse)
def svg_scale(root: str = Query("C"), scale: str = Query("major")):
    """Retorna escala em SVG."""
    notes = build_scale(root, scale)
    return generate_svg(notes, f"Escala {root} {scale}")


@app.get("/chord", response_class=HTMLResponse)
def chord_svg(root: str = Query("C"), type: str = Query("")):
    """Retorna o diagrama SVG de um acorde."""
    notes = build_chord(root, type)
    return generate_svg(notes, f"Acorde {root}{type}")
