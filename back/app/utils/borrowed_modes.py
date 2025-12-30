from typing import Dict, List, Optional, Set

from app.utils.common import is_chord_diatonic, parse_chord
from constants import MODE_SPECIFIC_NUMERALS, MODES_DATA, NOTES
from constants import NOTE_INDEX_MAP as NOTE_TO_INDEX

INTERVALS = {
    "": [0, 4, 7],
    "M": [0, 4, 7],
    "maj": [0, 4, 7],
    "m": [0, 3, 7],
    "min": [0, 3, 7],
    "-": [0, 3, 7],
    "dim": [0, 3, 6],
    "d": [0, 3, 6],
    "°": [0, 3, 6],
    "aug": [0, 4, 8],
    "+": [0, 4, 8],
    "5": [0, 7],
    "sus2": [0, 2, 7],
    "sus4": [0, 5, 7],
    "7sus2": [0, 2, 7, 10],
    "7sus4": [0, 5, 7, 10],
    "9sus4": [0, 5, 7, 10, 14],
    "13sus4": [0, 5, 7, 10, 14, 21],
    "add2": [0, 4, 7, 14],
    "add4": [0, 4, 7, 17],
    "add9": [0, 4, 7, 14],
    "add9(no5)": [0, 4, 14],
    "add11": [0, 4, 7, 17],
    "add11(no5)": [0, 4, 17],
    "m(add9)": [0, 3, 7, 14],
    "m(add9)(no5)": [0, 3, 14],
    "m(add11)(no5)": [0, 3, 17],
    "6": [0, 4, 7, 9],
    "6(no5)": [0, 4, 9],
    "m6": [0, 3, 7, 9],
    "m6(no5)": [0, 3, 9],
    "-6": [0, 3, 7, 9],
    "6/9": [0, 4, 7, 9, 14],
    "6/9(no5)": [0, 4, 9, 14],
    "m(6/9)": [0, 3, 7, 9, 14],
    "m(6/9)(no5)": [0, 3, 9, 14],
    "7": [0, 4, 7, 10],
    "7(no5)": [0, 4, 10],
    "maj7": [0, 4, 7, 11],
    "maj7(no5)": [0, 4, 11],
    "M7": [0, 4, 7, 11],
    "Δ": [0, 4, 7, 11],
    "m7": [0, 3, 7, 10],
    "m7(no5)": [0, 3, 10],
    "m7b9": [0, 3, 7, 10, 13],
    "m7b9(no5)": [0, 3, 10, 13],
    "min7": [0, 3, 7, 10],
    "-7": [0, 3, 7, 10],
    "dim7": [0, 3, 6, 9],
    "°7": [0, 3, 6, 9],
    "m7b5": [0, 3, 6, 10],
    "ø": [0, 3, 6, 10],
    "m(add9)b5": [0, 3, 6, 14],
    "m(maj7)": [0, 3, 7, 11],
    "m(maj7)(no5)": [0, 3, 11],
    "mM7": [0, 3, 7, 11],
    "maj7b5": [0, 4, 6, 11],
    "maj7#5": [0, 4, 8, 11],
    "maj7#11": [0, 4, 7, 11, 18],
    "7b5": [0, 4, 6, 10],
    "7#5": [0, 4, 8, 10],
    "7(maj7)": [0, 4, 7, 10, 11],
    "7(maj7)(no5)": [0, 4, 10, 11],
    "+7": [0, 4, 8, 10],
    "7b9": [0, 4, 7, 10, 13],
    "7b9(no5)": [0, 4, 10, 13],
    "7b13": [0, 4, 7, 10, 20],
    "7b13(no5)": [0, 4, 10, 20],
    "7#9": [0, 4, 7, 10, 15],
    "7#9(no5)": [0, 4, 10, 15],
    "7#11": [0, 4, 7, 10, 18],
    "7#11(no5)": [0, 4, 10, 18],
    "7alt": [0, 4, 10, 13, 18],
    "7b9b5": [0, 4, 6, 10, 13],
    "7b9#5": [0, 4, 8, 10, 13],
    "7#9b5": [0, 4, 6, 10, 15],
    "7#9#5": [0, 4, 8, 10, 15],
    "7b9#9": [0, 4, 7, 10, 13, 15],
    "7b9#11": [0, 4, 7, 10, 13, 18],
    "7#9#11": [0, 4, 7, 10, 15, 18],
    "7b9b13": [0, 4, 7, 10, 13, 20],
    "7#9b13": [0, 4, 7, 10, 15, 20],
    9: [0, 4, 7, 10, 14],
    "9(no5)": [0, 4, 10, 14],
    "maj9": [0, 4, 7, 11, 14],
    "maj9(no5)": [0, 4, 11, 14],
    "M9": [0, 4, 7, 11, 14],
    "m9": [0, 3, 7, 10, 14],
    "m9(no5)": [0, 3, 10, 14],
    "-9": [0, 3, 7, 10, 14],
    "11": [0, 4, 7, 10, 14, 17],
    "11(no5)": [0, 4, 10, 14, 17],
    "11(no3)": [0, 7, 10, 14, 17],
    "m11": [0, 3, 7, 10, 14, 17],
    "m11(no5)": [0, 3, 10, 14, 17],
    "-11": [0, 3, 7, 10, 14, 17],
    "maj11": [0, 4, 7, 11, 14, 17],
    "maj11(no5)": [0, 4, 11, 14, 17],
    "maj11(no5,no9)": [0, 4, 5, 11],
    "13": [0, 4, 7, 10, 14, 21],
    "13(no5)": [0, 4, 10, 14, 21],
    "13#11": [0, 4, 7, 10, 14, 18, 21],
    "m13": [0, 3, 7, 10, 14, 21],
    "m13(no5)": [0, 3, 10, 14, 21],
    "-13": [0, 3, 7, 10, 14, 21],
    "maj13": [0, 4, 7, 11, 14, 21],
    "maj13(no5)": [0, 4, 11, 14, 21],
    "quartal": [0, 5, 10],
    "split3": [0, 3, 4, 7],
    "mu": [0, 4, 14],
}

# --- Fonctions utilitaires ---


def get_notes_from_chord(chord_name: str) -> Optional[Set[str]]:
    """
    Parse un nom d'accord en trouvant la meilleure correspondance de qualité.
    Cette version est plus robuste et gère une grande variété de qualités.
    """
    # 1. Extraire la fondamentale (gère les "b" et "#")
    root_name = chord_name[0]
    if len(chord_name) > 1 and chord_name[1] in ["#", "b"]:
        root_name = chord_name[:2]

    if root_name not in NOTE_TO_INDEX:
        return None  # Fondamentale non valide

    # 2. Extraire la qualité (tout ce qui n'est pas la fondamentale)
    quality_str = chord_name[len(root_name) :]

    # 3. Trouver la meilleure correspondance pour la qualité dans le dictionnaire INTERVALS
    # On trie les clés par longueur décroissante pour trouver la correspondance la plus spécifique
    # (ex: "maj7" sera trouvé avant "maj" ou "7")
    best_match_quality = ""
    for quality in sorted(INTERVALS.keys(), key=lambda k: len(str(k)), reverse=True):
        if quality_str == quality:
            best_match_quality = str(quality)
            break

    if best_match_quality == "" and quality_str != "":
        # Si aucune correspondance exacte n'est trouvée pour une qualité non vide
        return None

    # 4. Construire le set de notes
    root_index = NOTE_TO_INDEX[root_name]
    final_intervals = INTERVALS[best_match_quality]

    # On utilise un set de notes normalisées (sans octave)
    chord_notes = {NOTES[(root_index + i) % 12] for i in final_intervals}

    return chord_notes


def build_scale(tonic: str, mode_name: str) -> Optional[List[str]]:
    """Construit une gamme à partir d'une tonique et du nom d'un mode."""
    # Accept case-insensitive mode names
    found_mode_key = next((k for k in MODES_DATA if k.lower() == mode_name.lower()), None)
    if not found_mode_key:
        return None
    mode_intervals = MODES_DATA[found_mode_key][0]
    tonic_index = NOTE_TO_INDEX[tonic]
    return [NOTES[(tonic_index + i) % 12] for i in mode_intervals]


def get_diatonic_chord_notes(scale: List[str], degree: int, num_notes: int = 4) -> Set[str]:
    """Construit un accord diatonique (en empilant des tierces) à partir d'une gamme."""
    chord_notes = set()
    scale_len = len(scale)
    for i in range(num_notes):
        note_index = (degree + (i * 2)) % scale_len
        chord_notes.add(scale[note_index])
    return chord_notes


# --- Fonctions d'analyse principales (légèrement adaptées) ---


def check_parallel_modes(chord_notes: Set[str], tonic: str) -> Optional[Dict]:
    """
    Vérifie si l'accord provient d'un mode parallèle COMMUN et musicalement pertinent.
    """
    priority_modes = ["Aeolian", "Ionian", "Dorian", "Mixolydian", "Lydian", "Phrygian"]

    for mode_name in priority_modes:
        numerals_for_this_mode = MODE_SPECIFIC_NUMERALS.get(mode_name, [])
        if not numerals_for_this_mode:
            continue

        parallel_scale = build_scale(tonic, mode_name)
        if not parallel_scale:
            continue

        for i in range(len(parallel_scale)):
            for num_notes in [3, 4]:
                diatonic_chord_notes = get_diatonic_chord_notes(parallel_scale, i, num_notes)
                if chord_notes == diatonic_chord_notes:
                    return {
                        "origin": f"Emprunt au mode parallèle : {tonic} {mode_name}",
                        "function": f"Accord diatonique en {tonic} {mode_name}",
                    }

    return None


def check_secondary_functions(
    chord_name: str, chord_notes: Set[str], tonic: str, original_mode: str = "ionian"
) -> Optional[Dict]:
    """
    Vérifie si l'accord a une fonction de dominante secondaire (V7/x),
    en gérant les variations comme les accords sus4, 9, etc.
    """
    original_scale = build_scale(tonic, original_mode)
    if not original_scale:
        return None

    parsed_data = parse_chord(chord_name)
    if not parsed_data:
        return None
    actual_root_index, _, _ = parsed_data

    for i in range(1, 7):  # Itère sur les cibles possibles (ii, iii, IV, V, vi, vii)
        target_chord_root = original_scale[i]

        secondary_dominant_root_index = (NOTE_TO_INDEX[target_chord_root] + 7) % 12

        if actual_root_index == secondary_dominant_root_index:
            expected_7th_index = (secondary_dominant_root_index + 10) % 12
            expected_7th_note = NOTES[expected_7th_index]

            expected_3rd_index = (secondary_dominant_root_index + 4) % 12
            expected_3rd_note = NOTES[expected_3rd_index]

            # Accept either a true major 3rd OR a suspended 4th (sus4) in place of the 3rd
            sus4_note = NOTES[(secondary_dominant_root_index + 5) % 12]
            if expected_7th_note in chord_notes and (
                expected_3rd_note in chord_notes or sus4_note in chord_notes
            ):
                # Use a case-insensitive lookup for the roman numeral list
                found_mode_key = next(
                    (k for k in MODE_SPECIFIC_NUMERALS if k.lower() == original_mode.lower()), None
                )
                if found_mode_key:
                    target_degree = MODE_SPECIFIC_NUMERALS[found_mode_key][i]
                else:
                    target_degree = MODE_SPECIFIC_NUMERALS.get(original_mode, [])[i]

                # Degree field uses an uppercase Roman for readability (tests expect this),
                # while the function description keeps the original casing.
                return {
                    "origin": f"Tonalité de {target_chord_root}",
                    "degree": f"V/{target_degree.upper()}",
                    "function": f"Dominante Secondaire de {target_degree}",
                }
    return None


def check_tritone_substitution(
    chord_name: str, chord_notes: Set[str], tonic: str, original_mode: str = "ionian"
) -> Optional[Dict]:
    """
    Vérifie si l'accord a une fonction de substitution tritonique (subV7/x).
    """
    original_scale = build_scale(tonic, original_mode)
    if not original_scale:
        return None

    parsed_data = parse_chord(chord_name)
    if not parsed_data:
        return None
    actual_root_index, _, _ = parsed_data

    # Vérifie si l'accord a la qualité de dominante (tierce majeure + septième mineure)
    # C'est une condition nécessaire pour une substitution tritonique
    expected_3rd_index = (actual_root_index + 4) % 12
    expected_7th_index = (actual_root_index + 10) % 12
    expected_3rd_note = NOTES[expected_3rd_index]
    expected_7th_note = NOTES[expected_7th_index]

    if not (expected_3rd_note in chord_notes and expected_7th_note in chord_notes):
        # Si ce n'est pas un accord de 7e de dominante, ce n'est pas un subV7
        return None

    # Itère sur TOUTES les cibles possibles (I, ii, iii, IV, V, vi, vii)
    for i in range(7):
        target_chord_root = original_scale[i]

        # 1. Trouver la dominante NORMALE de la cible
        standard_dominant_root_index = (NOTE_TO_INDEX[target_chord_root] + 7) % 12

        # 2. Trouver la fondamentale de la substitution tritonique (un triton plus loin)
        tritone_sub_root_index = (standard_dominant_root_index + 6) % 12

        # 3. Vérifier si notre accord a cette fondamentale
        if actual_root_index == tritone_sub_root_index:
            target_degree = MODE_SPECIFIC_NUMERALS.get(original_mode, [])[i]
            return {
                "origin": f"Substitution tritonique de {target_chord_root}",
                "degree": f"subV7/{target_degree}",
                "function": f"Substitution tritonique de {target_degree}",
            }

    return None


def get_borrowed_chords(quality_analysis: list) -> dict:
    """Analyse les accords empruntés avec la logique mise à jour."""
    borrowed_chords: Dict[str, List[str] | Dict] = {}

    for item in quality_analysis:
        if not item.get("is_diatonic"):
            chord_name = item.get("chord")
            context = item.get("segment_context", {})
            tonic = context.get("tonic")
            # mode from context is currently unused for this detection

            if not chord_name or not tonic:
                continue

            chord_notes = get_notes_from_chord(chord_name)
            if not chord_notes:
                borrowed_chords[chord_name] = {
                    "error": f"Qualité de l'accord '{chord_name}' non reconnue."
                }
                continue

            # Collect all modes for which this chord is diatonic in the given tonic
            found_modes: List[str] = []
            for mode_name in MODES_DATA.keys():
                try:
                    if is_chord_diatonic(chord_name, tonic, mode_name):
                        found_modes.append(mode_name)
                except Exception:
                    # Ignore modes that error during checking
                    continue

            if found_modes:
                borrowed_chords[chord_name] = found_modes
            else:
                borrowed_chords[chord_name] = {
                    "function": "Accord non-diatonique (origine inconnue)"
                }

    return borrowed_chords
