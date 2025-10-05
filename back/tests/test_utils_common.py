import pytest

from app.utils.common import (
    _get_core_quality,
    get_diatonic_7th_chord,
    get_note_from_index,
    get_note_index,
    is_chord_diatonic,
    is_dominant_chord,
    parse_chord,
)


@pytest.mark.parametrize(
    "note_str, expected_index",
    [
        ("C", 0),
        ("G#", 8),
        ("Ab", 8),  # Enharmonic
        ("B", 11),
        ("B#", 0),  # Enharmonic
        ("Fb", 4),  # Enharmonic (E)
        ("Cb", 11),  # Special case
        ("Fm7", 5),  # With quality
        ("Ddim", 2),  # With quality
    ],
)
def test_get_note_index(note_str, expected_index):
    assert get_note_index(note_str) == expected_index


def test_get_note_index_invalid():
    with pytest.raises(ValueError):
        get_note_index("H")


@pytest.mark.parametrize(
    "index, expected_note",
    [(0, "C"), (8, "G#"), (11, "B"), (12, "C")],  # Modulo test
)
def test_get_note_from_index(index, expected_note):
    assert get_note_from_index(index) == expected_note


@pytest.mark.parametrize(
    "chord_name, expected_tuple",
    [
        ("Cmaj7", (0, "maj7")),
        ("G#m7", (8, "m7")),
        ("Bbm7b5", (10, "m7b5")),
        ("F#", (6, "")),
        ("Fmaj", (5, "maj")),
        ("D", (2, "")),
        ("Abm", (8, "m")),
        ("Invalid", None),
        ("Hm7", None),
        ("A#", (10, "")),
        ("Cb", (11, "")),
        ("Em", (4, "m")),
        ("Emin", (4, "min")),
        ("A7", (9, "7")),
        ("Fdim", (5, "dim")),
        ("C6/9", (0, "6/9")),
        ("G9", (7, "9")),
        ("F#11", (6, "11")),
        ("D5", (2, "5")),
        ("Cadd9", (0, "add9")),
        ("123", None),
    ],
)
def test_parse_chord(chord_name, expected_tuple):
    assert parse_chord(chord_name) == expected_tuple


@pytest.mark.parametrize(
    "chord_name, is_dominant",
    [
        ("G7", True),
        ("C9", True),
        ("A13", True),
        ("F#7#11", True),
        ("E7alt", True),
        ("A7b5", True),
        ("D7#5", True),
        ("E7b9", True),
        ("B7#9", True),
        ("F7b9b5", True),
        ("C7b9#5", True),
        ("G7#9b5", True),
        ("A7#9#5", True),
        ("E7b9#9", True),
        ("D7b9#11", True),
        ("F7#9#11", True),
        ("C7b9b13", True),
        ("G7#9b13", True),
        ("A", True),
        ("Cmaj7", False),
        ("Am7", False),
        ("Bdim", False),
        ("Gsus4", False),
        ("C6/9", False),
    ],
)
def test_is_dominant_chord(chord_name, is_dominant):
    assert is_dominant_chord(chord_name) == is_dominant


# 🧪 Tests pour get_diatonic_7th_chord
@pytest.mark.parametrize(
    "degree, key_tonic_index, mode, expected_chord",
    [
        # C Ionian
        (1, 0, "Ionian", "Cmaj7"),
        (2, 0, "Ionian", "Dm7"),
        (5, 0, "Ionian", "G7"),
        (7, 0, "Ionian", "Bm7b5"),
        # D Dorian
        (1, 2, "Dorian", "Dm7"),
        (4, 2, "Dorian", "G7"),
        (7, 2, "Dorian", "Cmaj7"),
        # Invalid degrees
        (0, 0, "Ionian", None),
        (8, 0, "Ionian", None),
    ],
)
def test_get_diatonic_7th_chord(degree, key_tonic_index, mode, expected_chord):
    assert get_diatonic_7th_chord(degree, key_tonic_index, mode) == expected_chord


@pytest.mark.parametrize(
    "quality, expected_core",
    [
        ("maj9", "major"),
        ("m7", "minor"),
        ("m7b5", "diminished"),
        ("dim7", "diminished"),
        ("aug", "augmented"),
        ("7sus4", "suspended"),
        ("", "major"),
        ("6", "major"),
        ("6/9", "major"),
        ("add9", "major"),
        ("m13", "minor"),
        ("9", "dominant"),
        ("11", "dominant"),
        ("7alt", "dominant"),
        ("9sus4", "suspended"),
        ("5", "power"),
        ("xyz", "major"),  # Fallback
    ],
)
def test_get_core_quality(quality, expected_core):
    assert _get_core_quality(quality) == expected_core


@pytest.mark.parametrize(
    "chord, key, mode, expected",
    [
        # --- Cas en Do Majeur (C Ionian) ---
        ("Cmaj7", "C", "Ionian", True),
        ("G7", "C", "Ionian", True),
        ("Am7", "C", "Ionian", True),
        ("Bm7b5", "C", "Ionian", True),
        ("C", "C", "Ionian", True),
        ("Dm", "C", "Ionian", True),
        ("G", "C", "Ionian", True),
        ("Gsus2", "C", "Ionian", True),
        ("Csus4", "C", "Ionian", True),
        ("Bsus2", "C", "Ionian", False),
        ("Gmaj7", "C", "Ionian", False),
        ("A7", "C", "Ionian", False),
        ("Em", "C", "Ionian", True),
        ("E7", "C", "Ionian", False),
        ("F#m7", "C", "Ionian", False),
        ("Db", "C", "Ionian", False),
        # --- Nouveaux accords étendus en C Majeur ---
        ("C6", "C", "Ionian", True),
        ("Cadd9", "C", "Ionian", True),
        ("G9", "C", "Ionian", True),
        ("Fmaj9", "C", "Ionian", True),
        ("Dm11", "C", "Ionian", True),  # D-F-A-C-E-G
        ("C6/9", "C", "Ionian", True),  # C-E-G-A-D
        ("G11", "C", "Ionian", True),  # G-B-D-F-A-C
        ("G5", "C", "Ionian", True),  # Power chord
        ("Am(add9)", "C", "Ionian", True),  # A-C-E-B
        # --- Cas avec une autre tonalité (Ré majeur) ---
        ("Dmaj7", "D", "Ionian", True),
        ("A7", "D", "Ionian", True),
        ("F#m7", "D", "Ionian", True),
        ("G6", "D", "Ionian", True),  # G-B-D-E
        # --- Cas avec un autre mode ---
        ("Am(maj7)", "A", "Harmonic Minor", True),
        ("Cmaj7#5", "A", "Harmonic Minor", True),
        ("E7", "A", "Harmonic Minor", True),
        ("Fmaj7", "A", "Harmonic Minor", True),
        ("G#dim7", "A", "Harmonic Minor", True),
        ("D7", "A", "Harmonic Minor", False),
        ("Emaj7", "D", "Lydian", False),
        ("E7", "D", "Lydian", True),
        ("A7#11", "A", "Lydian Dominant", True),  # A-C#-E-G-D#
        # --- Cas invalides ---
        ("InvalidChord", "C", "Ionian", False),
        ("Cmaj7", "X", "Ionian", False),
    ],
)
def test_is_chord_diatonic(chord, key, mode, expected):
    """
    Teste la fonction is_chord_diatonic avec une variété de cas.
    """
    assert is_chord_diatonic(chord, key, mode) == expected
