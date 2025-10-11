import { defineStore } from 'pinia'
import { watch } from 'vue'
import { useMidiInput } from '@/composables/useMidiInput.ts'
import { useChordDetector } from '@/composables/useChordDetector.ts'
import { useAnalysisStore } from './analysis.ts' // Assurez-vous que le chemin est correct

export const useMidiStore = defineStore('midi', () => {
  // 1. On instancie les stores et composables dont on a besoin
  const analysisStore = useAnalysisStore()
  const { isEnabled, enableMidi, disableMidi } = useMidiInput()
  const { detectedChord, handleNoteOn, handleNoteOff } = useChordDetector()

  // 2. Le "cerveau" : on surveille les accords détectés
  // Cette logique est maintenant centralisée ici et tourne en permanence
  watch(detectedChord, (newChord) => {
    if (newChord && analysisStore.autoAddWithMidi) {
      analysisStore.addChordToProgression(newChord)
    }
  })

  // 3. L'action que la Navbar va appeler
  async function toggleMidi() {
    if (isEnabled.value) {
      disableMidi()
    } else {
      // On connecte les "câbles" au moment de l'activation
      await enableMidi({
        onNoteOn: handleNoteOn,
        onNoteOff: handleNoteOff
      })
    }
  }

  // 4. On expose uniquement ce dont les composants ont besoin
  return {
    isMidiEnabled: isEnabled,
    toggleMidi
  }
})
