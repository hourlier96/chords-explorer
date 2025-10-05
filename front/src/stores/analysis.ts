import { defineStore } from 'pinia'

export const useAnalysisStore = defineStore('analysis', {
  state: () => ({
    lastAnalysis: {
      result: null,
      progression: null,
      model: null
    }
  }),

  getters: {
    hasResult: (state) => state.lastAnalysis.result !== null
  },

  actions: {
    setLastAnalysis(newResult, progressionSnapshot) {
      const enrichedResult = newResult.quality_analysis.map((analysisItem, index) => ({
        ...analysisItem,
        inversion: progressionSnapshot[index].inversion || 0
      }))

      this.lastAnalysis.result = {
        ...newResult,
        quality_analysis: enrichedResult
      }
      this.lastAnalysis.progression = progressionSnapshot
    },

    setModel(newModel) {
      this.lastAnalysis.model = newModel
    },

    clearResult() {
      this.lastAnalysis.result = null
      this.lastAnalysis.progression = null
    }
  },

  persist: true
})
