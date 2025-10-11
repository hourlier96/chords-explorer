import { ref, onUnmounted } from 'vue'
import { WebMidi } from 'webmidi'
import * as Tone from 'tone'
import { piano } from '@/utils/sampler.js'

export function useMidiInput() {
  const isEnabled = ref(false)
  let activeInput = null

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
        piano.triggerAttack(e.note.identifier, Tone.now(), e.velocity)
        callbacks.onNoteOn?.(e.note)
      })

      activeInput.addListener('noteoff', (e) => {
        piano.triggerRelease(e.note.identifier, Tone.now())
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
