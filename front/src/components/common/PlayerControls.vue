<template>
  <div class="player-controls-wrapper">
    <TempoControl />

    <div class="time-signature-selector">
      <v-tooltip location="top" text="Signature Rythmique">
        <template #activator="{ props: tooltipProps }">
          <v-icon icon="mdi-timeline-clock-outline" v-bind="tooltipProps" />
        </template>
      </v-tooltip>
      <label
        v-for="sig in ['3/4', '4/4', '5/4']"
        :key="sig"
        class="radio-label-sm"
        :class="{ active: timeSignature === sig }"
      >
        <input
          type="radio"
          name="time-signature"
          :value="sig"
          :checked="timeSignature === sig"
          @change="timeSignature = sig"
        />
        {{ sig }}
      </label>
    </div>

    <v-tooltip
      location="top"
      :text="isMetronomeActive ? 'Désactiver le métronome' : 'Activer le métronome'"
    >
      <template #activator="{ props: tooltipProps }">
        <button
          v-bind="tooltipProps"
          @click="isMetronomeActive = !isMetronomeActive"
          class="control-icon-button"
          :class="{ 'is-active': isMetronomeActive }"
        >
          <v-icon icon="mdi-metronome" />
        </button>
      </template>
    </v-tooltip>

    <v-tooltip location="top" :text="isLooping ? 'Désactiver la loop' : 'Activer la loop'">
      <template #activator="{ props: tooltipProps }">
        <button
          v-bind="tooltipProps"
          @click="isLooping = !isLooping"
          class="control-icon-button"
          :class="{ 'is-active': isLooping }"
        >
          <v-icon icon="mdi-sync" />
        </button>
      </template>
    </v-tooltip>

    <div class="d-flex ga-2">
      <v-tooltip location="top" text="Lire la progression">
        <template #activator="{ props: tooltipProps }">
          <button
            v-bind="tooltipProps"
            @click="$emit('play')"
            class="control-icon-button"
            :disabled="isPlaying"
          >
            <v-icon icon="mdi-play" />
          </button>
        </template>
      </v-tooltip>
      <v-tooltip location="top" text="Stopper la lecture">
        <template #activator="{ props: tooltipProps }">
          <button
            v-bind="tooltipProps"
            @click="$emit('stop')"
            class="control-icon-button"
            :disabled="!isPlaying"
          >
            <v-icon icon="mdi-stop" />
          </button>
        </template>
      </v-tooltip>
    </div>
  </div>
</template>

<script setup>
import TempoControl from '@/components/common/TempoControl.vue'

defineProps({
  isPlaying: { type: Boolean, required: true }
})

defineEmits(['play', 'stop'])

const timeSignature = defineModel('timeSignature', { required: true })
const isMetronomeActive = defineModel('isMetronomeActive', { required: true })
const isLooping = defineModel('isLooping', { required: true })
</script>

<style scoped>
.player-controls-wrapper {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}
.control-icon-button {
  background-color: #4a4a4a;
  color: #edf2f4;
  border: 1px solid #555;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s ease;
}
.control-icon-button:hover:not(:disabled) {
  background-color: #5a5a5a;
  border-color: #777;
}
.control-icon-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.control-icon-button.is-active {
  background-color: #6497cc;
  color: #000;
  border-color: #5078a0;
}
.time-signature-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #252525;
  border-radius: 8px;
  padding: 5px;
  border: 1px solid #444;
  color: #bbb;
}
.radio-label-sm {
  padding: 0.2rem 0.6rem;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
  color: #bbb;
  background-color: transparent;
  font-size: 0.9rem;
}
.radio-label-sm.active {
  background-color: #007bff;
  color: white;
  font-weight: 500;
}
.radio-label-sm:not(.active):hover {
  background-color: #3f3f3f;
}
.radio-label-sm input[type='radio'] {
  display: none;
}
</style>
