<template>
  <div class="analysis-card">
    <div class="card-content">
      <div class="chord-name">{{ item.chord }}</div>
      <div class="numeral-display">
        <span class="found-numeral" :class="getChordClass(item)">
          {{ item.found_numeral ? item.found_numeral : ' ' }}
        </span>
        <v-tooltip v-if="borrowedInfo && !isSubstitution" location="right" max-width="300px">
          <template #activator="{ props: tooltipProps }">
            <v-icon
              v-bind="tooltipProps"
              icon="mdi-information"
              size="x-small"
              class="info-icon"
            ></v-icon>
          </template>
          <div class="borrowed-info-tooltip">
            <div v-for="(borrowed, idx) in borrowedInfo" :key="idx">
              {{ analysis.result.tonic }}
              {{ borrowed }}
            </div>
          </div>
        </v-tooltip>
      </div>
    </div>

    <div class="resize-handle" @mousedown.prevent="startResize"></div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
  analysis: { type: Object, required: true },
  piano: { type: Object, required: true },
  isSubstitution: { type: Boolean, default: false },
  beatWidth: { type: Number, required: true }
})

const emit = defineEmits(['update:item'])

const initialMouseX = ref(0)
const initialDuration = ref(0)

const borrowedInfo = computed(() => {
  return props.analysis.result.borrowed_chords?.[props.item.chord]
})

function getChordClass(item) {
  const isBorrowed = !item.is_diatonic && borrowedInfo.value
  const isForeign = !item.is_diatonic && !borrowedInfo.value
  return {
    borrowed_chord: isBorrowed,
    foreign_chord: isForeign,
    substitution_chord: props.isSubstitution
  }
}

/**
 * Démarre le processus de redimensionnement au clic sur la poignée.
 */
function startResize(event) {
  initialMouseX.value = event.clientX
  initialDuration.value = props.item.duration || 4

  window.addEventListener('mousemove', doResize)
  window.addEventListener('mouseup', stopResize)
}

/**
 * Calcule et applique le redimensionnement pendant le mouvement de la souris.
 */
function doResize(event) {
  const deltaX = event.clientX - initialMouseX.value
  const durationChange = Math.round(deltaX / props.beatWidth)
  let newDuration = initialDuration.value + durationChange
  newDuration = Math.max(1, newDuration)
  emit('update:item', {
    ...props.item,
    duration: newDuration
  })
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
.analysis-card {
  position: relative;
  box-sizing: border-box;
  transition: width 0.1s ease-out;
  width: 100%;
}

.card-content {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  border: 2px solid #555;
  background-color: #3c3c3c;
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  transition: all 0.2s;
}

.analysis-card:hover .card-content {
  border-color: #777;
}

.chord-name {
  font-size: 17px;
  font-weight: 600;
}

.numeral-display {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
  min-height: 2rem;
}

.found-numeral {
  font-family: 'Courier New', Courier, monospace;
  font-size: 1rem;
  font-weight: bold;
  color: #2ecc71;
}

.info-icon {
  color: #aaa;
  cursor: help;
}

.found-numeral.borrowed_chord {
  color: #f1c40f;
}
.found-numeral.foreign_chord {
  color: #e74c3c;
}
.found-numeral.substitution_chord {
  color: #bdc3c7;
}

.secondary-dominant-badge {
  position: absolute;
  top: -8px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  padding: 0.2rem 0.8rem;
  border-radius: 1rem;
  background-color: #4f3b78;
  border: 1px solid #7a5ba9;
  color: #e6dff2;
  font-size: 0.8rem;
  font-weight: 500;
  white-space: nowrap;
}

.play-button-corner {
  position: absolute;
  top: 0px;
  left: 0px;
  z-index: 5;
}

.borrowed-info-tooltip {
  font-size: 10px;
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
