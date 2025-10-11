<template>
  <div class="timeline-container">
    <div class="main-toolbar">
      <PlayerControls
        :is-playing="isPlaying"
        :is-track-empty="items.length === 0"
        v-model:time-signature="timeSignature"
        v-model:is-metronome-active="isMetronomeActive"
        v-model:is-looping="isLooping"
        @play="playEntireProgression"
        @stop="stopSound"
      />
      <slot name="toolbar-controls"></slot>
    </div>

    <v-card>
      <div ref="gridContainerRef" class="progression-grid-container" @click="$emit('grid-click')">
        <slot name="header"></slot>

        <TimelineGrid
          :total-beats="totalBeats"
          :beats-per-measure="beatsPerMeasure"
          :beat-width="BEAT_WIDTH"
          :is-playing="isPlaying"
          :playhead-position="playheadPosition"
          @seek="handleSeek"
        />

        <slot name="above-track"></slot>
        <div
          class="items-track"
          :style="{
            '--total-beats': totalBeats,
            '--beat-width': `${BEAT_WIDTH}px`
          }"
        >
          <draggable
            v-if="draggable"
            :modelValue="itemsWithPositions"
            @end="$emit('drag-end', $event)"
            item-key="id"
            class="draggable-container"
            ghost-class="ghost"
          >
            <template #item="{ element: item, index }">
              <div
                class="item-wrapper"
                :style="{ gridColumn: `${item.start} / span ${item.duration}` }"
                :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
                @click.stop="$emit('item-click', item, $event)"
              >
                <slot name="item" :item="item" :index="index"></slot>
              </div>
            </template>
          </draggable>

          <div v-else class="draggable-container">
            <template v-for="(item, index) in itemsWithPositions" :key="item.id">
              <div
                class="item-wrapper"
                :style="{ gridColumn: `${item.start} / span ${item.duration}` }"
                :class="{ 'is-playing-halo': index === currentlyPlayingIndex }"
                @click.stop="$emit('item-click', item, $event)"
              >
                <slot name="item" :item="item" :index="index"></slot>
              </div>
            </template>
          </div>
        </div>

        <div class="footer-controls-container">
          <slot name="footer"></slot>
        </div>
      </div>
    </v-card>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import draggable from 'vuedraggable'

import { BEAT_WIDTH, useStatePlayer } from '@/composables/useStatePlayer.ts'
import TimelineGrid from '@/components/common/TimelineGrid.vue'
import PlayerControls from '@/components/common/PlayerControls.vue'

const props = defineProps({
  items: { type: Array, required: true },
  playCallback: { type: Function, required: true },
  draggable: { type: Boolean, default: false }
})

const emit = defineEmits(['drag-end', 'item-click', 'grid-click'])

const gridContainerRef = ref(null)
defineExpose({
  gridContainerRef
})

// Calcule les positions de départ pour chaque élément
const itemsWithPositions = computed(() => {
  let currentBeat = 1
  return props.items.map((item) => {
    const start = currentBeat
    currentBeat += item.duration
    return { ...item, start }
  })
})

const handlePlayItem = async (payload) => {
  // On délègue la logique de lecture à la fonction passée en prop
  await props.playCallback(payload)
}

const {
  playheadPosition,
  beatsPerMeasure,
  totalBeats,
  isPlaying,
  currentlyPlayingIndex,
  timeSignature,
  isMetronomeActive,
  isLooping,
  playEntireProgression,
  stopSound,
  seek
} = useStatePlayer(itemsWithPositions, { onPlayItemAsync: handlePlayItem })

// Logique de défilement pendant la lecture
watch(playheadPosition, (newPixelPosition) => {
  if (!isPlaying.value || !gridContainerRef.value) return
  const container = gridContainerRef.value
  const containerWidth = container.clientWidth
  const targetScrollLeft = newPixelPosition - containerWidth / 2
  container.scrollTo({
    left: targetScrollLeft,
    behavior: 'auto'
  })
})

// Logique de positionnement au clic (seek)
function findClosestChordStartBeat(beat) {
  const targetItem = itemsWithPositions.value.find(
    (item) => beat + 1 >= item.start && beat + 1 < item.start + item.duration
  )
  return targetItem ? targetItem.start - 1 : beat
}

async function handleSeek(targetBeat) {
  const snappedBeat = findClosestChordStartBeat(targetBeat)
  const wasPlaying = isPlaying.value
  if (wasPlaying) {
    await stopSound()
    seek(snappedBeat)
    playEntireProgression()
  } else {
    seek(snappedBeat)
  }
}
</script>

<style scoped>
.progression-grid-container {
  overflow-x: auto;

  position: relative;

  padding: 1rem 1rem 4rem 1rem;

  background-color: #252525;
  border: 1px solid #444;
  border-radius: 8px;
}

.items-track {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  grid-auto-rows: minmax(100px, auto);
  align-items: stretch;
  min-height: 110px;
  cursor: default;
}
.draggable-container {
  display: contents;
}
.item-wrapper {
  height: 100%;
  display: flex;
  align-items: center;
  border-radius: 12px;
  transition: box-shadow 0.2s ease-in-out;
  cursor: pointer;
}

.footer-controls-container {
  position: sticky;
  bottom: 1rem;
  left: 0;
  width: 100%;
  z-index: 10;
}
</style>
