from app.utils.common import get_note_from_index, is_dominant_chord, parse_chord


def get_tritone_substitute(chord_name):
    """
    Calcule le substitut tritonique pour un accord donné.
    Retourne le substitut et une note explicative.
    """
    parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return " ", " - "

    # La substitution tritonique ne s'applique qu'aux accords de dominante.
    if not is_dominant_chord(chord_name, parsed_chord):
        return "", "Non dominant"

    root_index, _ = parsed_chord

    # Calculer la nouvelle fondamentale (à +6 demi-tons)
    sub_root_index = (root_index + 6) % 12
    sub_root_name = get_note_from_index(sub_root_index)

    # Le substitut est toujours un accord de 7ème de dominante
    sub_chord_name = f"{sub_root_name}7"

    # Trouver les guide tones pour l'explication
    original_third_index = (root_index + 4) % 12
    original_seventh_index = (root_index + 10) % 12
    guide_tones = (
        f"{get_note_from_index(original_third_index)} & "
        f"{get_note_from_index(original_seventh_index)}"
    )

    return sub_chord_name, guide_tones
