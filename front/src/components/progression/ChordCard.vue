<template>
  <div ref="chordSlotRef" class="chord-slot" :style="{ width: cardWidth }">
    <button class="chord-button" @click="$emit('start-editing')">
      {{ chordDisplayName }}
    </button>

    <button class="remove-button" @click="$emit('remove')">×</button>
    <Teleport to="body">
      <div v-if="isEditing" ref="editorPopoverRef" class="editor-popover" :style="popoverStyle">
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
              <button @click="changeInversion(-1)" class="inversion-button">-</button>
              <span>Position {{ chord.inversion + 1 }}</span>
              <button @click="changeInversion(1)" class="inversion-button">+</button>
            </div>
          </div>
        </div>
        <button @click="$emit('stop-editing')" class="close-editor">OK</button>
      </div>
    </Teleport>

    <div v-if="!isEditing" class="resize-handle" @mousedown.prevent="startResize"></div>
  </div>
</template>

<script setup>
import { ref, computed, watch, nextTick } from 'vue'
import { QUALITIES, NOTES } from '@/constants.js'
import { piano, getNotesForChord } from '@/sampler.js'
import { ALL_PLAYABLE_NOTES } from '@/keyboard.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  isEditing: { type: Boolean, default: false },
  beatWidth: { type: Number, required: true }
})

const emit = defineEmits(['update:modelValue', 'remove', 'start-editing', 'stop-editing'])

const editorPopoverRef = ref(null)
const chordSlotRef = ref(null)
const popoverStyle = ref(null)

const chord = computed({
  get: () => props.modelValue,
  set: (newValue) => {
    emit('update:modelValue', newValue)
  }
})

const activeQualityCategory = ref(null)
const chordDisplayName = computed(() => {
  return `${chord.value.root}${chord.value.quality}`
})
const activeQualityOptions = computed(() => {
  if (!activeQualityCategory.value) return []
  const group = QUALITIES.find((g) => g.label === activeQualityCategory.value)
  return group ? group.options : []
})
watch(
  () => props.isEditing,
  (isEditing) => {
    if (isEditing) {
      nextTick(() => {
        if (!chordSlotRef.value || !editorPopoverRef.value) return

        const triggerRect = chordSlotRef.value.getBoundingClientRect()
        const popoverRect = editorPopoverRef.value.getBoundingClientRect()
        const viewportWidth = window.innerWidth
        const viewportHeight = window.innerHeight
        const margin = 10

        let finalTop = triggerRect.bottom + margin

        if (finalTop + popoverRect.height > viewportHeight - margin) {
          finalTop = triggerRect.top - popoverRect.height - margin
        }

        let finalLeft = triggerRect.left + triggerRect.width / 2
        const popoverHalfWidth = popoverRect.width / 2

        if (finalLeft + popoverHalfWidth > viewportWidth - margin) {
          finalLeft = viewportWidth - popoverHalfWidth - margin
        }

        if (finalLeft - popoverHalfWidth < margin) {
          finalLeft = popoverHalfWidth + margin
        }

        popoverStyle.value = {
          position: 'absolute',
          top: `${finalTop + window.scrollY}px`,
          left: `${finalLeft + window.scrollX}px`
        }
      })

      let foundCategory = null
      if (chord.value.quality) {
        for (const group of QUALITIES) {
          if (group.options.some((opt) => opt.value === chord.value.quality)) {
            foundCategory = group.label
            break
          }
        }
      }
      activeQualityCategory.value = foundCategory || 'Majeurs'
    }
  }
)
function isNoteActive(note) {
  return chord.value.root === getNoteValue(note)
}

const normalizeNote = (note) => {
  const noteMap = { Db: 'C#', Eb: 'D#', Gb: 'F#', Ab: 'G#', Bb: 'A#' }
  const octave = note.slice(-1)
  const root = note.slice(0, -1)
  const mappedRoot = noteMap[root] || root
  return mappedRoot + octave
}

function changeInversion(direction) {
  const currentInversion = props.modelValue.inversion || 0
  const newInversion = currentInversion + direction

  const testChord = { ...props.modelValue, inversion: newInversion }
  const notes = getNotesForChord(testChord)

  if (!notes || notes.length === 0) return

  // Valider en utilisant la liste des notes du clavier
  const areNotesInRange = notes.every((note) => {
    const normalized = normalizeNote(note)
    return ALL_PLAYABLE_NOTES.includes(normalized)
  })

  if (areNotesInRange) {
    emit('update:modelValue', testChord)
    piano.play({ ...chord.value })
  } else {
    console.warn(
      `Le renversement ${newInversion} produit des notes hors de la tessiture du clavier.`
    )
  }
}
function updateChord(key, value) {
  emit('update:modelValue', { ...chord.value, [key]: value })
  piano.play({ ...chord.value, [key]: value })
}
function getNoteValue(note) {
  return note.split(' / ')[0]
}

const cardWidth = computed(() => {
  const duration = props.modelValue.duration || 4
  return `${duration * props.beatWidth}px`
})

const initialMouseX = ref(0)
const initialDuration = ref(0)

function startResize(event) {
  initialMouseX.value = event.clientX
  initialDuration.value = props.modelValue.duration || 4

  window.addEventListener('mousemove', doResize)
  window.addEventListener('mouseup', stopResize)
}

function doResize(event) {
  const deltaX = event.clientX - initialMouseX.value
  const durationChange = Math.round(deltaX / props.beatWidth)

  let newDuration = initialDuration.value + durationChange
  newDuration = Math.max(1, newDuration)

  if (newDuration !== props.modelValue.duration) {
    emit('update:modelValue', {
      ...props.modelValue,
      duration: newDuration
    })
  }
}
/**
 * Termine le processus de redimensionnement et nettoie les écouteurs.
 */
function stopResize() {
  window.removeEventListener('mousemove', doResize)
  window.removeEventListener('mouseup', stopResize)
}
</script>

<style scoped>
.chord-slot {
  position: relative;
  cursor: grab;
  min-width: 60px;
  transition: width 0.1s ease-out;
}
.chord-button {
  padding: 1rem 0;
  font-size: 17px;
  font-weight: 600;
  border-radius: 8px;
  border: 2px solid #555;
  background-color: #3c3c3c;
  color: white;
  width: 100%;
  height: 100%;
  transition: all 0.2s;
}
.chord-button:hover {
  border-color: #007bff;
}
.remove-button {
  position: absolute;
  top: 0px;
  left: 0px;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  border: none;
  background-color: #ff4d4d;
  color: white;
  font-weight: bold;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}

.editor-popover {
  position: absolute;
  transform: translateX(-50%);
  border: 1px solid #555555;
  width: 640px;
  background-color: #2c2c2e;
  color: white;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  z-index: 10;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.resize-handle {
  position: absolute;
  right: 0px;
  top: 0;
  bottom: 0;
  width: 6px;
  cursor: ew-resize;
  z-index: 5;
  border-top-right-radius: 10px;
  border-bottom-right-radius: 10px;
  opacity: 0.5;
  background-color: #c2bdbd;
  transition: opacity 0.2s;
}

.resize-handle:hover {
  opacity: 1;
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
  padding: 5px 10px;
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
.category-tabs::-webkit-scrollbar {
  height: 4px;
}
.category-tabs::-webkit-scrollbar-track {
  background: #4a4a4a;
}
.category-tabs::-webkit-scrollbar-thumb {
  background-color: #888;
  border-radius: 2px;
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
.inversion-control-footer span {
  font-weight: 500;
  color: #d1d1d6;
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
  transition: background-color 0.2s;
}
.inversion-button:hover {
  background-color: #5f5f5f;
}
.inversion-button:active {
  background-color: #3a3a3c;
}

.close-editor {
  padding: 12px;
  background-color: #0a84ff;
  border: none;
  color: white;
  cursor: pointer;
  font-size: 1rem;
  font-weight: bold;
  transition: background-color 0.2s;
}
.close-editor:hover {
  background-color: #0073e6;
}
</style>
