from typing import Dict, List, Optional, Tuple

NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
NOTE_INDEX_MAP = {
    "C": 0,
    "B#": 0,
    "C#": 1,
    "DB": 1,
    "Db": 1,
    "D": 2,
    "D#": 3,
    "EB": 3,
    "Eb": 3,
    "E": 4,
    "FB": 4,
    "Fb": 4,
    "F": 5,
    "E#": 5,
    "F#": 6,
    "GB": 6,
    "Gb": 6,
    "G": 7,
    "G#": 8,
    "AB": 8,
    "Ab": 8,
    "A": 9,
    "A#": 10,
    "BB": 10,
    "Bb": 10,
    "B": 11,
    "CB": 11,
    "Cb": 11,
}

ROMAN_DEGREES = ["I", "II", "III", "IV", "V", "VI", "VII"]

CHROMATIC_DEGREES_MAP = {
    0: "I",
    1: "bII",
    2: "II",
    3: "bIII",
    4: "III",
    5: "IV",
    6: "#IV",
    7: "V",
    8: "bVI",
    9: "VI",
    10: "bVII",
    11: "VII",
}

ROMAN_TO_DEGREE_MAP = {
    # Diatoniques
    "I": 1,
    "II": 2,
    "III": 3,
    "IV": 4,
    "V": 5,
    "VI": 6,
    "VII": 7,
    # Chromatiques
    "bII": 2,
    "bIII": 3,
    "bV": 5,
    "bVI": 6,
    "bVII": 7,
    "#I": 1,
    "#II": 2,
    "#IV": 4,
    "#V": 5,
    "#VI": 6,
}

CORE_QUALITIES = {
    # Majeurs
    "": "major",
    "M": "major",
    "maj": "major",
    "maj7": "major",
    "maj7b5": "major",
    "maj7#5": "major",
    "maj7#11": "major",
    "maj9": "major",
    "maj13": "major",
    "6": "major",
    "6/9": "major",
    "add9": "major",
    # Mineurs
    "m": "minor",
    "min": "minor",
    "m7": "minor",
    "m6": "minor",
    "m9": "minor",
    "m11": "minor",
    "m13": "minor",
    "m(maj7)": "minor",
    "m(add9)": "minor",
    # Dominantes
    "7": "dominant",
    "9": "dominant",
    "11": "dominant",
    "13": "dominant",
    "7b5": "dominant",
    "7#5": "dominant",
    "7b9": "dominant",
    "7b13": "dominant",
    "7#9": "dominant",
    "7#11": "dominant",
    "13#11": "dominant",
    "7alt": "dominant",
    "7b9b5": "dominant",
    "7b9#5": "dominant",
    "7#9b5": "dominant",
    "7#9#5": "dominant",
    "7b9#9": "dominant",
    "7b9#11": "dominant",
    "7#9#11": "dominant",
    "7b9b13": "dominant",
    "7#9b13": "dominant",
    # Diminués
    "dim": "diminished",
    "d": "diminished",
    "dim7": "diminished",
    "m7b5": "diminished",
    # Augmentés
    "aug": "augmented",
    # Suspendus
    "sus2": "suspended",
    "sus4": "suspended",
    "7sus2": "suspended",
    "7sus4": "suspended",
    "9sus4": "suspended",
    # Autres
    "5": "power",
}

MODES_DATA: Dict[str, Tuple[List[int], List[str], Optional[int]]] = {}
MAJOR_MODES_DATA = {
    "Ionian": (
        [0, 2, 4, 5, 7, 9, 11],
        ["maj7", "m7", "m7", "maj7", "7", "m7", "m7b5"],
        0,
    ),
    "Dorian": (
        [0, 2, 3, 5, 7, 9, 10],
        ["m7", "m7", "maj7", "7", "m7", "m7b5", "maj7"],
        -2,
    ),
    "Phrygian": (
        [0, 1, 3, 5, 7, 8, 10],
        ["m7", "maj7", "7", "m7", "m7b5", "maj7", "m7"],
        -4,
    ),
    "Lydian": (
        [0, 2, 4, 6, 7, 9, 11],
        ["maj7", "7", "m7", "m7b5", "maj7", "m7", "m7"],
        -5,
    ),
    "Mixolydian": (
        [0, 2, 4, 5, 7, 9, 10],
        ["7", "m7", "m7b5", "maj7", "m7", "m7", "maj7"],
        -7,
    ),
    "Aeolian": (
        [0, 2, 3, 5, 7, 8, 10],
        ["m7", "m7b5", "maj7", "m7", "m7", "maj7", "7"],
        -9,
    ),
    "Locrian": (
        [0, 1, 3, 5, 6, 8, 10],
        ["m7b5", "maj7", "m7", "m7", "maj7", "7", "m7"],
        -11,
    ),
}

# --- Modes de la gamme mineure harmonique ---
HARMONIC_MINOR_MODES = {
    "Harmonic Minor": (
        [0, 2, 3, 5, 7, 8, 11],
        ["m(maj7)", "m7b5", "maj7#5", "m7", "7", "maj7", "dim7"],
        None,
    ),
    "Ionian #5": (
        [0, 2, 4, 5, 8, 9, 11],
        ["maj7#5", "m7", "7", "maj7", "dim7", "m(maj7)", "m7b5"],
        None,
    ),
    "Dorian #4": (
        [0, 2, 3, 6, 7, 9, 10],
        ["m7", "7", "maj7", "dim7", "m(maj7)", "m7b5", "maj7#5"],
        None,
    ),
    "Phrygian Dominant": (
        [0, 1, 4, 5, 7, 8, 10],
        ["7", "maj7", "dim7", "m(maj7)", "m7b5", "maj7#5", "m7"],
        None,
    ),
    "Lydian #2": (
        [0, 3, 4, 6, 7, 9, 11],
        ["maj7", "dim7", "m(maj7)", "m7b5", "maj7#5", "m7", "7"],
        None,
    ),
    "Locrian ♮6": (
        [0, 1, 3, 5, 6, 9, 10],
        ["m7b5", "maj7#5", "m7", "7", "maj7", "dim7", "m(maj7)"],
        None,
    ),
    "Super Locrian bb7": (
        [0, 1, 3, 4, 6, 8, 9],
        ["dim7", "m(maj7)", "m7b5", "maj7#5", "m7", "7", "maj7"],
        None,
    ),
}

# --- Modes de la gamme mineure mélodique ---
MELODIC_MINOR_MODES = {
    "Melodic Minor": (
        [0, 2, 3, 5, 7, 9, 11],
        ["m(maj7)", "m7", "maj7#5", "7", "7", "m7b5", "m7b5"],
        None,
    ),
    "Dorian b2": (
        [0, 1, 3, 5, 7, 9, 10],
        ["m7", "maj7#5", "7", "7", "m7b5", "m7b5", "m(maj7)"],
        None,
    ),
    "Lydian #5": (
        [0, 2, 4, 6, 8, 9, 11],
        ["maj7#5", "7", "7", "m7b5", "m7b5", "m(maj7)", "m7"],
        None,
    ),
    "Lydian Dominant": (
        [0, 2, 4, 6, 7, 9, 10],
        ["7", "7", "m7b5", "m7b5", "m(maj7)", "m7", "maj7#5"],
        None,
    ),
    "Mixolydian b6": (
        [0, 2, 4, 5, 7, 8, 10],
        ["7", "m7b5", "m7b5", "m(maj7)", "m7", "maj7#5", "7"],
        None,
    ),
    "Locrian ♮2": (
        [0, 2, 3, 5, 6, 8, 10],
        ["m7b5", "m7b5", "m(maj7)", "m7", "maj7#5", "7", "7"],
        None,
    ),
    "Altered Scale": (
        [0, 1, 3, 4, 6, 8, 10],
        ["m7b5", "m(maj7)", "m7", "maj7#5", "7", "7", "m7b5"],
        None,
    ),
}

MODES_DATA.update(MAJOR_MODES_DATA)
MODES_DATA.update(HARMONIC_MINOR_MODES)
MODES_DATA.update(MELODIC_MINOR_MODES)
