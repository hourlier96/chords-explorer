import api from '@/helpers/axios-wrapper.ts'

export default {
  async analyzeProgression(params) {
    return await api.get(`/analyze`, params)
  },
  // Used by unit tests, uses Public API
  unitTest() {
    return api.get('/', {})
  }
}
