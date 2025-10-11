import { ref, onUnmounted } from 'vue'
import { WebMidi } from 'webmidi'
import * as Tone from 'tone'
import { piano } from '@/utils/sampler.js'

export function useMidiInput() {
  const isEnabled = ref(false)
  let activeInput = null

  let isSustainPedalDown = false
  const sustainedNotes = new Set()

  // On passe des callbacks pour que le composant "parent" décide quoi faire
  async function enableMidi(callbacks = {}) {
    if (isEnabled.value) return
    try {
      await WebMidi.enable()
      console.log('WebMidi enabled!')

      if (WebMidi.inputs.length < 1) {
        console.error("Aucun appareil d'entrée MIDI trouvé.")
        return
      }

      activeInput = WebMidi.inputs[0]
      console.log(`Écoute sur : ${activeInput.name}`)
      
      
      // On déclenche les callbacks fournis, en jouant aussi le son
      activeInput.addListener('noteon', (e) => {
        sustainedNotes.delete(e.note.identifier)
        piano.triggerAttack(e.note.identifier, Tone.now(), e.velocity)
        callbacks.onNoteOn?.(e.note)
      })

      activeInput.addListener('controlchange', (e) => {
        if (e.controller.number === 64) {
          if (e.value >= 0.5) { // webmidi.js normalizes value to 0-1
            isSustainPedalDown = true
          } else {
            // Pedal is released
            isSustainPedalDown = false
            if (sustainedNotes.size > 0) {
              piano.triggerRelease(Array.from(sustainedNotes), Tone.now())
              sustainedNotes.clear()
            }
          }
        }
      })

      activeInput.addListener('noteoff', (e) => {
        if (isSustainPedalDown) {
          sustainedNotes.add(e.note.identifier)
        } else {
          piano.triggerRelease(e.note.identifier, Tone.now())
        }
        callbacks.onNoteOff?.(e.note)
      })

      isEnabled.value = true
    } catch (err) {
      console.error('Could not enable WebMidi.', err)
    }
  }

  function disableMidi() {
    if (!isEnabled.value || !activeInput) return
    activeInput.removeListener() // Enlève tous les listeners d'un coup
    WebMidi.disable()
    activeInput = null
    isEnabled.value = false
    piano.releaseAll()
    console.log('WebMidi disabled.')
  }

  onUnmounted(disableMidi)

  return { isEnabled, enableMidi, disableMidi }
}
