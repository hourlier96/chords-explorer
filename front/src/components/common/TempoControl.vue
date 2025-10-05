<template>
  <div class="tempo-control">
    <label for="bpm-input">BPM</label>
    <input
      id="bpm-input"
      type="number"
      v-model.number="tempoStore.bpm"
      min="20"
      max="300"
      class="tempo-input"
    />
  </div>
</template>

<script setup>
import { useTempoStore } from '@/stores/tempo.js'

const tempoStore = useTempoStore()
</script>

<style scoped>
.tempo-control {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  background-color: #252525;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  border: 1px solid #444;
}
.tempo-control label {
  font-weight: 500;
  color: #bbb;
}
.tempo-input {
  width: 60px;
  background-color: #3c3c3c;
  border: 1px solid #555;
  color: white;
  border-radius: 6px;
  padding: 0.4rem;
  text-align: center;
  font-size: 1rem;
}
/* Cache les flèches sur l'input de type number */
.tempo-input::-webkit-outer-spin-button,
.tempo-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.tempo-input[type='number'] {
  -moz-appearance: textfield;
  appearance: textfield;
}
</style>
