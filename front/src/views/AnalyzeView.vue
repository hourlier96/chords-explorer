<template>
  <v-container fluid>
    <v-row>
      <v-col cols="6">
        <v-row>
          <v-col cols="12">
            <ChordProgressionBuilder
              v-model="progression"
              :is-loading="isLoading"
              :error="analysisError"
              v-model:ai-model="selectedAiModel"
              @analyze="analyzeProgression()"
              :editing-chord-id="editingChordId"
              :active-chord-object="currentlyEditingChord"
              @start-editing="(chord) => (editingChordId = chord.id)"
              @stop-editing="editingChordId = null"
              @update:chord="updateChord"
            />
          </v-col>

          <v-col cols="12">
            <v-card outlined>
              <v-card-text> Contenu de la deuxième ligne de la colonne gauche </v-card-text>
            </v-card>
          </v-col>
        </v-row>
      </v-col>

      <v-col cols="6">
        <ChordEditor v-model="currentlyEditingChord" @close="editingChordId = null" />
      </v-col>
    </v-row>
  </v-container>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue'
import { useAnalysisStore } from '@/stores/analysis.js'
import ChordProgressionBuilder from '@/components/progression/ChordProgressionBuilder.vue'
import ChordEditor from '@/components/progression/ChordEditor.vue'

const analysisStore = useAnalysisStore()

const defaultProgression = [
  {
    id: 1,
    root: 'C',
    quality: 'm',
    inversion: 2,
    duration: 2
  },
  {
    id: 2,
    root: 'F',
    quality: 'm',
    inversion: 0,
    duration: 2
  },
  {
    id: 3,
    root: 'D',
    quality: 'dim',
    inversion: 2,
    duration: 2
  },
  {
    id: 4,
    root: 'G',
    quality: 'aug',
    inversion: 0,
    duration: 1
  },
  {
    id: 5,
    root: 'G',
    quality: '',
    inversion: 1,
    duration: 1
  }
]

const progression = ref(
  analysisStore.lastAnalysis.progression && analysisStore.lastAnalysis.progression.length > 0
    ? JSON.parse(JSON.stringify(analysisStore.lastAnalysis.progression))
    : defaultProgression
)

const isLoading = ref(false)
const analysisError = ref(null)
const editingChordId = ref(null)

const selectedAiModel = ref('gemini-2.5-flash')

async function analyzeProgression() {
  isLoading.value = true
  analysisError.value = null
  analysisStore.clearResult()

  const chordsData = progression.value
  if (chordsData.length < 2) {
    analysisError.value = "Veuillez construire une progression d'au moins 2 accords."
    isLoading.value = false
    return
  }

  try {
    const response = await fetch('http://localhost:8000/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ chordsData, model: selectedAiModel.value })
    })
    if (!response.ok) throw new Error(`Erreur du serveur: ${response.statusText}`)
    const data = await response.json()
    if (data.error) throw new Error(data.error)

    const progressionSnapshot = JSON.parse(JSON.stringify(progression.value))
    analysisStore.setLastAnalysis(data, progressionSnapshot)
    analysisStore.setModel(selectedAiModel.value)
  } catch (e) {
    analysisError.value = `Une erreur est survenue : ${e.message}`
    analysisStore.clearResult()
  } finally {
    isLoading.value = false
  }
}

const currentlyEditingChord = computed({
  get() {
    if (!editingChordId.value) return null
    return progression.value.find((c) => c.id === editingChordId.value)
  },
  set(newValue) {
    if (!newValue || !editingChordId.value) return
    const index = progression.value.findIndex((c) => c.id === editingChordId.value)
    if (index !== -1) {
      progression.value[index] = newValue
    }
  }
})

function updateChord({ index, newChord }) {
  if (index >= 0 && index < progression.value.length) {
    progression.value[index] = newChord
  }
}
</script>

<style></style>
