import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useMidiInput } from '@/composables/useMidiInput.js'
import { defaultProgression } from '@/constants.js'

export const useAnalysisStore = defineStore('analysis', () => {
  // --- STATE ---
  const lastAnalysis = ref({
    progression: null,
    result: null,
    model: null
  });
  
  const activeProgression = ref(
    lastAnalysis.value.progression && lastAnalysis.value.progression.length > 0
      ? JSON.parse(JSON.stringify(lastAnalysis.value.progression))
      : defaultProgression
  );
  
  const isMidiEnabled = ref(false);
  const liveMidiNotes = ref(new Set());
  const liveMidiNotesArray = computed(() => Array.from(liveMidiNotes.value));

  // --- ACTIONS ---
  
  const { enableMidi: enableMidiDevice, disableMidi: disableMidiDevice } = useMidiInput();

  function addChordToProgression(newChord) {
    console.log(newChord)
    activeProgression.value.push(newChord);
  }

  async function toggleMidi() {
    if (isMidiEnabled.value) {
      disableMidiDevice();
      isMidiEnabled.value = false;
      liveMidiNotes.value.clear();
    } else {
      const midiCallbacks = {
        onNoteOn: (note) => liveMidiNotes.value.add(note),
        onNoteOff: (note) => liveMidiNotes.value.delete(note),
        onChordDetected: addChordToProgression
      };
      enableMidiDevice(midiCallbacks);
      isMidiEnabled.value = true;
    }
  }

  function setLastAnalysis(data, progressionSnapshot) {
    lastAnalysis.value = {
      result: data,
      progression: progressionSnapshot,
      model: lastAnalysis.value.model
    };
  }

  function clearResult() {
    lastAnalysis.value.result = null;
  }
  
  function setModel(modelName) {
    lastAnalysis.value.model = modelName;
  }


  // On retourne les nouvelles propriétés pour qu'elles soient accessibles
  return {
    lastAnalysis,
    activeProgression, // Exposer la progression active
    isMidiEnabled,     // Exposer l'état MIDI
    liveMidiNotes: liveMidiNotesArray, // Exposer les notes MIDI en direct
    toggleMidi,        // Exposer l'action toggle
    setLastAnalysis,
    clearResult,
    setModel
  };
});