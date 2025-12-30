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


def detect_tonic_and_mode(progression: list[str], model: str) -> dict:
    """
    Détermine la tonique, le mode et les segments en utilisant une approche fiable
    en deux étapes pour garantir la qualité de l'analyse ET la rigueur du formatage.
    """
    # --- Configuration et Initialisation ---
    try:
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    except Exception:
        raise ValueError(
            "Clé API Gemini non trouvée. Veuillez la définir dans vos variables d'environnement."
        )

    model_instance = genai.GenerativeModel(model)
    progression_str = " - ".join(progression)

    try:
        modes_list_str = str(list(MODES_DATA.keys()))
    except NameError:
        print(
            "Avertissement : MODES_DATA non trouvé, la contrainte de mode ne sera pas dans le prompt."
        )
        modes_list_str = "['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian', 'Harmonic Minor', 'Melodic Minor']"

    # === ÉTAPE 1 : L'ANALYSE EN PROSE (Le "Penseur") ===

    prompt_step_1 = (
        "# Rôle et Objectif\n"
        "Tu es un analyste expert en harmonie et en théorie musicale. Ta mission est d'analyser en "
        "profondeur une progression d'accords. Tu dois identifier la "
        "tonalité principale et décomposer la progression en segments harmoniques logiques.\n"
        "# Concepts Clés pour l'Analyse\n"
        "1.  **Centre Harmonique (Segment) :** Un groupe d'accords articulé "
        "autour d'une tonalité locale (ex: Do ionien). Un segment est souvent défini par une "
        "cadence forte (ex: ii-V-I, V-i).\n"
        "2.  **Accords Non-Diatoniques :** Identifie leur fonction "
        "(ex: dominante secondaire, emprunt modal).\n"
        "3.  **Notation Enharmonique :** Utilise la notation la plus logique "
        "(ex: Bbmaj7 au lieu de A#maj7 en Fa majeur).\n"
        "# Instructions\n"
        "1.  **Synthèse Initiale :** Commence par donner la tonalité principale (tonique et mode).\n"
        "2.  **Segmentation Logique :** Découpe la progression en centres harmoniques. "
        "Un segment doit contenir au moins 4 accords. Deux segments adjacents "
        "ne peuvent pas avoir le même centre tonal.\n"
        "3.  **Format de Sortie :** Réponds en **prose (texte simple)**. "
        "   - Pour l'analyse globale, écris : `Analyse Globale: [tonique] - [mode] - [explication]`\n"
        "   - Pour chaque segment, écris : `Segment: [start_index] à [end_index] - [tonique] - [mode] - [explication]`\n"
        "--- \n"
        f"Progression à analyser : {progression_str}"
    )

    try:
        response_step_1 = model_instance.generate_content(prompt_step_1)
        prose_analysis = response_step_1.text.strip()
    except Exception as e:
        print(f"Erreur lors de l'étape 1 (Analyse) : {e}")
        raise

    # === ÉTAPE 2 : LE FORMATAGE JSON (Le "Formateur") ===

    prompt_step_2 = (
        "# Rôle et Objectif\n"
        "Tu es un expert en formatage de données. Ta mission est de convertir une analyse "
        "textuelle en un objet JSON strict, sans rien interpréter ni modifier.\n"
        "# Analyse Textuelle à Convertir\n"
        "```text\n"
        f"{prose_analysis}\n"
        "```\n"
        "# Instructions Strictes\n"
        "1.  **Format de Sortie :** Ta réponse doit **impérativement** être un objet JSON "
        "unique, sans aucun texte avant ou après.\n"
        "2.  **Transcription :** Transcris les informations de l'analyse textuelle dans la structure JSON.\n"
        "3. N'utilise que la notation **anglo-saxonne** pour les notes (C, C#, D, Eb, E, F, F#, G, Ab, A, Bb, B).\n"
        "# Structure JSON Détaillée\n"
        "```json\n"
        "{\n"
        '  "global_analysis": {\n'
        '    "tonic": "...",\n'
        '    "mode": "...",\n'
        '    "explanation": "..."\n'
        "  },\n"
        '  "harmonic_segments": [\n'
        "    {\n"
        '      "start_index": 0,\n'
        '      "end_index": 3,\n'
        '      "tonic": "A",\n'
        '      "mode": "Aeolian",\n'
        '      "explanation": "..."\n'
        "    },\n"
        "    {\n"
        '      "start_index": 4,\n'
        '      "end_index": 7,\n'
        '      "tonic": "D",\n'
        '      "mode": "Dorian",\n'
        '      "explanation": "..."\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "```\n\n"
        "**Contraintes sur les valeurs :**\n"
        "- Les indices `start_index` et `end_index` doivent être des entiers (base 0).\n"
        f"- Le `mode` doit **obligatoirement** appartenir à la liste suivante : {modes_list_str}.\n"
    )

    try:
        response_step_2 = model_instance.generate_content(prompt_step_2)
        raw_text = response_step_2.text.strip()

        json_string = extract_json_from_response(raw_text)
        analysis_data = json.loads(json_string)
        return analysis_data

    except Exception as e:
        print(f"Erreur lors de l'étape 2 (Formatage JSON) : {e}")
        # Tenter de renvoyer une erreur structurée
        return {
            "global_analysis": {
                "tonic": "Error",
                "mode": "Error",
                "explanation": f"Failed to parse analysis: {e}",
            },
            "harmonic_segments": [],
        }
