import pytest

from app.modal_substitution.generator import (
    get_substitution_info,
    get_substitutions,
)


class TestGetSubstitutionInfo:
    """
    Tests pour la nouvelle fonction `get_substitution_info`.
    """

    def test_empty_list(self):
        """Vérifie qu'une liste vide en entrée retourne une liste vide."""
        assert get_substitution_info([]) == []

    @pytest.mark.parametrize(
        "analysis, expected",
        [
            # Cas 1: Mix de triades et d'accords de 7e
            (
                [
                    {"found_numeral": "Imaj7", "found_quality": "maj7"},  # Accord de 7e
                    {"found_numeral": "V", "found_quality": ""},  # Triade
                    {"found_numeral": "vim", "found_quality": "m"},  # Triade
                ],
                [
                    {"degree": 1, "is_triad": False},
                    {"degree": 5, "is_triad": True},
                    {"degree": 6, "is_triad": True},
                ],
            ),
            # Cas 2: Accords non-substituables (chromatiques/secondaires)
            (
                [
                    {"found_numeral": "(V7/V)", "found_quality": "7"},
                    {"found_numeral": "iim7", "found_quality": "m7"},
                ],
                [None, {"degree": 2, "is_triad": False}],
            ),
            # Cas 3: Entrées vides ou invalides
            (
                [
                    {},
                    {"found_numeral": ""},
                    {"found_numeral": "VIII", "found_quality": "M"},  # Chiffrage invalide
                ],
                [None, None, None],
            ),
        ],
    )
    def test_various_cases(self, analysis, expected):
        """Teste plusieurs scénarios de conversion de chiffrages en informations de substitution."""
        # On simule la présence de la constante globale dans la fonction testée
        # En pratique, elle serait importée directement dans le module.
        assert get_substitution_info(analysis) == expected


# --- Tests pour get_substitutions ---


class TestGetSubstitutions:
    """
    Tests pour la fonction `get_substitutions` mise à jour.
    """

    def test_mixed_triad_and_seventh_substitution(self):
        """
        Teste une substitution qui doit générer à la fois des triades et des accords de 7e.
        Substitution en Do Ionien (Majeur), tonique_index = 0.
        """
        progression = ["Dm", "G7", "C"]
        sub_info = [
            {"degree": 4, "is_triad": True},  # Doit générer F (triade)
            {"degree": 2, "is_triad": False},  # Doit générer Dm7 (7e)
            {"degree": 6, "is_triad": True},  # Doit générer Am (triade)
        ]
        result = get_substitutions(progression, 0, sub_info)

        expected = [
            {"chord": "F", "roman": "IV", "quality": ""},
            {"chord": "Dm7", "roman": "ii", "quality": "m7"},
            {"chord": "Am", "roman": "vi", "quality": "m"},
        ]
        assert result == expected

    def test_substitution_with_skipped_chord(self):
        """
        Teste une substitution en Ré Majeur où un accord est ignoré (`None`).
        L'accord ignoré doit conserver son nom d'origine.
        """
        progression = ["Gmaj7", "A7"]
        sub_info = [
            {"degree": 6, "is_triad": False},  # Doit générer Bm7
            None,  # Doit être ignoré
        ]
        result = get_substitutions(progression, 2, sub_info)  # Tonique = D

        expected = [
            # Le VIe degré de Ré Majeur est Si mineur 7 (Bm7).
            {"chord": "Bm7", "roman": "vi", "quality": "m7"},
            # L'accord ignoré reprend les infos de la progression originale.
            {
                "chord": "A7",
                "roman": None,
                "quality": None,
            },
        ]
        assert result == expected

    def test_empty_substitution_info(self):
        """
        Vérifie qu'une liste vide est retournée si la liste d'infos est vide.
        """
        progression = ["C", "G", "Am"]
        expected = []
        result = get_substitutions(progression, 0, [])
        assert result == expected

    def test_all_none_in_substitution_info(self):
        """
        Vérifie le comportement si toutes les informations de substitution sont None.
        La fonction doit retourner la progression originale.
        """
        progression = ["Fm", "C7"]
        sub_info = [None, None]
        result = get_substitutions(progression, 0, sub_info)

        expected = [
            {
                "chord": "Fm",
                "roman": None,
                "quality": None,
            },
            {
                "chord": "C7",
                "roman": None,
                "quality": None,
            },
        ]
        assert result == expected
