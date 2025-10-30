// src/stores/tempo.js
import { defineStore } from "pinia";

export const useTempoStore = defineStore("tempo", {
  state: () => ({
    bpm: 85,
  }),

  getters: {
    beatDurationMs: (state) => 60000 / state.bpm,
  },

  actions: {
    setBpm(newBpm) {
      this.bpm = Math.max(40, Math.min(300, newBpm));
    },
  },
});
