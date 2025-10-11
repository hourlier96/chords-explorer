import { defineStore } from 'pinia'
import { useMidiInput } from '@/composables/useMidiInput.ts'
import { useChordDetector } from '@/composables/useChordDetector.ts'

export const useMidiStore = defineStore('midi', () => {
  // 1. Instantiate composables
  const { isEnabled, enableMidi, disableMidi } = useMidiInput()
  const { detectedChord, handleNoteOn, handleNoteOff } = useChordDetector()

  // 3. The action to toggle MIDI remains the same
  async function toggleMidi() {
    if (isEnabled.value) {
      disableMidi()
    } else {
      await enableMidi({
        onNoteOn: handleNoteOn,
        onNoteOff: handleNoteOff
      })
    }
  }

  // 4. Expose the detected chord directly
  return {
    isMidiEnabled: isEnabled,
    toggleMidi,
    detectedChord
  }
})