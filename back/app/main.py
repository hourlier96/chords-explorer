from typing import Any, Dict, List, Tuple

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modal_substitution.generator import get_substitution_info, get_substitutions
from app.schema import ChordItem, ProgressionRequest
from app.secondary_dominant.generator import get_secondary_dominant_for_target
from app.tritone_substitution.generator import get_tritone_substitute
from app.utils.borrowed_modes import get_borrowed_chords
from app.utils.chords_analyzer import QualityAnalysisItem, analyze_chord_in_context
from app.utils.common import get_note_from_index, get_note_index
from app.utils.mode_detection_gemini import detect_tonic_and_mode
from constants import MAJOR_MODES_DATA, MODES_DATA

load_dotenv()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def analyze_progression_segments(
    progression: List[str], harmonic_segments: List[Dict[str, Any]]
) -> List[QualityAnalysisItem]:
    """
    Analyse chaque accord de la progression en utilisant le contexte
    tonal de son segment harmonique assigné.
    """
    # FIX: Use a generic `list` for the local variable to resolve the __setitem__ error.
    # mypy can be strict about assigning a specific TypedDict item to a list
    # annotated as List[Dict[str, Any]]. A generic list avoids this problem internally.
    final_analysis: list = [{} for _ in progression]

    for segment in harmonic_segments:
        segment_tonic_index = get_note_index(segment["tonic"])
        segment_mode = segment["mode"]

        # Applique l'analyse pour chaque accord dans la plage du segment
        for i in range(segment["start_index"], segment["end_index"] + 1):
            if i < len(progression):
                analyzed_chord = analyze_chord_in_context(
                    progression[i], segment_tonic_index, segment_mode
                )
                # Ajoute le contexte du segment pour référence future
                analyzed_chord["segment_context"] = {
                    "tonic": segment["tonic"],
                    "mode": segment["mode"],
                    "explanation": segment["explanation"],
                }
                final_analysis[i] = analyzed_chord

    # S'assure qu'il n'y a pas de trou si l'IA a manqué un accord
    # (ceci est une sécurité)
    for i, analysis in enumerate(final_analysis):
        if not analysis:
            # Analyse avec le contexte du premier segment par défaut
            fallback_tonic_index = get_note_index(harmonic_segments[0]["tonic"])
            fallback_mode = harmonic_segments[0]["mode"]
            final_analysis[i] = analyze_chord_in_context(
                progression[i], fallback_tonic_index, fallback_mode
            )

    # The function's return signature guarantees the final type.
    return final_analysis  # type: ignore


@app.post("/analyze")
def get_all_substitutions(request: ProgressionRequest):
    progression_data: List[ChordItem] = request.chordsData
    model: str = request.model
    if not progression_data:
        return {"error": "Progression cannot be empty"}

    progression = [f"{item.root}{item.quality}" for item in progression_data]
    try:
        # analysis_result = detect_tonic_and_mode(progression, model)  # type: ignore
        analysis_result = {
            "global_analysis": {
                "tonic": "C",
                "mode": "Harmonic Minor",
                "explanation": "La progression est fermement ancrée dans la tonalité de Do mineur. L'utilisation du Gaug (V+) et du G (V) majeurs indique l'emploi de la gamme de Do mineur harmonique, caractérisée par sa septième degré haussé (Si naturel) qui crée une dominante majeure.",
            },
            "harmonic_segments": [
                {
                    "start_index": 0,
                    "end_index": 0,
                    "tonic": "C",
                    "mode": "Harmonic Minor",
                    "explanation": "L'accord tonique (i) de Do mineur harmonique, établissant le centre tonal.",
                },
                {
                    "start_index": 1,
                    "end_index": 1,
                    "tonic": "C",
                    "mode": "Harmonic Minor",
                    "explanation": "L'accord de sous-dominante (iv) de Do mineur harmonique.",
                },
                {
                    "start_index": 2,
                    "end_index": 2,
                    "tonic": "C",
                    "mode": "Harmonic Minor",
                    "explanation": "L'accord de supertonique diminuée (ii°) de Do mineur harmonique, fonctionnant comme une pré-dominante.",
                },
                {
                    "start_index": 3,
                    "end_index": 3,
                    "tonic": "C",
                    "mode": "Harmonic Minor",
                    "explanation": "L'accord de dominante augmentée (V+) de Do mineur harmonique. Le Sol augmenté (G-B-D#) est une variante du V, amplifiant la tension vers la tonique.",
                },
                {
                    "start_index": 4,
                    "end_index": 4,
                    "tonic": "C",
                    "mode": "Harmonic Minor",
                    "explanation": "L'accord de dominante (V) de Do mineur harmonique. Après le V+, cet accord maintient la tension dominante, la quinte (D#) se résolvant chromatiquement vers Ré (D), préparant la résolution attendue vers l'accord de Do mineur.",
                },
            ],
        }

        global_analysis = analysis_result["global_analysis"]
        harmonic_segments = analysis_result["harmonic_segments"]

        global_tonic = global_analysis["tonic"]
        global_mode = global_analysis["mode"]
        global_explanation = global_analysis["explanation"]

        # 2. Analyser la progression en utilisant les segments
        quality_analysis: List[QualityAnalysisItem] = analyze_progression_segments(
            progression, harmonic_segments
        )

        # Ajout des propriétés originales aux résultats d'analyse
        for i, analyzed_chord in enumerate(quality_analysis):
            analyzed_chord["inversion"] = progression_data[i].inversion
            analyzed_chord["duration"] = progression_data[i].duration

        detected_tonic_index: int = get_note_index(global_tonic)

        borrowed_chords = get_borrowed_chords(quality_analysis, global_mode)
        degrees_to_borrow: List[Dict[str, Any] | None] = get_substitution_info(quality_analysis)

        substitutions: Dict[str, Dict[str, Any]] = {}
        for mode_name, (_, _, interval) in MAJOR_MODES_DATA.items():
            relative_tonic_index = (detected_tonic_index + interval + 12) % 12
            new_progression = get_substitutions(
                progression,
                relative_tonic_index,
                degrees_to_borrow,
            )
            for index, item in enumerate(new_progression):
                chord_data = progression_data[index]
                item["inversion"] = chord_data.inversion
                item["duration"] = chord_data.duration
            substitutions[mode_name] = {
                "borrowed_scale": f"{get_note_from_index(relative_tonic_index)} Major",
                "substitution": new_progression,
            }

        # Harmonize all existing modes
        harmonized_chords: Dict[str, List[QualityAnalysisItem]] = {}
        for target_mode_name in MODES_DATA.keys():
            new_progression_items = []

            # 1. SUBSTITUTION SEGMENT PAR SEGMENT
            for segment in harmonic_segments:
                segment_start = segment["start_index"]
                segment_end = segment["end_index"]

                segment_tonic_index = get_note_index(segment["tonic"])
                segment_progression = progression[segment_start : segment_end + 1]
                segment_sub_info = degrees_to_borrow[segment_start : segment_end + 1]

                substituted_segment = get_substitutions(
                    segment_progression,
                    segment_tonic_index,
                    segment_sub_info,
                    target_mode_name,
                )
                new_progression_items.extend(substituted_segment)

            # 2. ANALYSE DE LA NOUVELLE PROGRESSION
            final_analyzed_chords = []
            for i, item in enumerate(new_progression_items):
                current_segment = next(
                    s for s in harmonic_segments if s["start_index"] <= i <= s["end_index"]
                )
                context_tonic_index = get_note_index(current_segment["tonic"])

                analyzed_chord = analyze_chord_in_context(
                    item["chord"],
                    context_tonic_index,
                    target_mode_name,
                )
                final_analyzed_chords.append(analyzed_chord)

            harmonized_chords[target_mode_name] = final_analyzed_chords

        # Get all secondary dominants for all major modes
        secondary_dominants: Dict[str, List[Tuple[str, str, Dict[str, Any]]]] = {}
        for mode_name, substitutions_data in substitutions.items():
            secondary_dominants[mode_name] = []
            for item in substitutions_data["substitution"]:
                secondary_dominant, analysis = get_secondary_dominant_for_target(
                    item["chord"], global_tonic, mode_name
                )
                secondary_dominants[mode_name].append((secondary_dominant, item["chord"], analysis))

        tritone_substitutions: List[List[Any]] = []
        for chord in progression:
            substitute, analysis = get_tritone_substitute(chord)
            tritone_substitutions.append([chord, substitute, analysis])

        return {
            "tonic": global_tonic,
            "mode": global_mode,
            "explanations": global_explanation,
            "quality_analysis": quality_analysis,
            "borrowed_chords": borrowed_chords,
            "major_modes_substitutions": substitutions,
            "harmonized_chords": harmonized_chords,
            "secondary_dominants": secondary_dominants,
            "tritone_substitutions": tritone_substitutions,
        }
    except Exception as e:
        raise e


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
