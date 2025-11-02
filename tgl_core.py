import math

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


def generate_scale_svg(root: str, scale: str) -> str:
    """Gera um SVG simples mostrando notas da escala."""
    scale_notes = build_scale(root, scale)
    width, height = 700, 200
    fret_width = width / 13
    string_height = height / 6
    circles = []
    for s, string_note in enumerate(TUNING):
        base_idx = NOTES.index(string_note)
        y = s * string_height + string_height / 2
        for fret in range(13):
            note = NOTES[(base_idx + fret) % 12]
            if note in scale_notes:
                x = fret * fret_width + fret_width / 2
                circles.append(
                    f'<circle cx="{x}" cy="{y}" r="8" fill="orange" stroke="black" stroke-width="1"/>'
                )

    svg = f"""
    <svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">
      <rect width="100%" height="100%" fill="white" stroke="black" stroke-width="2"/>
      <!-- Cordas -->
      {''.join([f'<line x1="0" y1="{i*string_height + string_height/2}" x2="{width}" y2="{i*string_height + string_height/2}" stroke="gray" stroke-width="1"/>' for i in range(6)])}
      <!-- Trastes -->
      {''.join([f'<line x1="{i*fret_width}" y1="0" x2="{i*fret_width}" y2="{height}" stroke="lightgray" stroke-width="1"/>' for i in range(13)])}
      <!-- Notas -->
      {''.join(circles)}
    </svg>
    """
    return svg.strip()
