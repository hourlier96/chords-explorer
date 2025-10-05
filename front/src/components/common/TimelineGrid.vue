<template>
  <div
    class="timeline-container"
    :style="{
      '--total-beats': totalBeats,
      '--beat-width': `${beatWidth}px`
    }"
  >
    <div class="playhead" :style="{ transform: `translateX(${playheadPosition}px)` }"></div>

    <div class="rhythm-timeline" @click="handleClick">
      <template v-for="beat in totalBeats" :key="`timeline-beat-${beat}`">
        <div
          class="beat-marker"
          :class="{ 'measure-start': (beat - 1) % beatsPerMeasure === 0 }"
          :style="{ 'grid-column-start': beat }"
        >
          <span v-if="(beat - 1) % beatsPerMeasure === 0" class="measure-number">
            {{ Math.floor((beat - 1) / beatsPerMeasure) + 1 }}
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  totalBeats: { type: Number, required: true },
  beatsPerMeasure: { type: Number, required: true },
  beatWidth: { type: Number, required: true },
  isPlaying: { type: Boolean, default: false },
  playheadPosition: { type: Number, default: 0 }
})

const emit = defineEmits(['seek'])

function handleClick(event) {
  const clickX = event.offsetX

  const targetBeat = clickX / props.beatWidth
  emit('seek', targetBeat)
}
</script>

<style scoped>
.timeline-container {
  position: relative;
  width: 100%;
  padding-top: 20px;
}

.playhead {
  position: absolute;
  top: 15px;
  left: 0;
  width: 2px;
  height: calc(100% - 15px);
  background-color: #f44336;
  z-index: 10;
  pointer-events: none;
}

.rhythm-timeline {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  height: 20px;
  border-bottom: 1px solid #444;
  cursor: pointer;
  width: fit-content;
}

.beat-marker {
  height: 100%;
  width: 1px;
  background-color: rgba(255, 255, 255, 0.2);
  justify-self: start;
  position: relative;
}
.beat-marker.measure-start {
  width: 2px;
  background-color: rgba(255, 255, 255, 0.6);
}
.measure-number {
  position: absolute;
  top: -20px;
  left: 4px;
  font-size: 12px;
  color: #aaa;
}
</style>
