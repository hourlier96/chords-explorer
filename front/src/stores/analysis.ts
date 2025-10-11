import { ref } from 'vue'
import { defineStore } from 'pinia'
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
  
  const autoAddWithMidi = ref(true);

  // --- ACTIONS ---
  function addChordToProgression(newChord) {
    activeProgression.value.push(newChord);
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

  return {
    lastAnalysis,
    activeProgression,
    autoAddWithMidi,
    addChordToProgression, // L'action principale
    setLastAnalysis,
    clearResult,
    setModel
  };
}, {
  persist: true,
});