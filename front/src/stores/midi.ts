import { defineStore } from "pinia";
import { ref } from "vue";
import { useMidiInput } from "@/composables/useMidiInput.ts";
import { useChordDetector } from "@/composables/useChordDetector.ts";

export const useMidiStore = defineStore("midi", () => {
  const { isEnabled, liveMidiNotes, enableMidi, disableMidi } = useMidiInput();
  const { detectedChord, handleNoteOn, handleNoteOff } = useChordDetector();

  const autoAddWithMidi = ref(true);

  async function toggleMidi() {
    if (isEnabled.value) {
      disableMidi();
    } else {
      await enableMidi({
        onNoteOn: handleNoteOn,
        onNoteOff: handleNoteOff,
      });
    }
  }

  return {
    isMidiEnabled: isEnabled,
    autoAddWithMidi,
    liveMidiNotes,
    toggleMidi,
    detectedChord,
  };
});
