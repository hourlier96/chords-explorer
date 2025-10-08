<template>
  <div ref="chordSlotRef" class="chord-slot" :style="{ width: cardWidth }">
    <button class="chord-button" @click="$emit('start-editing')">
      {{ chordDisplayName }}
    </button>
    <button class="remove-button" @click="$emit('remove')">×</button>
    <div class="resize-handle" @mousedown.prevent="startResize"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  beatWidth: { type: Number, required: true }
})

const emit = defineEmits(['update:modelValue', 'remove', 'start-editing'])

const chordDisplayName = computed(() => {
  return `${props.modelValue.root}${props.modelValue.quality}`
})

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
  padding: 1.5rem 0;
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
  justify-content: center;
  line-height: 1;
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
</style>
