from typing import List

from app.utils.chords_analyzer import QualityAnalysisItem
from app.utils.common import (
    get_chord_notes,
    get_scale_notes,
)
from constants import (
    CORE_QUALITIES,
    MODES_DATA,
)


def find_possible_modes_for_chord(borrowed_chord_name: str, tonic_name: str) -> list[str]:
    """
    Analyse un accord et retourne la liste des modes parallèles auxquels il
    appartient diatoniquement, en se basant sur les notes.

    Args:
        borrowed_chord_name (str): Le nom de l'accord à analyser (ex: "Emaj7").
        tonic_name (str): La tonique de référence (ex: "C").

    Returns:
        list: Une liste de noms de modes où l'accord est diatonique.
    """
    # 1. Obtenir les notes de l'accord à tester.
    try:
        chord_notes = get_chord_notes(borrowed_chord_name)
        if not chord_notes:
            return []
    except (ValueError, TypeError):
        return []

    possible_modes = []
    chord_notes_set = set(chord_notes)

    # 2. Tester chaque mode défini dans nos données.
    for mode_name in MODES_DATA:
        try:
            # 3. Obtenir les notes de la gamme pour le mode en cours.
            scale_notes = get_scale_notes(tonic_name, mode_name)
            scale_notes_set = set(scale_notes)

            # 4. Vérifier si l'ensemble des notes de l'accord est un sous-ensemble
            #    des notes de la gamme. C'est la définition d'un accord diatonique.
            if chord_notes_set.issubset(scale_notes_set):
                possible_modes.append(mode_name)

        except (ValueError, TypeError):
            # Ignore les modes ou toniques qui pourraient être invalides.
            continue

    return possible_modes


def get_borrowed_chords(quality_analysis: List[QualityAnalysisItem], original_mode: str) -> dict:
    """
    Identifie les accords empruntés à partir d'une analyse de progression.
    """
    borrowed_chords = {}

    # Détermine si le mode d'origine est majeur ou mineur.
    mode_info = MODES_DATA.get(original_mode)
    if not mode_info:
        return {}  # Mode d'origine inconnu, on ne peut rien faire.

    original_mode_first_quality = mode_info[1][0]
    original_mode_core_quality = CORE_QUALITIES.get(original_mode_first_quality)

    for analysis_item in quality_analysis:
        # On ne traite que les accords non-diatoniques au mode d'origine.
        if not analysis_item.get("is_diatonic"):
            chord_name = analysis_item.get("chord")
            if chord_name is None:
                continue
            chord_name = chord_name
            found_quality = analysis_item.get("found_quality")
            base_numeral = analysis_item.get("found_numeral")

            # Règle d'exception : le V7 en tonalité mineure est une altération
            # si commune qu'il n'est généralement pas considéré comme un emprunt.
            if (
                original_mode_core_quality == "minor"
                and base_numeral == "V"
                and found_quality == "7"
            ):
                continue

            # Pour tous les autres, on cherche d'où ils pourraient venir.
            segment_context = analysis_item.get("segment_context", {})
            if "tonic" in segment_context:
                tonic_name = segment_context["tonic"]
                possible_modes = find_possible_modes_for_chord(chord_name, tonic_name)

                # Filtrer pour ne garder que les modes qui ne sont pas le mode original.
                if possible_modes:
                    modes_str_list = [mode for mode in possible_modes if mode != original_mode]
                    if modes_str_list:
                        borrowed_chords[chord_name] = modes_str_list
            else:
                # Si on n'a pas de contexte, on ne peut rien faire.
                print(
                    f"Warning: No segment context for chord {chord_name} "
                    "cannot determine borrowed modes."
                )
                continue

    return borrowed_chords
