<template>
  <v-card outlined>
    <v-card-title>Éditeur d'accord</v-card-title>
    <div v-if="chord" class="editor-content-wrapper">
      <div class="editor-content">
        <div class="root-note-selector">
          <template v-for="note in NOTES" :key="note">
            <div v-if="note.includes(' / ')" class="enharmonic-pair">
              <button
                v-for="enharmonicNote in note.split(' / ')"
                :key="enharmonicNote"
                @click="updateChord('root', enharmonicNote)"
                :class="{ active: isNoteActive(enharmonicNote) }"
                class="note-button"
              >
                {{ enharmonicNote }}
              </button>
            </div>
            <button
              v-else
              @click="updateChord('root', note)"
              :class="{ active: isNoteActive(note) }"
              class="note-button"
            >
              {{ note }}
            </button>
          </template>
        </div>
        <div class="main-content">
          <div class="quality-selector">
            <div class="category-tabs">
              <button
                v-for="group in QUALITIES"
                :key="group.label"
                @click="activeQualityCategory = group.label"
                :class="{ active: activeQualityCategory === group.label }"
                class="category-tab"
              >
                {{ group.label }}
              </button>
            </div>
            <div class="options-grid">
              <button
                v-for="option in activeQualityOptions"
                :key="option.value"
                @click="updateChord('quality', option.value)"
                :class="{ active: chord.quality === option.value }"
                class="option-button"
              >
                {{ option.text }}
              </button>
            </div>
          </div>
          <div class="inversion-control-footer">
            <v-btn
              @click="changeInversion(-1)"
              class="inversion-button"
              :disabled="chord?.notes?.length > 0"
            >
              -
            </v-btn>
            <span v-if="chord?.notes === undefined">Position {{ chord.inversion + 1 }}</span>
            <v-btn
              @click="changeInversion(1)"
              class="inversion-button"
              :disabled="chord?.notes?.length > 0"
            >
              +
            </v-btn>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="placeholder-text">Cliquez sur un accord pour l'éditer.</div>
  </v-card>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { QUALITIES, NOTES } from '@/constants.js'
import { piano, getNotesForChord } from '@/sampler.js'
import { ALL_PLAYABLE_NOTES } from '@/keyboard.js'
import { ENHARMONIC_EQUIVALENTS } from '@/constants.js'

const props = defineProps({
  modelValue: { type: Object, default: null }
})

const emit = defineEmits(['update:modelValue'])

const chord = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit('update:modelValue', newValue)
  }
})

const activeQualityCategory = ref('Majeurs')

const activeQualityOptions = computed(() => {
  if (!activeQualityCategory.value) return []
  const group = QUALITIES.find((g) => g.label === activeQualityCategory.value)
  return group ? group.options : []
})

watch(
  () => chord.value,
  (newChord) => {
    if (newChord) {
      let foundCategory = null
      if (newChord.quality) {
        for (const group of QUALITIES) {
          if (group.options.some((opt) => opt.value === newChord.quality)) {
            foundCategory = group.label
            break
          }
        }
      }
      activeQualityCategory.value = foundCategory || 'Majeurs'
    }
  },
  { immediate: true }
)

function isNoteActive(note) {
  if (!chord.value) return false
  return chord.value.root === note.split(' / ')[0]
}

function updateChord(key, value) {
  const newChord = { ...chord.value, [key]: value }
  chord.value = newChord
  delete newChord.notes
  piano.play(newChord)
}

const normalizeNote = (note) => {
  const octave = note.slice(-1)
  const root = note.slice(0, -1)
  const mappedRoot = ENHARMONIC_EQUIVALENTS[root] || root
  return mappedRoot + octave
}

function changeInversion(direction) {
  const currentInversion = chord.value.inversion || 0
  const newInversion = currentInversion + direction
  const testChord = { ...chord.value, inversion: newInversion }
  const notes = getNotesForChord(testChord)

  if (!notes || notes.length === 0) return

  const areNotesInRange = notes.every((note) => {
    const normalized = normalizeNote(note)
    return ALL_PLAYABLE_NOTES.includes(normalized)
  })

  if (areNotesInRange) {
    chord.value = testChord
    piano.play(testChord)
  }
}
</script>

<style scoped>
.placeholder-text {
  text-align: center;
  color: #888;
  padding: 2rem;
}
.editor-content {
  display: flex;
  flex-direction: row;
  max-height: 270px;
}

.root-note-selector {
  display: flex;
  flex-direction: column;
  overflow-y: auto;
  border-right: 1px solid #444;
  padding: 5px;
  flex-shrink: 0;
}
.note-button {
  background: none;
  border: none;
  color: #a9a9b0;
  padding: 2px 5px;
  cursor: pointer;
  text-align: center;
  font-size: 1rem;
  border-radius: 6px;
  transition:
    background-color 0.2s,
    color 0.2s;
}
.note-button:hover {
  background-color: #3a3a3c;
}
.note-button.active {
  background-color: #0a84ff;
  color: white;
  font-weight: bold;
}

.main-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.quality-selector {
  flex-grow: 1;
  padding: 10px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 6px 0;
  padding-bottom: 8px;
}
.category-tabs button {
  flex-shrink: 0;
  padding: 0.25rem 0.75rem;
  margin-right: 0.5rem;
  border-radius: 1rem;
  border: 1px solid transparent;
  background-color: #5f5f5f;
  color: #ddd;
  font-size: 0.8rem;
  transition: all 0.2s;
  cursor: pointer;
}
.category-tabs button:hover {
  background-color: #777;
}
.category-tabs button.active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
  gap: 0.5rem;
  overflow-y: auto;
  padding: 0.25rem;
}
.options-grid button {
  width: 100%;
  padding: 0.5rem 0.25rem;
  border-radius: 4px;
  border: 1px solid #5f5f5f;
  background-color: #3c3c3c;
  color: #ddd;
  font-size: 0.9rem;
  transition: all 0.2s;
  cursor: pointer;
}
.options-grid button:hover {
  border-color: #007bff;
  color: white;
}
.options-grid button.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: bold;
}

.inversion-control-footer {
  flex-shrink: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  border-top: 1px solid #444;
  background-color: #2c2c2e;
}
.inversion-button {
  font-family: monospace;
  font-size: 1.5rem;
  font-weight: bold;
  line-height: 1;
  padding: 5px 15px;
  border-radius: 8px;
  border: 1px solid #5f5f5f;
  background-color: #4a4a4a;
  color: white;
  cursor: pointer;
}
</style>
