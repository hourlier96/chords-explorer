<template>
  <v-container fluid>
    <v-row>
      <v-col cols="7">
        <v-row>
          <v-col cols="12" class="pl-0">
            <ChordProgressionBuilder
              v-model="progression"
              :is-loading="isLoading"
              :error="analysisError"
              v-model:ai-model="selectedAiModel"
              @analyze="analyzeProgression()"
              :editing-chord-id="editingChordId"
              :active-chord-object="currentlyEditingChord"
              @play-chord="(chord) => launchEdition(chord)"
              @start-editing="launchEdition($event)"
              @stop-editing="editingChordId = null"
            />
          </v-col>
        </v-row>
      </v-col>
      <v-col cols="5">
        <ChordEditor v-model="currentlyEditingChord" :disabled="lastChordPlayedFromAnalyze" />

        <PianoKeyboard
          v-if="currentlyEditingChord"
          :active-notes="selectedChordNotes"
          class="mt-1"
          @add-note="(note) => recalculateChord(note, currentlyEditingChord, false)"
          @remove-note="(note) => recalculateChord(note, currentlyEditingChord, true)"
          :disabled="lastChordPlayedFromAnalyze"
        />
        <div v-if="!lastChordPlayedFromAnalyze" class="text-center font-italic">
          {{ noMatch ? 'Aucune correspondance trouvée' : '' }}
          {{
            !noMatch && currentlyEditingChord && !currentlyEditingChord?.notes
              ? "Modifiez l'accord en cliquant sur les touches"
              : ''
          }}
        </div>
      </v-col>
    </v-row>
    <v-row v-if="analysisResults">
      <AnalysisGrid
        :title="`${analysisResults.tonic} ${analysisResults.mode}`"
        :progression-items="analysisResults.quality_analysis"
        :analysis="analysisStore.lastAnalysis"
        @play-chord="(chord) => launchEdition(chord, true)"
      />
    </v-row>
  </v-container>
</template>
<script lang="ts" setup>
import { ref, computed, watch, nextTick } from 'vue'
import { ENHARMONIC_EQUIVALENTS, CHORD_FORMULAS_NORMALIZED, NOTES_FLAT } from '@/constants'
import { useAnalysisStore } from '@/stores/analysis.js'
import { piano, getNotesForChord, noteToMidi } from '@/sampler.js'
import ChordProgressionBuilder from '@/components/progression/ChordProgressionBuilder.vue'
import PianoKeyboard from '@/components/common/PianoKeyboard.vue'
import ChordEditor from '@/components/progression/ChordEditor.vue'
import AnalysisGrid from '@/components/analysis/AnalysisGrid.vue'

const analysisStore = useAnalysisStore()

const defaultProgression = [
  {
    id: 1,
    root: 'A',
    quality: 'm7',
    inversion: 0,
    duration: 2,
    notes: ['A2', 'C4', 'E4', 'G4']
  },
  {
    id: 2,
    root: 'G',
    quality: '',
    inversion: 1,
    duration: 2,
    notes: ['B2', 'D4', 'G4']
  },
  {
    id: 3,
    root: 'C',
    quality: '',
    inversion: 0,
    duration: 2,
    notes: ['C3', 'G3', 'E4', 'G4']
  },
  {
    id: 4,
    root: 'F',
    quality: 'maj7',
    inversion: 0,
    duration: 2,
    notes: ['F2', 'A3', 'C4', 'E4']
  },
  {
    id: 5,
    root: 'D',
    quality: 'm7',
    inversion: 0,
    duration: 2,
    notes: ['D2', 'F3', 'A3', 'C4']
  },
  {
    id: 6,
    root: 'E',
    quality: 'sus4',
    inversion: 0,
    duration: 1,
    notes: ['E2', 'A3', 'B3']
  },
  {
    id: 7,
    root: 'E',
    quality: '7',
    inversion: 0,
    duration: 1,
    notes: ['G#2', 'G#3', 'B3', 'D4']
  },
  {
    id: 9,
    root: 'A',
    quality: '9',
    inversion: 0,
    duration: 2,
    notes: ['A2', 'G3', 'B3', 'C#4', 'E4']
  },
  {
    id: 10,
    root: 'D',
    quality: '7',
    inversion: 0,
    duration: 2,
    notes: ['D2', 'D4', 'F#4', 'A4', 'C4']
  },
  {
    id: 11,
    root: 'G',
    quality: '',
    inversion: 0,
    duration: 4,
    notes: ['G2', 'B3', 'D4', 'G4']
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

const selectedChordNotes = ref([])
const isRecalculating = ref(false)
const noMatch = ref(false)

const analysisResults = computed(() => analysisStore.lastAnalysis.result)

const lastChordPlayedFromAnalyze = ref(false)

function launchEdition(chord, fromAnalyze = false) {
  lastChordPlayedFromAnalyze.value = fromAnalyze
  editingChordId.value = chord.id
  selectedChordNotes.value = getNotesForChord(chord)
  noMatch.value = false
  piano.play(chord)
}

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

watch(
  () => currentlyEditingChord.value,
  (newActiveChord) => {
    // Avoid selecting chord when click on note
    if (isRecalculating.value) return

    if (newActiveChord) {
      selectedChordNotes.value = getNotesForChord(newActiveChord)
      noMatch.value = false
    }
  },
  { deep: true }
)

/**
 * @param {string} noteClicked - La dernière note ajoutée ou retirée.
 * @param {object} currentChord - L'objet représentant l'accord avant la modification.
 * @param {boolean} [remove=false] - Si vrai, la note est retirée au lieu d'être ajoutée.
 */
function recalculateChord(noteClicked, currentChord, remove = false) {
  if (!currentChord) return

  // 1. Mettre à jour et trier les notes par hauteur MIDI
  let allNotesWithOctave
  if (remove) {
    allNotesWithOctave = selectedChordNotes.value.filter((n) => n !== noteClicked)
  } else {
    allNotesWithOctave = [...new Set([...selectedChordNotes.value, noteClicked])]
  }
  selectedChordNotes.value = allNotesWithOctave.sort((a, b) => noteToMidi(a) - noteToMidi(b))

  isRecalculating.value = true

  // Gérer le cas où il n'y a plus de notes
  if (selectedChordNotes.value.length === 0) {
    currentlyEditingChord.value = { ...currentChord, quality: null, inversion: 0, notes: [] }
    nextTick(() => {
      isRecalculating.value = false
    })
    return
  }

  const allUniqueNoteNames = [...new Set(allNotesWithOctave.map((note) => note.slice(0, -1)))]
  let foundMatchData = null

  // 3. Itérer pour trouver une correspondance
  for (const potentialRootName of allUniqueNoteNames) {
    const normalizedRoot = ENHARMONIC_EQUIVALENTS[potentialRootName] || potentialRootName
    const rootIndex = NOTES_FLAT.indexOf(normalizedRoot)
    if (rootIndex === -1) continue

    const intervals = allUniqueNoteNames
      .map((noteName) => {
        const normalizedNote = ENHARMONIC_EQUIVALENTS[noteName] || noteName
        const noteIndex = NOTES_FLAT.indexOf(normalizedNote)
        return (noteIndex - rootIndex + 12) % 12
      })
      .sort((a, b) => a - b)

    const sorted_formulas = Object.entries(CHORD_FORMULAS_NORMALIZED).sort(
      ([, formulaA], [, formulaB]) => formulaB.length - formulaA.length
    )
    for (const [quality, formula] of sorted_formulas) {
      const sortedFormula = [...formula].sort((a, b) => a - b)
      const isMatch =
        intervals.length === sortedFormula.length &&
        intervals.every((val, index) => val === sortedFormula[index])

      if (isMatch) {
        const lowestNoteName = allNotesWithOctave[0].slice(0, -1)
        const normalizedLowestNote = ENHARMONIC_EQUIVALENTS[lowestNoteName] || lowestNoteName
        const lowestNoteIndex = NOTES_FLAT.indexOf(normalizedLowestNote)
        const bassNoteInterval = (lowestNoteIndex - rootIndex + 12) % 12
        const inversionIndex = formula.findIndex((interval) => interval === bassNoteInterval)

        foundMatchData = {
          root: potentialRootName,
          quality: quality,
          inversion: inversionIndex !== -1 ? inversionIndex : 0
        }
        break
      }
    }
    if (foundMatchData) break
  }

  if (foundMatchData) {
    noMatch.value = false
    currentlyEditingChord.value = {
      ...currentChord,
      ...foundMatchData,
      notes: selectedChordNotes.value
    }
  } else {
    noMatch.value = true
    currentlyEditingChord.value = {
      ...currentChord,
      root: '?',
      quality: '?',
      inversion: 0,
      notes: selectedChordNotes.value
    }
  }

  nextTick(() => {
    isRecalculating.value = false
  })
}
</script>

<style></style>
