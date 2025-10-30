from typing import List

from app.schema import ChordItem
from app.utils.chords_analyzer import QualityAnalysisItem


def fill_interface_data(
    quality_analysis: List[QualityAnalysisItem], progression_data: List[ChordItem]
) -> None:
    for i, analyzed_chord in enumerate(quality_analysis):
        analyzed_chord["id"] = progression_data[i].id
        analyzed_chord["inversion"] = progression_data[i].inversion
        analyzed_chord["duration"] = progression_data[i].duration
        if getattr(progression_data[i], "notes", None):
            analyzed_chord["notes"] = progression_data[i].notes
