<template>
  <div class="piano-container" ref="pianoContainer">
    <div class="piano-keyboard">
      <div v-for="key in whiteKeys" :key="key.note" class="white-key-wrapper">
        <div :class="getNoteClasses(key.note, 'white')" @click="clickNote(key.note)"></div>
        <div
          v-if="key.blackKey"
          :class="getNoteClasses(key.blackKey, 'black')"
          @click.stop="clickNote(key.blackKey)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from 'vue'
import { whiteKeys } from '@/keyboard.js'
import { piano } from '@/sampler.js'

const emit = defineEmits(['add-note', 'remove-note'])
const pianoContainer = ref(null)
const clickedNote = ref([])

const props = defineProps({
  activeNotes: {
    type: Array,
    default: () => []
  }
})

const normalizedActiveNotes = computed(() => {
  const noteMap = { Db: 'C#', Eb: 'D#', Gb: 'F#', Ab: 'G#', Bb: 'A#' }
  return props.activeNotes.map((note) => {
    const octave = note.slice(-1)
    const root = note.slice(0, -1)
    const mappedRoot = noteMap[root] || root
    return mappedRoot + octave
  })
})

function getNoteClasses(note, type) {
  const isActive = normalizedActiveNotes.value.includes(note)
  const isLocallyActive = clickedNote.value.includes(note)
  return {
    'piano-key': true,
    white: type === 'white',
    black: type === 'black',
    active: isActive || isLocallyActive
  }
}

function clickNote(note) {
  const isParentActive = normalizedActiveNotes.value.includes(note)
  const isLocallyActive = clickedNote.value.includes(note)
  const isVisuallyActive = isParentActive || isLocallyActive

  if (isVisuallyActive) {
    emit('remove-note', note)
    clickedNote.value = clickedNote.value.filter((n) => n !== note)
  } else {
    emit('add-note', note)
    clickedNote.value.push(note)
    piano.triggerAttackRelease(note, '8n')
  }
}

onMounted(() => {
  // L'objet `pianoContainer.value` contient maintenant l'élément DOM réel
  const container = pianoContainer.value

  if (container) {
    // 1. Calculer le milieu du contenu total (scrollable)
    const scrollWidth = container.scrollWidth

    // 2. Calculer la largeur visible du conteneur
    const clientWidth = container.clientWidth

    // 3. Calculer la position pour centrer le contenu
    const centerPosition = (scrollWidth - clientWidth) / 2

    // 4. Appliquer le défilement horizontal
    container.scrollLeft = centerPosition
  }
})
</script>

<style scoped>
.piano-container {
  overflow-x: auto;
  display: flex;
}

.piano-keyboard {
  display: inline-flex;
  flex-wrap: nowrap;
  margin: 0 auto;
}

.white-key-wrapper {
  position: relative;
}

.piano-key {
  border: 1px solid #000;
  box-sizing: border-box;
  cursor: pointer;
  transition: background-color 0.1s ease;
}

.piano-key.white {
  width: 30px;
  height: 110px;
  background-color: #f8f8f8;
  border-bottom-left-radius: 5px;
  border-bottom-right-radius: 5px;
}

.piano-key.white:hover {
  background-color: #e0e0e0;
}

.piano-key.black {
  position: absolute;
  top: 0;
  right: -10px;
  width: 19px;
  height: 63px;
  background-color: #222;
  z-index: 1;
  border-radius: 4px;
}

.piano-key.black:hover {
  background-color: #444;
}

.piano-key.active {
  background-color: #ff4136;
  border-color: #c42c22;
}
</style>
