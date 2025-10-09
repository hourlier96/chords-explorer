// src/composables/useMidiInput.js
import { ref, onUnmounted } from 'vue'
import { WebMidi } from 'webmidi'
import * as Tone from 'tone'
import { piano } from '@/sampler.js'
import { CHORD_FORMULAS_NORMALIZED, NOTES_FLAT, ENHARMONIC_EQUIVALENTS } from '@/constants'

export function useMidiInput() {
  const isEnabled = ref(false)
  const activeInput = ref(null)
  const pressedNotes = new Set()
  let chordDetectionTimeout = null

  function identifyChordFromNotes(noteNames, fullNoteIdentifiers) {
    if (noteNames.length === 0) return null

    for (const potentialRoot of noteNames) {
      const normalizedRoot = ENHARMONIC_EQUIVALENTS[potentialRoot] || potentialRoot
      const rootIndex = NOTES_FLAT.indexOf(normalizedRoot)
      if (rootIndex === -1) continue

      const intervals = noteNames
        .map((note) => {
          const normalizedNote = ENHARMONIC_EQUIVALENTS[note] || note
          const noteIndex = NOTES_FLAT.indexOf(normalizedNote)
          return (noteIndex - rootIndex + 12) % 12
        })
        .sort((a, b) => a - b)

      const uniqueIntervals = [...new Set(intervals)]

      const sortedFormulas = Object.entries(CHORD_FORMULAS_NORMALIZED).sort(
        ([, formulaA], [, formulaB]) => formulaB.length - formulaA.length
      )

      for (const [quality, formula] of sortedFormulas) {
        const sortedFormula = [...formula].sort((a, b) => a - b)
        const isMatch =
          uniqueIntervals.length === sortedFormula.length &&
          uniqueIntervals.every((val, index) => val === sortedFormula[index])
        if (isMatch) {
          return {
            id: Date.now(),
            root: potentialRoot,
            quality: quality,
            inversion: 0, // We can calculate this, but 0 is fine for now
            duration: 2, // Default duration
            notes: fullNoteIdentifiers
          }
        }
      }
    }
    return null // No match found
  }

  function handleNoteOn(e, callbacks) {
    piano.triggerAttack(e.note.identifier, Tone.now(), e.velocity)
    callbacks?.onNoteOn?.(e.note.identifier)
    if (chordDetectionTimeout) clearTimeout(chordDetectionTimeout)
    pressedNotes.add(e.note.identifier)
    lastPlayedChordNotes = new Set(pressedNotes)
  }

  let lastPlayedChordNotes = new Set()

  function handleNoteOff(e, callbacks) {
    piano.triggerRelease(e.note.identifier, Tone.now())
    callbacks?.onNoteOff?.(e.note.identifier)

    pressedNotes.delete(e.note.identifier)
    if (pressedNotes.size > 0) return
    if (chordDetectionTimeout) clearTimeout(chordDetectionTimeout)

    chordDetectionTimeout = setTimeout(() => {
      if (lastPlayedChordNotes.size >= 2) {
        const uniqueNoteNames = [
          ...new Set(Array.from(lastPlayedChordNotes).map((identifier) => identifier.slice(0, -1)))
        ]
        const playedNotesArray = Array.from(lastPlayedChordNotes)
        const detectedChordData = identifyChordFromNotes(uniqueNoteNames, playedNotesArray)
        if (detectedChordData) {
          const finalChordObject = {
            ...detectedChordData
          }
          callbacks.onChordDetected(finalChordObject)
        }
      }
      lastPlayedChordNotes.clear()
    }, 50)
  }

  async function enableMidi(callbacks) {
    if (isEnabled.value) return
    try {
      await WebMidi.enable()
      console.log('WebMidi enabled!')

      if (WebMidi.inputs.length < 1) {
        console.error("Aucun appareil d'entrée MIDI trouvé.")
        return
      }

      // Use the first available MIDI input device
      const midiInput = WebMidi.inputs[0]
      console.log(`Écoute sur : ${midiInput.name}`) // Vérifiez que c'est bien votre clavier
      activeInput.value = midiInput

      // Add listeners
      midiInput.addListener('noteon', (e) => handleNoteOn(e, callbacks))
      midiInput.addListener('noteoff', (e) => handleNoteOff(e, callbacks))

      isEnabled.value = true
    } catch (err) {
      console.error('Could not enable WebMidi.', err)
    }
  }

  function disableMidi() {
    if (!isEnabled.value || !activeInput.value) return

    activeInput.value.removeListener('noteon')
    activeInput.value.removeListener('noteoff')
    WebMidi.disable()

    activeInput.value = null
    isEnabled.value = false
    piano.releaseAll()
    console.log('WebMidi disabled.')
  }

  onUnmounted(() => {
    disableMidi()
  })

  return { isEnabled, enableMidi, disableMidi }
}
