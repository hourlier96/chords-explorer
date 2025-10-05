from app.utils.common import (
    format_numeral,
    get_chord_notes,
    get_note_from_index,
    get_note_index,
    get_scale_notes,
    parse_chord,
)
from constants import CORE_QUALITIES, MODES_DATA, ROMAN_DEGREES


def is_chord_diatonic(chord_name, tonic_name, mode_name):
    """
    Vérifie si toutes les notes d'un accord appartiennent à une gamme donnée.
    C'est la nouvelle fonction de base pour la compatibilité.
    """
    try:
        scale_notes = get_scale_notes(tonic_name, mode_name)
        chord_notes = get_chord_notes(chord_name)

        # Si l'accord ou la gamme n'est pas valide, il n'est pas diatonique.
        if not scale_notes or not chord_notes:
            return False

        # Vérifie si l'ensemble des notes de l'accord est un sous-ensemble des notes de la gamme.
        return set(chord_notes).issubset(set(scale_notes))
    except (ValueError, TypeError):
        # En cas d'erreur (ex: nom de mode invalide), on considère l'accord non diatonique.
        return False


def get_roman_numeral(chord_name, tonic_index, mode_name):
    """
    Analyse un accord et retourne un tuple contenant le chiffrage attendu (diatonique)
    et le chiffrage réel (joué), en utilisant une analyse par les notes.
    """
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return (f"({chord_name})", f"({chord_name})")

    chord_index, found_quality = parsed_chord
    interval = (chord_index - tonic_index + 12) % 12

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    if interval not in mode_intervals:
        return (f"({chord_name})", f"({chord_name})")

    degree_index = mode_intervals.index(interval)
    base_numeral = ROMAN_DEGREES[degree_index]
    expected_quality = mode_qualities[degree_index]

    expected_numeral = format_numeral(base_numeral, expected_quality)
    found_numeral = format_numeral(base_numeral, found_quality)

    # La logique de compatibilité est remplacée par un appel direct à is_chord_diatonic.
    tonic_name = get_note_from_index(tonic_index)
    if is_chord_diatonic(chord_name, tonic_name, mode_name):
        return (expected_numeral, found_numeral)
    else:
        # Si l'accord n'est pas diatonique, on met son chiffrage entre parenthèses.
        return (expected_numeral, f"({found_numeral})")


def get_secondary_dominant_for_target(target_chord_name, tonic_name, mode_name):
    """
    Calcule la dominante (primaire ou secondaire) qui cible un accord donné.
    Retourne la dominante et son analyse fonctionnelle dans la tonalité.
    """
    if not target_chord_name:
        return "N/A", "Pas d'accord d'origine"
    parsed_target = parse_chord(target_chord_name)
    if not parsed_target:
        return "N/A", "Accord non reconnu"

    target_root_index, target_quality = parsed_target

    # On ne crée généralement pas de dominante pour une cible diminuée.
    if CORE_QUALITIES.get(target_quality) == "diminished":
        return "N/A", "(Cible diminuée)"

    # 1. Trouver la fondamentale de la dominante (une quinte juste au-dessus de la cible)
    dominant_root_index = (target_root_index + 7) % 12
    dominant_root_name = get_note_from_index(dominant_root_index)
    dominant_chord = f"{dominant_root_name}7"

    # 2. Analyser la fonction de cette dominante dans la tonalité
    tonic_index = get_note_index(tonic_name)
    _, target_numeral = get_roman_numeral(target_chord_name, tonic_index, mode_name)

    # Cas spécial : si la cible est la tonique (I), c'est la dominante primaire.
    # On vérifie si le chiffrage (sans parenthèses) commence par 'I'.
    if target_numeral.strip("()").upper().startswith("I"):
        analysis = "V7 (Dominante Primaire)"
    else:
        analysis = f"V7/{target_numeral}"

    return dominant_chord, analysis
