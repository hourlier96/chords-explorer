<template>
  <v-card outlined>
    <div v-if="chord" class="editor-content-wrapper">
      <div class="editor-content">
        <div class="root-note-selector">
          <template v-for="note in NOTES" :key="note">
            <div v-if="note.includes(' / ')" class="enharmonic-pair">
              <div
                v-for="enharmonicNote in note.split(' / ')"
                :key="enharmonicNote"
                @click="!props.disabled && updateChord('root', enharmonicNote)"
                :class="{ active: isNoteActive(enharmonicNote), disabled: props.disabled }"
                class="note-badge"
              >
                {{ enharmonicNote }}
              </div>
            </div>
            <div
              v-else
              @click="!props.disabled && updateChord('root', note)"
              :class="{ active: isNoteActive(note), disabled: props.disabled }"
              class="note-badge"
            >
              {{ note }}
            </div>
          </template>
        </div>
        <div class="main-content">
          <div class="quality-selector">
            <div class="category-tabs">
              <div
                v-for="group in QUALITIES"
                :key="group.label"
                @click="!props.disabled && (activeQualityCategory = group.label)"
                :class="{ active: activeQualityCategory === group.label, disabled: props.disabled }"
                class="category-badge"
              >
                {{ group.label }}
              </div>
            </div>
            <div class="options-grid">
              <div
                v-for="option in activeQualityOptions"
                :key="option.value"
                @click="!props.disabled && updateChord('quality', option.value)"
                :class="{ active: chord.quality === option.value, disabled: props.disabled }"
                class="option-badge"
              >
                {{ option.text }}
              </div>
            </div>
          </div>
          <div class="inversion-control-footer">
            <div
              @click="!isLegacyInversionDisabled && changeInversion(-1)"
              class="inversion-badge"
              :class="{ disabled: isLegacyInversionDisabled }"
            >
              -
            </div>
            <span v-if="chord?.notes === undefined">Position {{ chord.inversion + 1 }}</span>
            <div
              @click="!isLegacyInversionDisabled && changeInversion(1)"
              class="inversion-badge"
              :class="{ disabled: isLegacyInversionDisabled }"
            >
              +
            </div>
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
  modelValue: { type: Object, default: null },
  disabled: { type: Boolean, default: false }
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
/* ... (styles existants inchangés) ... */
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

/* Les .note-button deviennent .note-badge */
.note-badge {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  user-select: none;
  background-color: transparent;
  color: #ccc;
  font-size: 0.9rem;
  min-width: 60px;
  padding: 4px 12px;
  margin: 2px 0;
  border-radius: 4px;
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}

.note-badge:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.note-badge.active {
  background-color: #007bff;
  color: white;
  font-weight: bold;
}

.enharmonic-pair {
  display: flex;
}
.enharmonic-pair .note-badge {
  min-width: 30px;
  flex-grow: 1;
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
  gap: 6px;
  padding-bottom: 12px;
}

/* Le sélecteur cible maintenant .category-badge */
.category-badge {
  padding: 3px 10px;
  border-radius: 1rem; /* Forme "pilule" pour un look de badge */
  border: 1px solid #555;
  background-color: transparent;
  color: #ccc;
  font-size: 0.75rem;
  transition: all 0.2s ease;
  cursor: pointer;
  user-select: none;
}
.category-badge:hover {
  background-color: rgba(255, 255, 255, 0.05);
  border-color: #777;
}
.category-badge.active {
  background-color: #007bff;
  color: white;
  border-color: #007bff;
  font-weight: bold;
}

.options-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(85px, 1fr));
  gap: 0.5rem;
  overflow-y: auto;
  padding: 0.2rem;
}

/* Le sélecteur cible maintenant .option-badge */
.option-badge {
  width: 100%;
  padding: 0.4rem 0.2rem;
  border-radius: 6px;
  border: 1px solid #555;
  background-color: #333;
  color: #ddd;
  font-size: 0.8rem;
  transition: all 0.2s ease;
  cursor: pointer;
  user-select: none;
  text-align: center;
}
.option-badge:hover {
  border-color: #007bff;
  color: white;
  background-color: #3a3a3a;
}
.option-badge.active {
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

/* Le sélecteur cible maintenant .inversion-badge */
.inversion-badge {
  font-family: monospace;
  font-size: 1.2rem;
  font-weight: bold;
  line-height: 1;
  padding: 6px 16px;
  border-radius: 6px;
  border: 1px solid #5f5f5f;
  background-color: #444;
  color: white;
  cursor: pointer;
  user-select: none;
  transition: all 0.2s ease;
}
.inversion-badge:hover {
  background-color: #555;
  border-color: #777;
}

/* Nouvelle règle pour gérer l'état désactivé */
.disabled {
  cursor: not-allowed !important;
  opacity: 0.5;
  pointer-events: none; /* Empêche tout événement de souris */
}
</style>
