<template>
  <div ref="pianoContainer" class="piano-container">
    <div class="piano-keyboard">
      <div v-for="key in whiteKeys" :key="key.note" class="white-key-wrapper">
        <button
          :class="getNoteClasses(key.note, 'white')"
          :disabled="props.disabled"
          @click="clickNote(key.note)"
        />
        <button
          v-if="key.blackKey"
          :class="getNoteClasses(key.blackKey, 'black')"
          :disabled="props.disabled"
          @click.stop="clickNote(key.blackKey)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, computed } from "vue";
import { whiteKeys } from "@/keyboard.js";

const emit = defineEmits(["add-note", "remove-note"]);
const pianoContainer = ref(null);

const props = defineProps({
  activeNotes: {
    type: Array,
    default: () => [],
  },
  disabled: {
    type: Boolean,
    default: false,
  },
});

const normalizedActiveNotes = computed(() => {
  const noteMap = { Db: "C#", Eb: "D#", Gb: "F#", Ab: "G#", Bb: "A#" };
  return props.activeNotes.map((note) => {
    const octave = note.slice(-1);
    const root = note.slice(0, -1);
    const mappedRoot = noteMap[root] || root;
    return mappedRoot + octave;
  });
});

function getNoteClasses(note, type) {
  const isActive = normalizedActiveNotes.value.includes(note);
  return {
    "piano-key": true,
    white: type === "white",
    black: type === "black",
    active: isActive,
  };
}

function clickNote(note) {
  const isActive = normalizedActiveNotes.value.includes(note);

  if (isActive) {
    emit("remove-note", note);
  } else {
    emit("add-note", note);
  }
}

onMounted(() => {
  const container = pianoContainer.value;
  if (container) {
    const centerPosition = (container.scrollWidth - container.clientWidth) / 2;
    container.scrollLeft = centerPosition;
  }
});
</script>
<style scoped>
.piano-container {
  overflow-x: auto;
  display: flex;
  border-radius: 8px;
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
