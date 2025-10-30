from typing import Any, Dict, List

from app.utils.chords_analyzer import QualityAnalysisItem, analyze_chord_in_context
from app.utils.common import get_note_index
from app.utils.mode_detection_gemini import detect_tonic_and_mode


def analyze_progression_segments(
    progression: List[str], harmonic_segments: List[Dict[str, Any]]
) -> List[QualityAnalysisItem]:
    """
    Analyse chaque accord de la progression en utilisant le contexte
    tonal de son segment harmonique assigné.
    """
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

    for i, analysis in enumerate(final_analysis):
        if not analysis:
            # Analyse avec le contexte du premier segment par défaut
            fallback_tonic_index = get_note_index(harmonic_segments[0]["tonic"])
            fallback_mode = harmonic_segments[0]["mode"]
            final_analysis[i] = analyze_chord_in_context(
                progression[i], fallback_tonic_index, fallback_mode
            )

    return final_analysis  # type: ignore


def get_analysis_data(
    progression: List[str], model: str
) -> tuple[Any, Any, list[QualityAnalysisItem]]:
    analysis_result = detect_tonic_and_mode(progression, model)  # type: ignore
    global_analysis = analysis_result["global_analysis"]
    harmonic_segments = analysis_result["harmonic_segments"]
    quality_analysis: List[QualityAnalysisItem] = analyze_progression_segments(
        progression, harmonic_segments
    )

    return global_analysis, harmonic_segments, quality_analysis
