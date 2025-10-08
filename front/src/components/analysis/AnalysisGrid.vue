<template>
  <div class="detailed-analysis-container">
    <ProgressionTimeline
      :items="displayedProgression"
      :play-callback="handlePlayItemAnalysis"
      :draggable="false"
    >
      <template #header>
        <div class="substitution-header">
          <div v-if="!isSubstitution" class="mode-selector-wrapper with-icon">
            <v-menu location="bottom">
              <template #activator="{ props }">
                <div class="mode-selector" v-bind="props">
                  <span>{{ globalModeLabel }}</span>
                  <v-icon icon="mdi-chevron-down" class="selector-icon"></v-icon>
                </div>
              </template>
              <v-list dense class="mode-selection-list">
                <v-list-item @click="selectedMode = null" class="list-item-reset">
                  <v-list-item-title>Progression d'origine</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-for="mode in availableModes"
                  :key="mode"
                  @click="selectedMode = mode"
                >
                  <v-list-item-title>{{ mode }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
          </div>
          <div v-if="!isSubstitution" class="legend">
            <div class="legend-item">
              <div class="legend-dot" style="background-color: #2ecc71"></div>
              <span>Diatonique</span>
            </div>
            <div class="legend-item">
              <div class="legend-dot" style="background-color: #f1c40f"></div>
              <span>Emprunts</span>
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
            <v-menu activator="parent" location="bottom">
              <v-list dense class="mode-selection-list">
                <v-list-item @click="updateSegmentMode(segment.key, null)" class="list-item-reset">
                  <v-list-item-title>Mode d'origine</v-list-item-title>
                </v-list-item>
                <v-list-item
                  v-for="mode in availableModes"
                  :key="mode"
                  @click="updateSegmentMode(segment.key, mode)"
                >
                  <v-list-item-title>{{ mode }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>

            <v-tooltip location="top" :text="segment.explanation">
              <template #activator="{ props }">
                <span v-bind="props" class="segment-label"
                  >{{ segment.label }}
                  <v-icon icon="mdi-chevron-down" size="x-small" class="segment-icon"></v-icon
                ></span>
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

import { BEAT_WIDTH, useStatePlayer } from '@/composables/useStatePlayer.js'
import { sleep } from '@/utils.js'
import { useTempoStore } from '@/stores/tempo.js'
import ProgressionTimeline from '@/components/common/ProgressionTimeline.vue'
import AnalysisCard from '@/components/analysis/AnalysisCard.vue'

const props = defineProps({
  title: { type: String, required: true },
  progressionItems: { type: Array, required: true },
  analysis: { type: Object, required: true },
  piano: { type: Object, required: true },
  isSubstitution: { type: Boolean, default: false }
})

const emit = defineEmits(['update:progressionItems'])

const tempoStore = useTempoStore()
const selectedMode = ref(null)
const segmentModes = ref({})
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

const globalModeLabel = computed(() => {
  return selectedMode.value || "Progression d'origine"
})

const availableModes = computed(() => Object.keys(props.analysis.result.harmonized_chords))

const displayedProgression = computed(() => {
  const baseProgression = progressionState.value.map((item, index) => {
    if (!item.segment_context) return item

    const segmentKey = item.segment_context.explanation

    const substitutionMode = segmentModes.value[segmentKey] || selectedMode.value

    if (substitutionMode) {
      const newModeChords = props.analysis.result.harmonized_chords[substitutionMode]
      const newChordData = newModeChords ? newModeChords[index] : null

      if (newChordData) {
        return {
          ...item,
          ...newChordData
        }
      }
    }
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

      const localMode = segmentModes.value[segmentKey]
      const globalMode = selectedMode.value
      const originalMode = item.segment_context.mode

      const modeForLabel = localMode || globalMode || originalMode

      currentSegment = {
        key: segmentKey,
        start: item.start,
        duration: item.duration,
        label: `${item.segment_context.tonic} ${modeForLabel}`,
        explanation: item.segment_context.explanation,
        hasLocalOverride: !!localMode
      }
    }
  })
  if (currentSegment) {
    segments.push(currentSegment)
  }
  return segments
})

function updateSegmentMode(segmentKey, mode) {
  if (mode) {
    segmentModes.value[segmentKey] = mode
  } else {
    delete segmentModes.value[segmentKey]
  }
}

function updateProgressionItem(index, newItem) {
  const newProgression = [...progressionState.value]
  const cleanItem = { ...newItem }
  delete cleanItem.start
  newProgression[index] = cleanItem
  progressionState.value = newProgression
  emit('update:progressionItems', newProgression)
}

const handlePlayItemAnalysis = async ({ item }) => {
  if (!item.chord) return
  let chordDurationMs = item.duration * tempoStore.beatDurationMs
  if (item && chordDurationMs > 0) {
    props.piano.play(item)
    await sleep(chordDurationMs)
  }
}
</script>

<style scoped>
.detailed-analysis-container {
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
  margin-bottom: 8px; /* Espace entre les segments et les accords */
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
