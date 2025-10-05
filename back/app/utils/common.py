from constants import (
    CORE_QUALITIES,
    MODES_DATA,
    NOTE_INDEX_MAP,
    NOTES,
)


# Returns the chromatic index (0–11) for a given note string
def get_note_index(note_str: str) -> int:
    """
    Converts a note string (e.g., "C#", "Gb") into its chromatic index (0-11).
    This function is guaranteed to return an integer or raise a ValueError.
    """
    note_map = {
        "DB": "C#",
        "EB": "D#",
        "FB": "E",
        "GB": "F#",
        "AB": "G#",
        "BB": "A#",
        "B#": "C",
    }

    clean_note = (
        note_str.upper()
        .replace("♭", "B")
        .split("M")[0]
        .split("m")[0]
        .split("°")[0]
        .split("dim")[0]
        .split("7")[0]
        .split("ø")[0]
    )

    if not clean_note:
        raise ValueError(f"Invalid note string: '{note_str}'")

    if clean_note == "CB":
        return 11

    if clean_note in note_map:
        clean_note = note_map[clean_note]

    note_to_find = (
        clean_note[:2] if len(clean_note) > 1 and clean_note[1] in ["#", "B"] else clean_note[0]
    )

    try:
        return NOTES.index(note_to_find)
    except ValueError:
        raise ValueError(f"Note '{note_to_find}' could not be resolved to a valid index.") from None


# Returns note name from chromatic index (0–11)
def get_note_from_index(index):
    return NOTES[index % 12]


# Parses a chord name and returns its root index and a normalized quality string
def parse_chord(chord_name):
    chord_name = chord_name.strip()

    # Utilisation des qualités reconnues depuis CORE_QUALITIES
    KNOWN_QUALITIES = sorted(CORE_QUALITIES.keys(), key=lambda q: -len(q))

    for quality in KNOWN_QUALITIES:
        if chord_name.endswith(quality):
            root = chord_name[: -len(quality)] if len(quality) > 0 else chord_name
            try:
                root_index = get_note_index(root)
                return root_index, quality
            except ValueError:
                return None

    # Si aucun suffixe ne matche, on tente un accord majeur simple
    try:
        root_index = get_note_index(chord_name)
        return root_index, ""
    except ValueError:
        return None


def is_dominant_chord(chord_name, parsed_chord=None):
    """
    Vérifie si un accord est un accord de dominante.
    Un accord est considéré comme dominant si sa qualité de base est 'dominant',
    ou s'il s'agit d'une triade majeure simple (qui peut fonctionner comme un dominant).
    """
    if not parsed_chord:
        # Note: Assurez-vous que les fonctions parse_chord et _get_core_quality
        # sont disponibles dans le même scope.
        parsed_chord = parse_chord(chord_name)
    if not parsed_chord:
        return False

    _, quality = parsed_chord
    core_quality = _get_core_quality(quality)

    # 1. Les accords dont la qualité de base est 'dominant' le sont toujours.
    if core_quality == "dominant":
        return True

    # 2. Une triade majeure simple (sans extensions comme 6, 9, maj7) peut
    # fonctionner comme un accord de dominante. Nous acceptons les qualités
    # qui représentent une triade majeure simple.
    if core_quality == "major" and quality in ["", "M", "maj"]:
        return True

    # 3. Tous les autres types d'accords ne sont pas considérés comme dominants.
    return False


# Returns a diatonic 7th chord for a degree and tonic, with optional simplification
def get_diatonic_7th_chord(degree, key_tonic_index, mode_name="Ionian"):
    """
    Génère un accord de septième diatonique à partir d'un degré, d'une tonique et d'un mode.
    Cette version est robuste et gère les degrés invalides.
    """
    if degree is None or not (1 <= degree <= 7):
        return None

    mode_intervals, mode_qualities, _ = MODES_DATA[mode_name]

    chord_root_index = (key_tonic_index + mode_intervals[degree - 1]) % 12
    quality = mode_qualities[degree - 1]
    name = get_note_from_index(chord_root_index)

    return name + quality


def _get_core_quality(quality):
    if quality in CORE_QUALITIES:
        return CORE_QUALITIES[quality]
    # Cas non reconnu : essayer de simplifier
    if quality.startswith("maj"):
        return "major"
    if quality.startswith("m"):
        return "minor"
    if quality.startswith("dim") or quality.startswith("d") or quality.startswith("°"):
        return "diminished"
    if quality.startswith("aug") or quality.startswith("+"):
        return "augmented"
    if "sus" in quality:
        return "suspended"
    if "5" in quality:
        return "power"
    return "major"  # fallback


def get_scale_notes(key_tonic_str: str, mode_name: str) -> list[str]:
    """
    Génère la liste des notes d'une gamme à partir d'une tonique et d'un mode.
    """
    # 1. Valider et normaliser la tonique
    root_note = key_tonic_str[0].upper()
    accidental = key_tonic_str[1:]

    # Gère les bémols en cherchant l'équivalent diésé (ex: Bb -> A#)
    # Ne touche pas à la note "B" seule.
    if accidental == "b":
        # On calcule l'index de la note bémolisée et on prend la note diésée correspondante
        flat_index = (NOTE_INDEX_MAP[root_note] - 1 + 12) % 12
        tonic_normalized = NOTES[flat_index]
    else:
        # Pour les notes naturelles ou diésées
        tonic_normalized = key_tonic_str

    if tonic_normalized not in NOTE_INDEX_MAP:
        raise ValueError(f"Tonic '{key_tonic_str}' could not be normalized or is invalid.")

    tonic_index = NOTE_INDEX_MAP[tonic_normalized]

    # 2. Valider le mode
    found_mode_key = next((key for key in MODES_DATA if key.lower() == mode_name.lower()), None)
    if not found_mode_key:
        raise ValueError(f"Mode '{mode_name}' not found.")

    # 3. Récupérer les intervalles et construire la gamme
    intervals = MODES_DATA[found_mode_key][0]
    scale_notes = [(NOTES[(tonic_index + i) % 12]) for i in intervals]

    return scale_notes


def format_numeral(base_numeral, quality):
    core_quality = CORE_QUALITIES.get(quality, "major")
    numeral = base_numeral.lower() if core_quality in ["minor", "diminished"] else base_numeral
    suffix_map = {
        "maj7": "maj7",
        "m7": "7",
        "7": "7",
        "m7b5": "ø7",
        "dim7": "°7",
        "dim": "°",
        "aug": "+",
        "sus4": "sus4",
        "sus2": "sus2",
        "add9": "add9",
        "m(maj7)": "m(maj7)",
        "m6": "m6",
        "m9": "m9",
        "m11": "m11",
        "m13": "m13",
        "9": "9",
        "11": "11",
        "13": "13",
    }
    suffix = suffix_map.get(quality, "")
    return numeral + suffix


def get_chord_notes(chord_name: str) -> list[str] | None:
    """
    Analyse un nom d'accord et renvoie ses notes constitutives.
    Cette version est autonome et définit ses propres constantes pour éviter
    les problèmes d'environnement.

    Args:
        chord_name (str): Le nom de l'accord (ex: "C6", "F#m7", "Bb").

    Returns:
        list[str] | None: Une liste de notes ou None si l'accord est invalide.
    """

    CHORD_FORMULAS = {
        # --- Triades de base ---
        "": [0, 4, 7],
        "M": [0, 4, 7],
        "maj": [0, 4, 7],
        "m": [0, 3, 7],
        "min": [0, 3, 7],
        "dim": [0, 3, 6],
        "d": [0, 3, 6],
        "aug": [0, 4, 8],
        "+": [0, 4, 8],
        "5": [0, 7],
        # --- Accords suspendus ---
        "sus2": [0, 2, 7],
        "sus4": [0, 5, 7],
        "7sus2": [0, 2, 7, 10],
        "7sus4": [0, 5, 7, 10],
        "9sus4": [0, 5, 7, 10, 14],
        "13sus4": [0, 5, 7, 10, 14, 21],
        # --- Accords "add" ---
        "add9": [0, 4, 7, 14],
        "m(add9)": [0, 3, 7, 14],
        # --- Accords de 6ème ---
        "6": [0, 4, 7, 9],
        "m6": [0, 3, 7, 9],
        "6/9": [0, 4, 7, 9, 14],
        # --- Accords de 7ème ---
        "7": [0, 4, 7, 10],
        "maj7": [0, 4, 7, 11],
        "m7": [0, 3, 7, 10],
        "dim7": [0, 3, 6, 9],
        "m7b5": [0, 3, 6, 10],
        "m(maj7)": [0, 3, 7, 11],
        "maj7b5": [0, 4, 6, 11],
        "maj7#5": [0, 4, 8, 11],
        "maj7#11": [0, 4, 7, 11, 18],
        # --- Accords de dominante altérés ---
        "7b5": [0, 4, 6, 10],
        "7#5": [0, 4, 8, 10],
        "7b9": [0, 4, 7, 10, 13],
        "7b13": [0, 4, 7, 10, 20],
        "7#9": [0, 4, 7, 10, 15],
        "7#11": [0, 4, 7, 10, 18],
        "7alt": [0, 4, 10, 13, 18],  # Altéré générique : b9 et #11
        "7b9b5": [0, 4, 6, 10, 13],
        "7b9#5": [0, 4, 8, 10, 13],
        "7#9b5": [0, 4, 6, 10, 15],
        "7#9#5": [0, 4, 8, 10, 15],
        "7b9#9": [0, 4, 7, 10, 13, 15],  # double altération de la 9e
        "7b9#11": [0, 4, 7, 10, 13, 18],
        "7#9#11": [0, 4, 7, 10, 15, 18],
        "7b9b13": [0, 4, 7, 10, 13, 20],  # b13 = A# = +20 demi-tons
        "7#9b13": [0, 4, 7, 10, 15, 20],
        # --- Accords de 9ème ---
        "9": [0, 4, 7, 10, 14],
        "maj9": [0, 4, 7, 11, 14],
        "m9": [0, 3, 7, 10, 14],
        # --- Accords de 11ème ---
        "11": [0, 4, 7, 10, 14, 17],
        "m11": [0, 3, 7, 10, 14, 17],
        # --- Accords de 13ème ---
        "13": [0, 4, 7, 10, 14, 21],
        "13#11": [0, 4, 7, 10, 14, 18, 21],
        "m13": [0, 3, 7, 10, 14, 21],
        "maj13": [0, 4, 7, 11, 14, 21],
    }

    # Trier les qualités de la plus longue à la plus courte pour une analyse correcte
    KNOWN_QUALITIES = sorted(CHORD_FORMULAS.keys(), key=len, reverse=True)

    # --- Logique de la fonction ---
    chord_name = chord_name.strip()

    # 1. Itérer sur les qualités connues pour trouver la bonne correspondance
    for quality in KNOWN_QUALITIES:
        if chord_name.endswith(quality):
            # Extraire la partie racine potentielle
            root_str = chord_name[: -len(quality)] if quality else chord_name
            if root_str in NOTE_INDEX_MAP:
                root_index = NOTE_INDEX_MAP[root_str]

                # Construire les notes de l'accord
                intervals = CHORD_FORMULAS[quality]
                chord_notes = []
                for interval in intervals:
                    note_index = (root_index + interval) % 12
                    chord_notes.append(NOTES[note_index])
                return chord_notes

    # Si aucune correspondance n'est trouvée après la boucle, l'accord est invalide
    return None


def is_chord_diatonic(chord_name: str, key_tonic_str: str, mode_name: str) -> bool:
    """
    Vérifie si toutes les notes d'un accord appartiennent à une gamme donnée.

    Args:
        chord_name (str): Le nom de l'accord à vérifier (ex: "Am7", "Csus2").
        key_tonic_str (str): La note tonique de la gamme (ex: "C", "F#").
        mode_name (str): Le nom du mode (ex: "Ionian", "Dorian").

    Returns:
        bool: True si l'accord est diatonique, False sinon.
    """
    try:
        # 1. Obtenir les notes de la gamme de la tonalité.
        scale_notes = get_scale_notes(key_tonic_str, mode_name)

        # 2. Obtenir les notes constitutives de l'accord
        chord_notes = get_chord_notes(chord_name)

        # Gérer les cas où l'accord ou la gamme est invalide.
        if not scale_notes or not chord_notes:
            return False

    except ValueError:
        # Si get_scale_notes lève une erreur, l'accord n'est pas diatonique.
        return False

    # 3. Vérifier si chaque note de l'accord est dans la gamme.
    scale_notes_set = set(scale_notes)
    for note in chord_notes:
        if note not in scale_notes_set:
            return False  # Au moins une note est en dehors de la gamme.

    # 4. Si toutes les notes sont dans la gamme, l'accord est diatonique.
    return True
