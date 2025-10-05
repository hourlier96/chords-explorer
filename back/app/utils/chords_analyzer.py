from typing import Any, Dict, NotRequired, Optional, TypedDict

from app.utils.common import (
    format_numeral,
    get_note_from_index,
    is_chord_diatonic,
    parse_chord,
)
from constants import CHROMATIC_DEGREES_MAP, MODES_DATA

# Defines the parallel mode for borrowing chords
PARALLEL_MODES = {
    "Ionian": "Aeolian",
    "Dorian": "Phrygian",  # Exemple, à adapter si besoin
    "Phrygian": "Dorian",  # Exemple
    "Lydian": "Mixolydian",  # Exemple
    "Mixolydian": "Lydian",  # Exemple
    "Aeolian": "Ionian",
}


class QualityAnalysisItem(TypedDict):
    chord: str
    found_numeral: Optional[str]
    expected_numeral: Optional[str]
    found_quality: Optional[str]
    expected_quality: Optional[str]
    expected_chord_name: Optional[str]
    segment_context: NotRequired[Dict[str, Any]]
    is_diatonic: bool | None
    inversion: NotRequired[int]
    duration: NotRequired[int]


def analyze_chord_in_context(chord_name, tonic_index, mode_name) -> QualityAnalysisItem:
    """
    Analyse un accord dans un contexte tonal/modal, en gérant les accords
    diatoniques et les emprunts courants.
    """

    # --- Analyse principale ---
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return {
            "chord": chord_name,
            "found_numeral": None,
            "expected_numeral": None,
            "found_quality": None,
            "expected_quality": None,
            "expected_chord_name": None,
            "is_diatonic": None,
        }

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    base_numeral = CHROMATIC_DEGREES_MAP.get(interval)

    if not base_numeral:
        return {
            "chord": chord_name,
            "found_numeral": None,
            "expected_numeral": None,
            "found_quality": None,
            "expected_quality": None,
            "expected_chord_name": None,
            "is_diatonic": None,
        }

    found_numeral = format_numeral(base_numeral, found_quality)
    is_diatonic_flag = is_chord_diatonic(chord_name, get_note_from_index(tonic_index), mode_name)

    expected_quality = None
    expected_numeral = None
    expected_chord_name = None

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval in mode_intervals:
        # La fondamentale de l'accord est diatonique au mode
        degree_index = mode_intervals.index(interval)
        expected_quality = mode_qualities[degree_index]

        # On utilise le `base_numeral` déjà calculé pour formater le chiffrage attendu
        expected_numeral = format_numeral(base_numeral, expected_quality)

        # Gestion spécifique de la sensible en mode mineur (V7)
        if mode_name == "Aeolian" and base_numeral == "V" and found_quality in ["7", "M"]:
            expected_quality = "7" if found_quality == "7" else "M"
            expected_numeral = format_numeral(base_numeral, expected_quality)
    else:
        # La fondamentale est chromatique (emprunt)
        # La logique existante pour trouver des correspondances dans d'autres modes est correcte.
        for mode, data in MODES_DATA.items():
            if mode:
                p_intervals, p_qualities = data[0], data[1]
                if interval in p_intervals:
                    degree_index = p_intervals.index(interval)
                    expected_quality = p_qualities[degree_index]
                    expected_numeral = format_numeral(base_numeral, expected_quality)
                    break  # On a trouvé une correspondance

    # Calcul du nom de l'accord attendu
    if expected_quality is not None:
        expected_root_index = (tonic_index + interval) % 12
        expected_root_name = get_note_from_index(expected_root_index)

        if "b" in base_numeral and "#" in expected_root_name:
            flat_note_index = (expected_root_index + 1) % 12
            expected_root_name = get_note_from_index(flat_note_index) + "b"

        expected_chord_name = expected_root_name + expected_quality

    return {
        "chord": chord_name,
        "found_numeral": found_numeral,
        "expected_numeral": expected_numeral,
        "found_quality": found_quality,
        "expected_quality": expected_quality,
        "expected_chord_name": expected_chord_name,
        "is_diatonic": is_diatonic_flag,
    }
