from typing import Any, Dict, List, Tuple

import uvicorn
from back.app.chords_calculator.modal_substitution import get_substitution_info, get_substitutions
from back.app.chords_calculator.secondary_dominant import get_secondary_dominant_for_target
from back.app.chords_calculator.tritone_substitution import get_tritone_substitute
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.schema import ChordItem, ProgressionRequest
from app.services.analysis import get_analysis_data
from app.services.data_filler import fill_interface_data
from app.utils.borrowed_modes import get_borrowed_chords
from app.utils.chords_analyzer import QualityAnalysisItem, analyze_chord_in_context
from app.utils.common import get_note_from_index, get_note_index
from constants import MAJOR_MODES_DATA, MODES_DATA

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/analyze")
def get_all_substitutions(request: ProgressionRequest):
    progression_data: List[ChordItem] = request.chords_data
    model: str = request.model
    if not progression_data:
        return {"error": "Progression cannot be empty"}

    progression = [f"{item.root}{item.quality}" for item in progression_data]
    try:
        # 1. Analyse IA et scan des segments harmoniques
        global_analysis, harmonic_segments, quality_analysis = get_analysis_data(progression, model)

        # 2. Ajout des propriétés originales aux résultats d'analyse
        fill_interface_data(quality_analysis, progression_data)

        # 3. Calcul des accords empruntés pour les accords non diatoniques
        borrowed_chords = get_borrowed_chords(quality_analysis)

        global_tonic = global_analysis["tonic"]
        detected_tonic_index: int = get_note_index(global_tonic)

        degrees_to_borrow: List[Dict[str, Any] | None] = get_substitution_info(quality_analysis)

        substitutions: Dict[str, Dict[str, Any]] = {}
        for mode_name, (_, _, interval) in MAJOR_MODES_DATA.items():
            relative_tonic_index = (detected_tonic_index + interval + 12) % 12
            new_progression = get_substitutions(
                progression, relative_tonic_index, degrees_to_borrow
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
                    segment_progression, segment_tonic_index, segment_sub_info, target_mode_name
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
                    item["chord"], context_tonic_index, target_mode_name
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
            "explanations": global_analysis["explanation"],
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
