from typing import List, Optional

from pydantic import BaseModel


class ChordItem(BaseModel):
    id: float | str  # Using float for compatibility with Date.now() in JS
    root: str
    quality: str
    inversion: int = 0
    duration: int = 2
    notes: Optional[List[str]] = None


class ProgressionRequest(BaseModel):
    chordsData: List[ChordItem]
    model: str
