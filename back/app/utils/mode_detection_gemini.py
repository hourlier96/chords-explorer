import json
import os

import google.generativeai as genai

from constants import MODES_DATA


def extract_json_from_response(text: str) -> str:
    """
    Extrait une chaîne JSON d'un texte pouvant contenir des balises Markdown.
    """
    try:
        first_brace = text.index("{")
        last_brace = text.rindex("}")
        return text[first_brace : last_brace + 1]
    except ValueError:
        raise ValueError("Aucun objet JSON valide n'a été trouvé dans la réponse de l'IA.")


def detect_tonic_and_mode(progression: list[str], model) -> dict:
    """
    Détermine la tonique, le mode et les explications d'une progression
    en utilisant l'API Google Gemini pour une analyse plus fiable et performante.
    """

    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception:
        raise ValueError(
            "Clé API Gemini non trouvée. Veuillez la définir dans vos variables d'environnement."
        )

    # --- Initialisation du modèle ---
    model = genai.GenerativeModel(model)

    # --- Création du prompt ---
    # Le prompt est modifié pour demander des explications détaillées avant la tonique et le mode.
    # Nouveau prompt amélioré
    prompt = (
        "# Rôle et Objectif\n"
        "Tu es un expert en théorie musicale. Analyse une progression d'accords pour "
        "identifier ses différents centres harmoniques. Une progression peut avoir une "
        "tonalité globale mais moduler ou faire des emprunts passagers à d'autres tonalités.\n\n"
        "# Instructions et Contraintes Strictes\n"
        "1. **Analyse Globale :** Identifie d'abord la tonalité principale ou le point "
        "de départ de la progression.\n"
        "2. **Segments Harmoniques :** Découpe la progression en segments logiques "
        "(ex: cadences ii-V-I, modulations). Pour chaque segment, identifie sa tonalité "
        "(tonique et mode) et sa fonction.\n"
        "3. **Format de Sortie :** Ta réponse doit **impérativement** être un objet JSON "
        "unique, sans aucun texte avant ou après. L'objet JSON doit contenir deux clés "
        "principales : `global_analysis` et `harmonic_segments`.\n\n"
        "# Structure JSON Détaillée\n"
        "```json\n"
        "{\n"
        '  "global_analysis": {\n'
        '    "tonic": "Eb",\n'
        '    "mode": "Ionian",\n'
        '    "explanation": "La progression est globalement en Mi bémol majeur mais '
        'utilise des cadences secondaires pour voyager."\n'
        "  },\n"
        '  "harmonic_segments": [\n'
        "    {\n"
        '      "start_index": 0,\n'
        '      "end_index": 2,\n'
        '      "tonic": "Bb",\n'
        '      "mode": "Ionian",\n'
        '      "explanation": "Cadence ii-V-I vers Si bémol majeur, le Vème degré de '
        'la tonalité principale."\n'
        "    },\n"
        "    {\n"
        '      "start_index": 3,\n'
        '      "end_index": 3,\n'
        '      "tonic": "Eb",\n'
        '      "mode": "Ionian",\n'
        '      "explanation": "Résolution sur la tonique principale."\n'
        "    },\n"
        "    {\n"
        '      "start_index": 4,\n'
        '      "end_index": 6,\n'
        '      "tonic": "G",\n'
        '      "mode": "Aeolian",\n'
        '      "explanation": "Cadence ii-V-i vers Sol mineur, le iiième degré."\n'
        "    },\n"
        "    {\n"
        '      "start_index": 7,\n'
        '      "end_index": 7,\n'
        '      "tonic": "C",\n'
        '      "mode": "Aeolian",\n'
        '      "explanation": "Accord de dominante (V7/vi) préparant le retour au '
        'début (Cm7)."\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n\n"
        "**Contraintes sur les valeurs :**\n"
        "- Les indices `start_index` et `end_index` sont basés sur 0.\n"
        f"- Le `mode` doit **obligatoirement** appartenir à la liste suivante : "
        f"{list(MODES_DATA.keys())}.\n"
        "--- \n"
        f"Progression à analyser : {' - '.join(progression)}"
    )

    try:
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        json_string = extract_json_from_response(raw_text)
        analysis_data = json.loads(json_string)
        return analysis_data
    except Exception as e:
        print(f"Une erreur est survenue: {e}")
        raise
