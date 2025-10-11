<template>
  <div class="detailed-analysis-container">
    <ProgressionTimeline
      :items="displayedProgression"
      :play-callback="playAnalysisChordItem"
      :draggable="false"
    >
      <template #header>
        <div class="substitution-header">
          <div v-if="!isSubstitution" class="legend">
            <div class="legend-item">
              <div class="legend-dot" style="background-color: #2ecc71"></div>
              <span>Diatonique</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background-color: #f1c40f"></div>
              <span>Emprunts modaux</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background-color: red"></div>
              <span>Hors tonalité</span>
            </div>
          </div>
        </div>
      </template>

      <template #above-track>
        <div
          class="segments-track"
          :style="{
            '--total-beats': totalBeatsForCss,
            '--beat-width': `${BEAT_WIDTH}px`
          }"
        >
          <div
            v-for="segment in harmonicSegments"
            :key="segment.key"
            class="segment-bar"
            :style="{ gridColumn: `${segment.start} / span ${segment.duration}` }"
            :class="{ 'has-local-override': segment.hasLocalOverride }"
          >
            <v-tooltip location="top" :text="segment.explanation">
              <template #activator="{ props }">
                <span v-bind="props" class="segment-label">{{ segment.label }}</span>
              </template>
            </v-tooltip>
          </div>
        </div>
      </template>

      <template #item="{ item, index }">
        <AnalysisCard
          :piano="piano"
          :item="item"
          :analysis="analysis"
          :is-substitution="isSubstitution"
          :beat-width="BEAT_WIDTH"
          @update:item="(newItem) => updateProgressionItem(index, newItem)"
        />
      </template>
    </ProgressionTimeline>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

import { BEAT_WIDTH } from '@/composables/useStatePlayer.ts'
import { useStores } from '@/composables/useStores.ts'
import { sleep } from '@/utils/time.js'
import { piano } from '@/utils/sampler.js'
import ProgressionTimeline from '@/components/common/ProgressionTimeline.vue'
import AnalysisCard from '@/components/analysis/AnalysisCard.vue'

const props = defineProps({
  title: { type: String, required: true },
  progressionItems: { type: Array, required: true },
  analysis: { type: Object, required: true },
  isSubstitution: { type: Boolean, default: false }
})

const emit = defineEmits(['update:progressionItems', 'play-chord'])

const { tempo: tempoStore } = useStores()
const progressionState = ref([])
const totalBeatsForCss = computed(() => {
  return displayedProgression.value.reduce((acc, chord) => acc + chord.duration, 0) || 8
})

watch(
  () => props.progressionItems,
  (newItems) => {
    progressionState.value = newItems.map((item) => ({
      ...item,
      duration: item.duration || 2,
      inversion: item.inversion || 0
    }))
  },
  { immediate: true, deep: true }
)

const displayedProgression = computed(() => {
  const baseProgression = progressionState.value.map((item, index) => {
    if (!item.segment_context) return item
    return item
  })

  let currentBeat = 1
  return baseProgression.map((chord) => {
    const start = currentBeat
    currentBeat += chord.duration
    return { ...chord, start }
  })
})

const harmonicSegments = computed(() => {
  const progression = displayedProgression.value
  if (!progression || progression.length === 0) {
    return []
  }
  const segments = []
  let currentSegment = null
  progression.forEach((item) => {
    if (!item.segment_context) return
    const segmentKey = item.segment_context.explanation

    if (currentSegment && currentSegment.key === segmentKey) {
      currentSegment.duration += item.duration
    } else {
      if (currentSegment) segments.push(currentSegment)

      currentSegment = {
        key: segmentKey,
        start: item.start,
        duration: item.duration,
        label: `${item.segment_context.tonic} ${item.segment_context.mode}`,
        explanation: item.segment_context.explanation
      }
    }
  })
  if (currentSegment) {
    segments.push(currentSegment)
  }
  return segments
})

function updateProgressionItem(index, newItem) {
  const newProgression = [...progressionState.value]
  const cleanItem = { ...newItem }
  delete cleanItem.start
  newProgression[index] = cleanItem
  progressionState.value = newProgression
  emit('update:progressionItems', newProgression)
}

const playAnalysisChordItem = async ({ item }) => {
  if (!item.chord) return
  const chordToPlay = {
    id: item.id,
    notes: item.notes,
    root: item.expected_chord_name.match(/^[A-G][#b]?/)?.[0],
    quality: item.found_quality,
    inversion: item.inversion,
    duration: item.duration
  }
  if (chordToPlay.duration > 0) {
    const chordDurationMs = chordToPlay.duration * tempoStore.beatDurationMs
    emit('play-chord', chordToPlay)
    piano.play(chordToPlay)
    await sleep(chordDurationMs)
  }
}
</script>

<style scoped>
.detailed-analysis-container {
  width: 100%;
  background-color: #2f2f2f;
  border-radius: 8px;
  padding: 1rem;
  overflow-x: auto;
}

.mode-selector-wrapper {
  flex-shrink: 0;
  min-width: 180px;
}
.mode-selector {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 6px;
  padding: 0.5rem 0.8rem;
  font-size: 1.1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
}
.mode-selector:hover {
  border-color: #777;
}
.mode-selector:focus {
  outline: none;
  border-color: #6497cc;
}
.legend {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 13px;
  color: #bdc3c7;
  flex-shrink: 0;
  flex-grow: 1;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}
.legend-square {
  width: 30px;
  height: 10px;
}
.substitution-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
  margin-bottom: 0.5rem;
}

.segments-track {
  display: grid;
  grid-template-columns: repeat(var(--total-beats, 8), var(--beat-width));
  grid-auto-rows: minmax(28px, auto);
  align-items: stretch;
  margin-bottom: 8px;
  padding: 0;
}

.segment-bar {
  background-color: rgba(100, 151, 204, 0.2);
  border: 1px solid #6497cc;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 8px;
  font-size: 13px;
  font-weight: 500;
  color: #cde1f7;
  overflow: hidden;
  cursor: pointer;
  transition: background-color 0.2s ease;
}

.segment-bar:hover {
  background-color: rgba(100, 151, 204, 0.4);
}

.segment-bar.has-local-override {
  border-color: #f1c40f;
  box-shadow: 0 0 5px rgba(241, 196, 15, 0.5);
}

.mode-selector-wrapper.with-icon {
  position: relative;
  display: flex;
  align-items: center;
}

.mode-selection-list {
  background-color: #2c2c2c !important;
  color: #edf2f4 !important;
  border: 1px solid #555;
  border-radius: 6px;
  max-height: 250px;
  overflow-y: auto;
}

.mode-selection-list .v-list-item-title {
  color: #edf2f4 !important;
  opacity: 1 !important;
  font-size: 0.9rem;
}

.mode-selection-list .list-item-reset .v-list-item-title {
  color: #f1c40f !important;
  font-weight: bold;
}

.mode-selection-list .v-list-item:hover {
  background-color: #6497cc !important;
}

.mode-selector {
  -webkit-appearance: none;
  -moz-appearance: none;
  appearance: none;
  padding-right: 2.5rem;
}

.selector-icon {
  position: absolute;
  right: 0.5rem;
  pointer-events: none;
  opacity: 0.7;
}

.is-playing-halo .analysis-card {
  box-shadow: 0 0 20px 5px rgba(253, 203, 110, 0.7);
  border-radius: 12px;
}
</style>
