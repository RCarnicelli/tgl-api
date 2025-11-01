from typing import List, Tuple, Dict, Optional, Set

NOTES_SHARP = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]
ENH_EQ = {"Db":"C#", "Eb":"D#", "Gb":"F#", "Ab":"G#", "Bb":"A#"}
TUNING = ["E","B","G","D","A","E"]  # 1..6 (top→bottom)
OPEN_IDX = [NOTES_SHARP.index(n) for n in TUNING]

MODES = {
    "ionian":     [0,2,4,5,7,9,11],
    "dorian":     [0,2,3,5,7,9,10],
    "phrygian":   [0,1,3,5,7,8,10],
    "lydian":     [0,2,4,6,7,9,11],
    "mixolydian": [0,2,4,5,7,9,10],
    "aeolian":    [0,2,3,5,7,8,10],
    "locrian":    [0,1,3,5,6,8,10],
    "harm_minor": [0,2,3,5,7,8,11],
    "mel_minor":  [0,2,3,5,7,9,11],
}

QUALITY_INTERVALS = {
    "maj": [0,4,7],
    "min": [0,3,7],
    "dim": [0,3,6],
    "aug": [0,4,8],
}

DEFAULT_SCALE_FOR_QUALITY = {
    "maj": "ionian",
    "min": "aeolian",
    "dim": "locrian",
    "aug": "ionian",
}

def norm_note(n: str) -> str:
    return ENH_EQ.get(n, n).upper()

def note_to_idx(n: str) -> int:
    return NOTES_SHARP.index(norm_note(n))

def idx_to_note(i: int) -> str:
    return NOTES_SHARP[(i % 12 + 12) % 12]

def add_int(idx: int, semitones: int) -> int:
    return (idx + semitones) % 12

def string_note_at_fret(string_num: int, fret: int) -> str:
    base = OPEN_IDX[string_num-1]
    return idx_to_note(base + fret)

def triad_pitches(root: str, quality: str, inversion: int=0) -> List[int]:
    root_idx = note_to_idx(root)
    ints = QUALITY_INTERVALS[quality]
    pcs = [(root_idx + x) % 12 for x in ints]
    for _ in range(inversion % 3):
        pcs = pcs[1:] + pcs[:1]
    return pcs

def assign_to_strings(pcs: List[int], strings: Tuple[int,int,int], order_top_to_bottom=True):
    s_sorted = tuple(sorted(strings))
    seq = pcs[:] if order_top_to_bottom else list(reversed(pcs))
    return list(zip(s_sorted, seq))  # list of (string, pc)

def apply_spread(mapping, spread: Optional[str]):
    if not spread: return mapping
    V = list(mapping)  # [(s,pc), (s,pc), (s,pc)] top→bottom
    if spread.lower() == "drop2": return [V[0], V[2], V[1]]
    if spread.lower() == "drop3": return [V[2], V[0], V[1]]
    return mapping

def choose_frets_for_mapping(mapping, start_fret: int) -> Dict[int,int]:
    result = {}
    lo, hi = start_fret, start_fret + 6
    for s, pc in mapping:
        found = None
        for t in range(lo, hi+1):
            n = string_note_at_fret(s, t)
            if note_to_idx(n) == pc:
                found = t; break
        if found is None:
            raise ValueError(f"Sem posição para corda {s} na janela {lo}-{hi}.")
        result[s] = found
    return result

def scale_set(root: str, mode: Optional[str]) -> Set[str]:
    if mode is None:
        mode = "ionian"
    r_idx = note_to_idx(root)
    return { idx_to_note(r_idx + d) for d in MODES[mode] }

def generate_triad_voicing(root: str, quality: str, strings: Tuple[int,int,int], inversion: int, spread: Optional[str], start_fret: int) -> Dict[int,int]:
    pcs = triad_pitches(root, quality, inversion)
    mapping = assign_to_strings(pcs, strings, True)
    mapping = apply_spread(mapping, spread)
    frets = choose_frets_for_mapping(mapping, start_fret)
    voicing = { s: None for s in range(1,7) }
    voicing.update(frets)
    return voicing

# ---------- ASCII (3-col grid) ----------
def render_ascii_grid(voicing, start_fret, chord_root, quality, scale_mode, highlight_scale=True, show_all_scale=False):
    lo = start_fret
    scale = scale_set(chord_root, scale_mode or DEFAULT_SCALE_FOR_QUALITY[quality])
    lines = []
    for s in range(1,7):
        parts = []
        absf = voicing.get(s, None)
        for col in range(0,7):
            fret = lo + col
            note = string_note_at_fret(s, fret)
            if absf == "X" and col == 0:
                parts.append(" X ")
                continue
            if isinstance(absf, int) and absf == fret:
                parts.append(f" {note[:2]:<2}")
            else:
                if highlight_scale and (show_all_scale or isinstance(absf,int)) and note in scale:
                    parts.append(f" {note[:2].lower():<2}")
                else:
                    parts.append(" . ")
        lines.append(f"{s}|" + "|".join(parts) + "|")
    ruler = "    " + "  ".join(str(i) for i in range(0,7))
    return "\n".join(lines+[ruler])

# ---------- SVG ----------
def render_svg_fretboard(voicing, start_fret, chord_root, quality, scale_mode, highlight_scale, show_all_scale, width=420, height=520):
    CELL_W, CELL_H = 45, 60
    PADDING_L, PADDING_T = 70, 60
    lo = start_fret
    triad_pcs = triad_pitches(chord_root, quality, 0)
    scale = scale_set(chord_root, scale_mode or DEFAULT_SCALE_FOR_QUALITY[quality])

    def colX(c): return PADDING_L + c*CELL_W
    def rowY(r): return PADDING_T + r*CELL_H

    # strings & frets
    strings_svg = "\n".join([f'<line class=\"string\" x1=\"{PADDING_L}\" y1=\"{rowY(r)}\" x2=\"{PADDING_L+CELL_W*7}\" y2=\"{rowY(r)}\" />' for r in range(6)])
    frets = []
    for c in range(0,7):
        if c == 0:
            frets.append(f'<line class=\"nut\" x1=\"{colX(c)}\" y1=\"{PADDING_T-6}\" x2=\"{colX(c)}\" y2=\"{PADDING_T+CELL_H*6+6}\" />')
        else:
            frets.append(f'<line class=\"fret\" x1=\"{colX(c)}\" y1=\"{PADDING_T-6}\" x2=\"{colX(c)}\" y2=\"{PADDING_T+CELL_H*6+6}\" />')
    frets_svg = "\n".join(frets)

    # labels & ruler
    labels = "\n".join([f'<text class=\"label\" x=\"{PADDING_L-12}\" y=\"{rowY(i)+4}\" text-anchor=\"end\">{i+1} ({TUNING[i]})</text>' for i in range(6)])
    ruler = "\n".join([f'<text class=\"ruler\" x=\"{colX(c)}\" y=\"{PADDING_T+CELL_H*6+30}\" text-anchor=\"middle\">{lo+c}</text>' for c in range(7)])

    # markers
    markers = []
    for s in range(1,7):
        absf = voicing.get(s, None)
        for col in range(0,7):
            fret = lo + col
            note = string_note_at_fret(s, fret)
            isPlaced = isinstance(absf, int) and absf == fret
            isScale = (note in scale)
            if isPlaced or (show_all_scale and highlight_scale and isScale):
                x = colX(col) + CELL_W/2; y = rowY(s-1); r = 14
                pc = triad_pcs
                isChordTone = (note_to_idx(note) in pc)
                fill = "#111" if isPlaced and isChordTone else ("#333" if isPlaced else "#2aa4f4")
                textFill = "#fff" if isPlaced else "#001f3f"
                stroke = "#222"
                markers.append(
                    f'<g transform=\"translate({x},{y})\"><circle r=\"{r}\" fill=\"{fill}\" stroke=\"{stroke}\" stroke-width=\"{2 if isPlaced else 1}\" />'
                    f'<text x=\"0\" y=\"4\" text-anchor=\"middle\" font-size=\"12\" fill=\"{textFill}\" style=\"font-weight:{700 if isPlaced else 600}\">{note}</text></g>'
                )
    markers_svg = "\n".join(markers)

    # sizes
    w = PADDING_L + CELL_W*7 + 40
    h = PADDING_T + CELL_H*6 + 80
    w = max(w, width); h = max(h, height)

    svg = f"""<svg width="{w}" height="{h}" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .nut{{stroke:#111;stroke-width:8}}
      .fret{{stroke:#666;stroke-width:2}}
      .string{{stroke:#333;stroke-width:2}}
      .label{{font:14px sans-serif;fill:#222}}
      .ruler{{font:12px monospace;fill:#444}}
    </style>
  </defs>
  <rect x="0" y="0" width="{w}" height="{h}" fill="#fff"/>
  {strings_svg}
  {frets_svg}
  {labels}
  {ruler}
  {markers_svg}
</svg>"""
    return svg
# --------- TÉTRADES ---------
TETRAD_INTERVALS = {
    "maj7": [0, 4, 7, 11],
    "min7": [0, 3, 7, 10],
    "7":    [0, 4, 7, 10],   # dominante
    "m7b5": [0, 3, 6, 10],   # meio-diminuto (ø)
    "dim7": [0, 3, 6, 9],    # diminuto
}

def tetrad_pitches(root: str, quality: str, inversion: int = 0):
    if quality not in TETRAD_INTERVALS:
        raise ValueError("quality deve ser: maj7|min7|7|m7b5|dim7")
    root_idx = note_to_idx(root)
    ints = TETRAD_INTERVALS[quality]
    pcs = [(root_idx + x) % 12 for x in ints]  # [1,3,5,7]
    for _ in range(inversion % 4):
        pcs = pcs[1:] + pcs[:1]
    return pcs  # 4 PCs

def assign_to_strings_k(pcs, strings, order_top_to_bottom=True):
    s_sorted = tuple(sorted(strings))
    seq = pcs[:] if order_top_to_bottom else list(reversed(pcs))
    if len(seq) != len(s_sorted):
        raise ValueError("número de cordas deve = número de vozes")
    return list(zip(s_sorted, seq))  # [(string, pc),...]

def apply_spread_k(mapping, spread: str | None):
    if not spread: return mapping
    V = list(mapping)  # top→bottom
    n = len(V)
    if n == 3:
        # já implementado em triads; mantém compatibilidade
        if spread.lower() == "drop2": return [V[0], V[2], V[1]]
        if spread.lower() == "drop3": return [V[2], V[0], V[1]]
    if n == 4:
        # convenção clássica (top→bottom = V1 alto ... V4 baixo)
        if spread.lower() == "drop2":
            # 2ª voz (de cima) cai para a base
            return [V[0], V[2], V[3], V[1]]
        if spread.lower() == "drop3":
            # 3ª voz (de cima) cai para a base
            return [V[0], V[1], V[3], V[2]]
    return mapping

def generate_tetrad_voicing(root: str, quality: str, strings: tuple[int,int,int,int],
                            inversion: int, spread: str | None, start_fret: int):
    pcs = tetrad_pitches(root, quality, inversion)
    mapping = assign_to_strings_k(pcs, strings, True)
    mapping = apply_spread_k(mapping, spread)
    frets = choose_frets_for_mapping(mapping, start_fret)
    voicing = { s: None for s in range(1,7) }
    voicing.update(frets)
    return voicing
