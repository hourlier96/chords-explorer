import unittest

from app.utils.borrowed_modes import check_secondary_functions, get_borrowed_chords

# --- Données et Fonctions Mock (pour isoler le test) ---
# Recréez ici les dépendances nécessaires pour que le test soit autonome.

NOTES = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]
NOTE_TO_INDEX = {note: i for i, note in enumerate(NOTES)}
ROMAN_NUMERALS = ["I", "ii", "iii", "IV", "V", "vi", "vii°"]

MODES_DATA = {"ionian": [0, 2, 4, 5, 7, 9, 11], "harmonic minor": [0, 2, 3, 5, 7, 8, 11]}


class TestCheckSecondaryFunctions(unittest.TestCase):
    """
    Suite de tests pour la fonction check_secondary_functions.
    """

    def test_d7sus4_in_c_harmonic_minor(self):
        """
        TEST CLÉ : Vérifie que D7sus4 est bien identifié comme V/V en Do mineur harmonique.
        C'est le cas qui échouait précédemment.
        """
        # Arrange
        chord_name = "D7sus4"
        chord_notes = {"D", "G", "A", "C"}
        tonic = "C"
        mode = "Harmonic Minor"

        expected_result = {
            "origin": "Tonalité de G",
            "degree": "V/V",
            "function": "Dominante Secondaire de V",
        }

        # Act
        result = check_secondary_functions(chord_name, chord_notes, tonic, mode)

        # Assert
        self.assertIsNotNone(result, "La fonction ne devrait pas retourner None pour D7sus4.")
        self.assertEqual(result, expected_result)

    def test_standard_v7_of_v_in_c_major(self):
        """
        Teste un cas standard de V7/V en tonalité majeure.
        """
        # Arrange
        chord_name = "D7"
        chord_notes = {"D", "F#", "A", "C"}
        tonic = "C"
        mode = "Ionian"

        expected_result = {
            "origin": "Tonalité de G",
            "degree": "V/V",
            "function": "Dominante Secondaire de V",
        }

        # Act
        result = check_secondary_functions(chord_name, chord_notes, tonic, mode)

        # Assert
        self.assertEqual(result, expected_result)

    def test_v7_of_vi_in_c_major(self):
        """
        Teste une dominante secondaire visant un autre degré (le vi).
        """
        # Arrange
        chord_name = "E7"
        chord_notes = {"E", "G#", "B", "D"}
        tonic = "C"
        mode = "Ionian"

        expected_result = {
            "origin": "Tonalité de A",
            "degree": "V/VI",
            "function": "Dominante Secondaire de vi",
        }

        # Act
        result = check_secondary_functions(chord_name, chord_notes, tonic, mode)

        # Assert
        self.assertEqual(result, expected_result)

    def test_non_secondary_dominant_should_return_none(self):
        """
        Vérifie qu'un accord non-dominant mais avec la bonne fondamentale retourne bien None.
        (ex: Am7 n'est pas la dominante de Dm, même si A est la dominante de D)
        """
        # Arrange
        chord_name = "Am7"  # La dominante de Dm serait A7, pas Am7
        chord_notes = {"A", "C", "E", "G"}
        tonic = "C"
        mode = "Ionian"

        # Act
        result = check_secondary_functions(chord_name, chord_notes, tonic, mode)

        # Assert
        self.assertIsNone(
            result, "Un accord qui n'a pas de fonction de dominante (Am7) devrait retourner None."
        )


# --- Tests Unitaires pour `get_borrowed_chords` ---


def test_get_borrowed_one_chord_in_major_key():
    """Identifie un accord emprunté simple (bVII) dans une tonalité majeure."""
    analysis = [
        {"chord": "Cmaj", "is_diatonic": True, "segment_context": {"tonic": "C", "mode": "Ionian"}},
        {
            "chord": "Bb",
            "is_diatonic": False,
            "found_quality": "",
            "found_numeral": "bVII",
            "segment_context": {"tonic": "C", "mode": "Ionian"},
        },
        {"chord": "Fmaj", "is_diatonic": True, "segment_context": {"tonic": "C", "mode": "Ionian"}},
    ]
    result = get_borrowed_chords(analysis)
    expected = {"Bb": ["Dorian", "Mixolydian", "Aeolian", "Mixolydian b6", "Locrian ♮2"]}

    if "Bb" in result:
        result["Bb"].sort()
    expected["Bb"].sort()
    assert result == expected


def test_get_borrowed_finds_other_chord_in_minor():
    """Vérifie qu'un vrai emprunt en mode mineur est identifié."""
    analysis = [
        {
            "chord": "Amin",
            "is_diatonic": True,
            "segment_context": {"tonic": "A", "mode": "Aeolian"},
        },
        {
            "chord": "B",
            "is_diatonic": False,
            "found_quality": "",
            "found_numeral": "II",
            "segment_context": {"tonic": "A", "mode": "Aeolian"},
        },
        {
            "chord": "E7",
            "is_diatonic": False,
            "found_quality": "7",
            "found_numeral": "V",
            "segment_context": {"tonic": "A", "mode": "Aeolian"},
        },
    ]
    result = get_borrowed_chords(analysis)
    expected = {
        "B": ["Lydian", "Dorian #4", "Lydian #5", "Lydian Dominant"],
        "E7": ["Ionian", "Harmonic Minor", "Melodic Minor"],
    }

    if "B" in result:
        result["B"].sort()
    expected["B"].sort()
    assert result == expected


def test_get_borrowed_with_no_borrowed_chords():
    """Teste une progression entièrement diatonique."""
    analysis = [
        {"chord": "Gmaj", "is_diatonic": True},
        {"chord": "Fmaj", "is_diatonic": True},
        {"chord": "Cmaj", "is_diatonic": True},
        {"chord": "Dmin", "is_diatonic": True},
    ]
    result = get_borrowed_chords(analysis)
    assert result == {}


def test_get_borrowed_chords_in_c_ionian():
    """
    Teste une série d'emprunts complexes dans une tonalité de Do Majeur (Ionian)
    pour vérifier que les modes d'origine corrects sont identifiés.
    """
    analysis = [
        # Dm9 est diatonique en Mixolydian (en plus de Ionian)
        {"chord": "Dm9", "is_diatonic": False, "segment_context": {"tonic": "C", "mode": "Ionian"}},
        # Fm9 est diatonique à plusieurs modes mineurs
        {"chord": "Fm9", "is_diatonic": False, "segment_context": {"tonic": "C", "mode": "Ionian"}},
        # Dm7b5 est le ii de plusieurs modes mineurs
        {
            "chord": "Dm7b5",
            "is_diatonic": False,
            "segment_context": {"tonic": "C", "mode": "Ionian"},
        },
        {
            "chord": "Cmaj7",
            "is_diatonic": True,
            "segment_context": {"tonic": "C", "mode": "Ionian"},
        },
    ]
    result = get_borrowed_chords(analysis)
    expected = {
        "Dm9": ["Ionian", "Mixolydian", "Ionian #5"],
        "Fm9": ["Phrygian", "Aeolian", "Harmonic Minor"],
        "Dm7b5": ["Aeolian", "Harmonic Minor", "Ionian #5", "Mixolydian b6", "Locrian ♮2"],
    }

    for key in expected:
        expected[key].sort()
    for key in result:
        result[key].sort()

    # Tri des listes pour une comparaison fiable et indépendante de l'ordre
    assert result == expected
