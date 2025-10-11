<template>
  <div class="builder-container">
    <ProgressionTimeline
      ref="gridContainerRef"
      :items="progression"
      :play-callback="playChordItem"
      draggable
      @drag-end="onDragEnd"
      @item-click="handleChordClick"
      @grid-click="selectedChordIds.clear()"
    >
      <template #item="{ item: chord, index }">
        <ChordCard
          :class="{ 'is-selected': selectedChordIds.has(chord.id) }"
          :modelValue="chord"
          :beat-width="BEAT_WIDTH"
          @update:modelValue="(newChord) => updateChord(index, newChord)"
          :is-editing="editingChordId === chord.id"
          :piano="piano"
          @remove="removeChord(chord.id)"
          @start-editing="startEditing(chord)"
          @stop-editing="stopEditing"
        />
      </template>

      <template #footer>
        <div class="footer-controls">
          <v-tooltip
            v-if="!showQuickImport && isMidiEnabled"
            location="top"
            text="Ajout automatique"
          >
            <template #activator="{ props }">
              <button
                v-bind="props"
                class="add-button"
                :style="{ backgroundColor: autoAddWithMidi ? 'lightgreen' : '' }"
                @click="autoAddWithMidi = !autoAddWithMidi"
              >
                <v-icon> mdi-piano </v-icon>
              </button>
            </template>
          </v-tooltip>

          <button v-if="!showQuickImport" class="add-button" @click="addChord()">+</button>
          <v-tooltip v-if="!showQuickImport" location="top" text="Import textuel">
            <template #activator="{ props }">
              <button v-bind="props" class="add-button" @click="showQuickImport = true">
                <v-icon icon="mdi-keyboard" />
              </button>
            </template>
          </v-tooltip>
          <div v-if="showQuickImport">
            <input
              type="text"
              v-model="quickImportText"
              placeholder="Ex: Cmaj7 G7"
              class="quick-import-input"
              @keyup.enter="processQuickImport"
            />
            <div class="quick-import-buttons">
              <button @click="processQuickImport" class="quick-import-button">
                <v-icon icon="mdi-check" />
              </button>
              <button @click="cancelQuickImport" class="quick-import-button cancel">
                <v-icon icon="mdi-close" />
              </button>
            </div>
          </div>
          <v-tooltip v-if="!showQuickImport" location="top" text="Reset la progression">
            <template #activator="{ props }">
              <button v-bind="props" @click="removeAllChords" class="add-button">
                <v-icon icon="mdi-close" />
              </button>
            </template>
          </v-tooltip>
        </div>
      </template>
    </ProgressionTimeline>

    <div class="analyze-section-container">
      <div class="model-selector">
        <label :class="{ active: aiModel === 'gemini-2.5-flash' }" class="radio-label">
          <input
            type="radio"
            name="ai-model"
            value="gemini-2.5-flash"
            :checked="aiModel === 'gemini-2.5-flash'"
            @change="$emit('update:aiModel', 'gemini-2.5-flash')"
          />
          Modèle Rapide
        </label>

        <button
          class="analyze-icon-button"
          @click="onAnalyze"
          :disabled="isLoading || progression.length === 0 || isProgressionUnchanged"
          aria-label="Analyser la progression"
        >
          <template v-if="isLoading">
            <v-progress-circular indeterminate color="white" size="20" width="2" />
          </template>
          <template v-else>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8"></circle>
              <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
            </svg>
          </template>
        </button>

        <label :class="{ active: aiModel === 'gemini-2.5-pro' }" class="radio-label">
          <input
            type="radio"
            name="ai-model"
            value="gemini-2.5-pro"
            :checked="aiModel === 'gemini-2.5-pro'"
            @change="$emit('update:aiModel', 'gemini-2.5-pro')"
          />
          Modèle Précis
        </label>
      </div>
    </div>
    <div v-if="error" class="error-message">{{ error }}</div>
  </div>
</template>

<script setup>
import { storeToRefs } from 'pinia'
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'

import { BEAT_WIDTH } from '@/composables/useStatePlayer.ts'
import { piano, getNotesAsMidi } from '@/utils/sampler.js'
import { sleep } from '@/utils/time.js'
import { useStores } from '@/composables/useStores.ts'

import ProgressionTimeline from '@/components/common/ProgressionTimeline.vue'
import ChordCard from '@/components/progression/ChordCard.vue'

const { analysis: analysisStore, tempo: tempoStore, midi: midiStore } = useStores()
const { autoAddWithMidi } = storeToRefs(analysisStore)
const { isMidiEnabled } = storeToRefs(midiStore)

const props = defineProps({
  modelValue: { type: Array, required: true },
  isLoading: { type: Boolean, default: false },
  error: { type: String, default: '' },
  aiModel: { type: String, required: true },
  editingChordId: { type: [Number, null], default: null }
})
const emit = defineEmits([
  'update:modelValue',
  'analyze',
  'update:aiModel',
  'start-editing',
  'play-chord'
])

const editingChordId = ref(null)
const showQuickImport = ref(false)
const quickImportText = ref('')

const gridContainerRef = ref(null)

const selectedChordIds = ref(new Set())
const clipboard = ref([])
const undoStack = ref([])

const playChordItem = async ({ item }) => {
  if (!item) return
  const chordDurationMs = item.duration * tempoStore.beatDurationMs
  emit('play-chord', item)
  piano.play(item)
  await sleep(chordDurationMs)
}

const progression = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit('update:modelValue', newValue)
  }
})

const isProgressionUnchanged = computed(() => {
  if (!analysisStore.lastAnalysis.progression || !analysisStore.hasResult) return false
  return (
    JSON.stringify(progression.value) === JSON.stringify(analysisStore.lastAnalysis.progression) &&
    props.aiModel === analysisStore.lastAnalysis.model
  )
})

function onDragEnd(event) {
  const { oldIndex, newIndex } = event
  const newProgression = [...progression.value]
  const [movedItem] = newProgression.splice(oldIndex, 1)
  newProgression.splice(newIndex, 0, movedItem)
  progression.value = newProgression
}

function addChord() {
  const newChord = {
    id: Date.now(),
    root: 'C',
    quality: '',
    inversion: 2,
    duration: 2
  }
  progression.value = [...progression.value, newChord]
  // Place scroll at the end to show the new chord
  nextTick(() => {
    if (gridContainerRef.value && gridContainerRef.value.gridContainerRef) {
      const scrollableDiv = gridContainerRef.value.gridContainerRef
      scrollableDiv.scrollLeft = scrollableDiv.scrollWidth
    }
  })
}

function removeChord(chordId) {
  progression.value = progression.value.filter((c) => c.id !== chordId)
  selectedChordIds.value.delete(chordId)
  if (editingChordId.value === chordId) {
    stopEditing()
  }
}

function updateChord(index, newChord) {
  const newProgression = [...progression.value]
  newProgression[index] = newChord
  progression.value = newProgression
}

function startEditing(chord) {
  emit('start-editing', chord)
}

function stopEditing() {
  editingChordId.value = null
}

function onAnalyze() {
  emit('analyze', progression.value)
}

function parseChordString(chordStr) {
  if (!chordStr) return null
  const rootMatch = chordStr.match(/^[A-G][#b]?/)
  if (!rootMatch) return null
  const root = rootMatch[0]
  const quality = chordStr.substring(root.length)
  return {
    id: Date.now() + Math.random(),
    root,
    quality,
    inversion: 0,
    duration: 2
  }
}

function removeAllChords() {
  progression.value = []
  stopEditing()
  selectedChordIds.value.clear()
  clipboard.value = []
}

/**
 * Calcule le coût de transition
 */
function calculateMusicalCost(notesA, notesB, weights) {
  if (notesA.length === 0 || notesB.length === 0) return Infinity
  const sortedA = [...notesA].sort((a, b) => a - b)
  const sortedB = [...notesB].sort((a, b) => a - b)
  const sopranoMove = Math.abs(sortedA[sortedA.length - 1] - sortedB[sortedB.length - 1])
  const sopranoCost = sopranoMove * weights.soprano
  const bassMove = Math.abs(sortedA[0] - sortedB[0])
  const bassCost = bassMove * weights.bass
  let overallDistance = 0
  const len = Math.min(sortedA.length, sortedB.length)
  for (let i = 0; i < len; i++) {
    overallDistance += Math.abs(sortedA[i] - sortedB[i])
  }
  const overallCost = (overallDistance / len) * weights.overall
  return sopranoCost + bassCost + overallCost
}

/**
 * Traite une chaîne d'accords en choisissant le meilleur "voicing" (inversion/octave)
 * en se basant sur le fonctionnement spécifique de getNotesAsMidi.
 */
function processQuickImport() {
  if (!quickImportText.value.trim()) return

  const WEIGHTS = { soprano: 3.0, bass: 2.0, overall: 1.0 }
  const REPEATED_BASS_PENALTY = 10

  const chordStrings = quickImportText.value
    .split(/[; -]/)
    .map((s) => s.trim())
    .filter((s) => s)
  if (chordStrings.length === 0) {
    cancelQuickImport()
    return
  }

  const newChords = []
  let previousChordNotes =
    progression.value.length > 0
      ? getNotesAsMidi(progression.value[progression.value.length - 1])
      : null

  for (const chordStr of chordStrings) {
    const baseChord = parseChordString(chordStr)
    if (!baseChord) continue

    if (!previousChordNotes) {
      const firstChord = { ...baseChord }
      // Inversion de base différente selon la note, pour "centrer"
      if (['C', 'C#', 'D', 'D#', 'E'].includes(baseChord.root)) {
        firstChord.inversion = 1
      } else {
        firstChord.inversion = 0
      }

      newChords.push(firstChord)
      previousChordNotes = getNotesAsMidi(firstChord)
      continue
    }

    let bestInversion = 0
    let bestNotesForNextIteration = []
    let minCost = Infinity

    const rootPositionNotes = getNotesAsMidi({ ...baseChord, inversion: 0 })
    const voicingsPerOctave = rootPositionNotes.length

    const searchRangeStart = -voicingsPerOctave
    const searchRangeEnd = 2 * voicingsPerOctave

    for (let i = searchRangeStart; i < searchRangeEnd; i++) {
      const currentNotes = getNotesAsMidi({ ...baseChord, inversion: i })
      if (!currentNotes || currentNotes.length === 0) continue

      let cost = calculateMusicalCost(previousChordNotes, currentNotes, WEIGHTS)

      const previousBass = Math.min(...previousChordNotes)
      const currentBass = Math.min(...currentNotes)
      if (currentBass === previousBass) {
        cost += REPEATED_BASS_PENALTY
      }

      if (cost < minCost) {
        minCost = cost
        bestInversion = i
        bestNotesForNextIteration = currentNotes
      }
    }

    const finalChord = { ...baseChord, inversion: bestInversion }
    newChords.push(finalChord)
    previousChordNotes = bestNotesForNextIteration
  }

  if (newChords.length > 0) {
    progression.value = [...progression.value, ...newChords]
  }

  cancelQuickImport()
}
function cancelQuickImport() {
  showQuickImport.value = false
  quickImportText.value = ''
}

// --- Copy/Paste Logic ---

/**
 * Annule la dernière action enregistrée dans la pile d'annulation.
 */
function undoLastAction() {
  const lastAction = undoStack.value.pop()
  if (!lastAction) return // Rien à annuler

  if (lastAction.type === 'paste') {
    const idsToRemove = new Set(lastAction.payload.pastedChordIds)
    progression.value = progression.value.filter((chord) => !idsToRemove.has(chord.id))
    // On nettoie la sélection au cas où les accords supprimés étaient sélectionnés
    selectedChordIds.value.clear()
  }
}

function handleChordClick(chord, event) {
  if (event.ctrlKey || event.metaKey) {
    if (selectedChordIds.value.has(chord.id)) {
      selectedChordIds.value.delete(chord.id)
    } else {
      selectedChordIds.value.add(chord.id)
    }
  } else {
    selectedChordIds.value.clear()
    selectedChordIds.value.add(chord.id)
  }
}

function copySelectedChords() {
  if (selectedChordIds.value.size === 0) return
  // Copy in the order of appearance in the progression
  const chordsToCopy = progression.value.filter((chord) => selectedChordIds.value.has(chord.id))
  clipboard.value = chordsToCopy.map((c) => ({ ...c }))
}

function pasteChords() {
  if (clipboard.value.length === 0) return

  const newChords = clipboard.value.map((chord) => ({
    ...chord,
    id: Date.now() + Math.random()
  }))

  const newChordIds = newChords.map((c) => c.id)

  const currentProgression = [...progression.value]
  let pasteIndex = -1

  if (selectedChordIds.value.size > 0) {
    const indices = progression.value
      .map((c, i) => (selectedChordIds.value.has(c.id) ? i : -1))
      .filter((i) => i !== -1)
    if (indices.length > 0) {
      pasteIndex = Math.max(...indices)
    }
  }

  if (pasteIndex !== -1) {
    currentProgression.splice(pasteIndex + 1, 0, ...newChords)
  } else {
    currentProgression.push(...newChords)
  }

  progression.value = currentProgression

  undoStack.value.push({
    type: 'paste',
    payload: {
      pastedChordIds: newChordIds
    }
  })

  selectedChordIds.value.clear()
  newChords.forEach((c) => selectedChordIds.value.add(c.id))
}

function handleKeyDown(event) {
  const activeElementTag = document.activeElement?.tagName
  if (activeElementTag === 'INPUT' || activeElementTag === 'TEXTAREA') {
    return
  }

  const isCtrlOrCmd = event.ctrlKey || event.metaKey

  if (isCtrlOrCmd && event.key.toLowerCase() === 'c') {
    event.preventDefault()
    copySelectedChords()
  }

  if (isCtrlOrCmd && event.key.toLowerCase() === 'v') {
    event.preventDefault()
    pasteChords()
  }

  if (isCtrlOrCmd && event.key.toLowerCase() === 'z') {
    event.preventDefault()
    undoLastAction()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.builder-container {
  background-color: #2f2f2f;
  padding: 0.8rem 1rem;
  border-radius: 8px;
  max-height: fit-content;
}

.is-selected {
  box-shadow: 0 0 0 3px #0095ff;
  border-radius: 10px;
}

.is-playing-halo .chord-slot {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
  border-radius: 12px;
}

.footer-controls {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);

  display: flex;
  align-items: center;
  gap: 10px;

  padding: 19px 0 0 0;
}

.add-button {
  width: 35px;
  height: 35px;
  font-size: 16px;
  border-radius: 50%;
  border: 2px dashed #555;
  background-color: transparent;
  color: #888;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
}

.add-button:hover {
  background-color: #3c3c3c;
  color: white;
  border-color: #888;
}

.quick-import-input {
  background-color: #3c3c3c;
  border: 1px solid #555;
  color: white;
  border-radius: 6px;
  padding: 0.6rem 1rem;
  width: 150px;
  text-align: center;
}

.quick-import-input::placeholder {
  color: #888;
}

.quick-import-buttons {
  display: inline-flex;
  gap: 10px;
  margin-left: 5px;
}

.quick-import-button {
  width: 35px;
  height: 35px;
  border-radius: 50%;
  border: none;
  background-color: #4caf50;
  color: white;
  cursor: pointer;
}

.quick-import-button.cancel {
  background-color: #f44336;
}

.analyze-section-container {
  margin-top: 1rem;
  display: flex;
  justify-content: center;
}

.model-selector {
  display: flex;
  align-items: center;
  gap: 5px;
  background-color: #252525;
  border-radius: 8px;
  padding: 5px;
  border: 1px solid #444;
}

.analyze-icon-button {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.2s ease-in-out;
}

.analyze-icon-button:not(:disabled):hover {
  background-color: #0056b3;
}

.analyze-icon-button:disabled {
  background-color: #555;
  cursor: not-allowed;
  color: #888;
}

.radio-label {
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
}

.radio-label-sm {
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
}

.radio-label-sm.active {
  background-color: #007bff;
  color: white;
  font-weight: 500;
}

.radio-label-sm:not(.active):hover {
  background-color: #3f3f3f;
}

.radio-label-sm input[type='radio'] {
  display: none;
}

.analyze-button {
  padding: 1rem 2rem;
  font-size: 1.2rem;
  border-radius: 8px;
  border: none;
  background-color: #007bff;
  color: white;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.analyze-button:disabled {
  background-color: #555;
  cursor: not-allowed;
}

.error-message {
  color: #ff4d4d;
  text-align: center;
  margin-top: 1rem;
}
</style>
