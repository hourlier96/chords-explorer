from app.utils.borrowed_modes import find_possible_modes_for_chord, get_borrowed_chords


def test_find_modes_for_major_iv_chord():
    """Teste que Fmaj en Do est bien identifié dans tous les modes compatibles."""
    result = find_possible_modes_for_chord("F", "C")
    expected = {
        "Ionian",
        "Dorian",
        "Mixolydian",
        "Melodic Minor",
        "Ionian #5",
        "Locrian ♮6",
        "Dorian b2",
    }
    assert set(result) == expected


def test_find_modes_for_minor_ii_chord():
    """Teste qu'un accord mineur (iimin) est associé aux bons modes."""
    result = find_possible_modes_for_chord("Dmin", "C")
    expected = {"Ionian", "Dorian", "Mixolydian", "Melodic Minor", "Ionian #5"}
    assert set(result) == expected


def test_find_modes_for_borrowed_flat_vii():
    """Teste un emprunt classique au parallèle mineur : l'accord bVIImaj."""
    result = find_possible_modes_for_chord("Bb", "C")
    expected = {"Dorian", "Mixolydian", "Aeolian", "Mixolydian b6", "Locrian ♮2"}
    assert set(result) == expected


def test_find_modes_for_diminished_chord():
    """Teste qu'un accord diminué est correctement localisé."""
    result = find_possible_modes_for_chord("Gdim", "C")
    expected = {"Phrygian", "Dorian b2", "Phrygian Dominant"}
    assert set(result) == expected


def test_find_modes_for_distant_chord():
    """Teste qu'un accord distant est correctement localisé dans les modes exotiques."""
    # F#maj n'est pas dans les modes standards de Do, mais il est diatonique à certains.
    result = find_possible_modes_for_chord("F#", "C")
    expected = {"Locrian", "Locrian ♮6", "Altered Scale"}
    assert set(result) == expected


def test_find_modes_for_invalid_chord_name():
    """Teste que la fonction gère un nom d'accord invalide et retourne une liste vide."""
    result = find_possible_modes_for_chord("C-Invalide", "C")
    assert result == []


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
    result = get_borrowed_chords(analysis, "Ionian")
    expected = {"Bb": ["Dorian", "Mixolydian", "Aeolian", "Mixolydian b6", "Locrian ♮2"]}

    if "Bb" in result:
        result["Bb"].sort()
    expected["Bb"].sort()
    assert result == expected


def test_get_borrowed_skips_standard_v7_in_minor():
    """Vérifie que le V7 en mode mineur est bien ignoré (altération standard)."""
    analysis = [
        {
            "chord": "Amin",
            "is_diatonic": True,
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
    result = get_borrowed_chords(analysis, "Aeolian")
    assert result == {}


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
    result = get_borrowed_chords(analysis, "Aeolian")
    expected = {"B": ["Dorian #4", "Lydian", "Lydian #5", "Lydian Dominant"]}

    if "B" in result:
        result["B"].sort()
    expected["B"].sort()
    assert result == expected


def test_get_borrowed_filters_original_mode_from_results():
    """Teste que le mode d'origine est bien retiré de la liste."""
    analysis = [
        {"chord": "Cmin", "is_diatonic": True, "segment_context": {"tonic": "C", "mode": "Dorian"}},
        {
            "chord": "Gmin",
            "is_diatonic": False,
            "found_quality": "m",
            "found_numeral": "v",
            "segment_context": {"tonic": "C", "mode": "Dorian"},
        },
    ]
    result = get_borrowed_chords(analysis, "Dorian")
    expected_modes = {
        "Aeolian",
        "Mixolydian",
        "Mixolydian b6",
        "Lydian Dominant",
        "Dorian #4",
    }

    assert "Gmin" in result
    assert set(result["Gmin"]) == expected_modes


def test_get_borrowed_with_no_borrowed_chords():
    """Teste une progression entièrement diatonique."""
    analysis = [
        {"chord": "Gmaj", "is_diatonic": True},
        {"chord": "Fmaj", "is_diatonic": True},
        {"chord": "Cmaj", "is_diatonic": True},
        {"chord": "Dmin", "is_diatonic": True},
    ]
    result = get_borrowed_chords(analysis, "Mixolydian")
    assert result == {}


def test_get_borrowed_chords_in_c_ionian():
    """
    Teste une série d'emprunts complexes dans une tonalité de Do Majeur (Ionian)
    pour vérifier que les modes d'origine corrects sont identifiés.
    """
    analysis = [
        # Dm9 est diatonique en Mixolydian (en plus de Ionian)
        {
            "chord": "Dm9",
            "is_diatonic": False,
            "segment_context": {"tonic": "C", "mode": "Ionian"},
        },
        # Fm9 est diatonique à plusieurs modes mineurs
        {
            "chord": "Fm9",
            "is_diatonic": False,
            "segment_context": {"tonic": "C", "mode": "Ionian"},
        },
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
    result = get_borrowed_chords(analysis, "Ionian")

    # Dictionnaire attendu mis à jour avec les résultats corrects de l'analyse par notes
    expected = {
        "Dm9": ["Mixolydian", "Ionian #5"],
        "Fm9": ["Aeolian", "Harmonic Minor", "Phrygian"],
        "Dm7b5": [
            "Aeolian",
            "Locrian ♮2",
            "Mixolydian b6",
            "Harmonic Minor",
            "Ionian #5",
        ],
    }

    for key in expected:
        expected[key].sort()
    for key in result:
        result[key].sort()

    # Tri des listes pour une comparaison fiable et indépendante de l'ordre
    assert result == expected
