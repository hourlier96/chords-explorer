<template>
  <div class="piano-container">
    <div class="piano-keyboard">
      <div v-for="key in whiteKeys" :key="key.note" class="white-key-wrapper">
        <div :class="getNoteClasses(key.note, 'white')" @click="playNote(key.note)"></div>

        <div
          v-if="key.blackKey"
          :class="getNoteClasses(key.blackKey, 'black')"
          @click.stop="playNote(key.blackKey)"
        ></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { piano } from '@/sampler.js'
import { whiteKeys } from '@/keyboard.js'

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
  return {
    'piano-key': true,
    white: type === 'white',
    black: type === 'black',
    active: isActive
  }
}

async function playNote(note) {
  piano.triggerAttackRelease(note, '8n')
}
</script>

<style scoped>
.piano-container {
  overflow-x: auto;
}

.piano-keyboard {
  display: flex;
  background: #000;
  flex-wrap: 0;
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
  width: 40px;
  height: 180px;
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
  right: -14px;
  width: 28px;
  height: 110px;
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
