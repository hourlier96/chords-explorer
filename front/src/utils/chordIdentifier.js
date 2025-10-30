import {
  CHORD_FORMULAS_NORMALIZED,
  NOTES_FLAT,
  ENHARMONIC_EQUIVALENTS,
} from "@/constants";

/**
 * Identifie un accord à partir d'une liste de noms de notes.
 * @param {string[]} noteNames - Noms des notes sans l'octave (ex: ['C', 'E', 'G']).
 * @param {string[]} fullNoteIdentifiers - Identifiants complets des notes (ex: ['C4', 'E4', 'G4']).
 * @returns {object|null} L'objet accord ou null si non trouvé.
 */
export function identifyChordFromNotes(noteNames, fullNoteIdentifiers) {
  if (noteNames.length === 0) return null;

  for (const potentialRoot of noteNames) {
    const normalizedRoot =
      ENHARMONIC_EQUIVALENTS[potentialRoot] || potentialRoot;
    const rootIndex = NOTES_FLAT.indexOf(normalizedRoot);
    if (rootIndex === -1) continue;

    const intervals = noteNames
      .map((note) => {
        const normalizedNote = ENHARMONIC_EQUIVALENTS[note] || note;
        const noteIndex = NOTES_FLAT.indexOf(normalizedNote);
        return (noteIndex - rootIndex + 12) % 12;
      })
      .sort((a, b) => a - b);

    const uniqueIntervals = [...new Set(intervals)];

    const sortedFormulas = Object.entries(CHORD_FORMULAS_NORMALIZED).sort(
      ([, formulaA], [, formulaB]) => formulaB.length - formulaA.length,
    );

    for (const [quality, formula] of sortedFormulas) {
      const sortedFormula = [...formula].sort((a, b) => a - b);
      const isMatch =
        uniqueIntervals.length === sortedFormula.length &&
        uniqueIntervals.every((val, index) => val === sortedFormula[index]);
      if (isMatch) {
        return {
          id: Date.now(),
          root: potentialRoot,
          quality: quality,
          inversion: 0, // À calculer si besoin
          duration: 2,
          notes: fullNoteIdentifiers,
        };
      }
    }
  }
  return null; // Aucun accord trouvé
}
