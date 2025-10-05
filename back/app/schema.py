from typing import List

from pydantic import BaseModel


class ChordItem(BaseModel):
    id: float | str  # Using float for compatibility with Date.now() in JS
    root: str
    quality: str
    inversion: int = 0
    duration: int = 2


class ProgressionRequest(BaseModel):
    chordsData: List[ChordItem]
    model: str
