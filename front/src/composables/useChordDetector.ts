import { ref } from 'vue'
import { identifyChordFromNotes } from '@/utils/chordIdentifier.js'

export function useChordDetector() {
  const detectedChord = ref(null)

  // On utilise une Map pour stocker l'objet note entier (pour le tri)
  // La clé est l'identifiant (ex: 'E4'), la valeur est l'objet note complet.
  const pressedNotes = new Map()
  let lastPlayedChordNotes = new Map()
  let chordDetectionTimeout = null

  function handleNoteOn(note) {
    if (chordDetectionTimeout) clearTimeout(chordDetectionTimeout)
    
    // On stocke l'objet note entier, avec son numéro MIDI pour le tri futur
    pressedNotes.set(note.identifier, note) 
    
    // On garde une copie de la Map des notes jouées
    lastPlayedChordNotes = new Map(pressedNotes)
  }

  function handleNoteOff(note) {
    pressedNotes.delete(note.identifier)

    if (pressedNotes.size === 0) {
      chordDetectionTimeout = setTimeout(() => {
        if (lastPlayedChordNotes.size >= 2) {
          
          const notesAsObjects = Array.from(lastPlayedChordNotes.values())
          notesAsObjects.sort((a, b) => a.number - b.number)
          const playedNotesArray = notesAsObjects.map(n => n.identifier)
          const uniqueNoteNames = [...new Set(playedNotesArray.map((id) => id.slice(0, -1)))]
          const chordData = identifyChordFromNotes(uniqueNoteNames, playedNotesArray)
          
          if (chordData) {
            detectedChord.value = chordData
          }
        }
        lastPlayedChordNotes.clear()
      }, 50)
    }
  }

  return {
    detectedChord,
    handleNoteOn,
    handleNoteOff
  }
}