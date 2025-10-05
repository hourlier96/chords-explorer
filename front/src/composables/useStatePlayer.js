// Fichier : src/composables/useStatePlayer.js

import { ref, computed, watch } from 'vue'
import * as Tone from 'tone'
import { useCorePlayer } from '@/composables/useCorePlayer.js'
import { useTempoStore } from '@/stores/tempo.js'

export const BEAT_WIDTH = 70

export function useStatePlayer(progressionSource, { onPlayItemAsync, piano }) {
  const tempoStore = useTempoStore()

  const timeSignature = ref('4/4')
  const isMetronomeActive = ref(true)
  const isLooping = ref(true)

  const playheadPosition = ref(0)
  const animationFrameId = ref(null)

  const seekStartBeat = ref(0)

  const beatsPerMeasure = computed(() => parseInt(timeSignature.value.split('/')[0], 10))

  const totalBeats = computed(() => {
    const progressionDuration = progressionSource.value.reduce(
      (sum, chord) => sum + (chord.duration || 0),
      0
    )
    if (progressionDuration === 0) return beatsPerMeasure.value
    const totalWithMargin = progressionDuration + (progressionSource.value.length > 0 ? 4 : 0)
    return Math.ceil(totalWithMargin / beatsPerMeasure.value) * beatsPerMeasure.value
  })

  const startAnimation = (startBeat = 0) => {
    const playbackStartTime = Tone.now()
    const animatePlayhead = () => {
      if (!isPlaying.value) return
      const elapsedTimeMs = (Tone.now() - playbackStartTime) * 1000
      const elapsedBeats = elapsedTimeMs / tempoStore.beatDurationMs
      playheadPosition.value = (startBeat + elapsedBeats) * BEAT_WIDTH
      animationFrameId.value = requestAnimationFrame(animatePlayhead)
    }
    if (animationFrameId.value) cancelAnimationFrame(animationFrameId.value)
    animatePlayhead()
  }

  const stopAnimation = () => {
    if (animationFrameId.value) {
      cancelAnimationFrame(animationFrameId.value)
      animationFrameId.value = null
    }
  }

  const {
    isPlaying,
    currentlyPlayingIndex,
    play: corePlay,
    stop: coreStop
  } = useCorePlayer({
    progression: progressionSource,
    tempoStore,
    isLooping,
    isMetronomeActive,
    beatsPerMeasure,
    onPlayItemAsync,
    onStart: startAnimation,
    onStop: () => {
      stopAnimation()
      piano?.releaseAll()
    }
  })

  const playWrapper = () => {
    if (isPlaying.value) return

    // Calculer l'index et l'offset à partir de la position mémorisée
    let startIndex = 0
    let startOffsetBeats = 0
    let beatsBefore = 0

    for (const [index, chord] of progressionSource.value.entries()) {
      if (
        seekStartBeat.value >= beatsBefore &&
        seekStartBeat.value < beatsBefore + chord.duration
      ) {
        startIndex = index
        startOffsetBeats = seekStartBeat.value - beatsBefore
        break
      }
      beatsBefore += chord.duration
    }

    corePlay({ startIndex, startOffsetBeats })
  }

  const stopWrapper = () => {
    coreStop()
    seekStartBeat.value = 0
    playheadPosition.value = 0
  }

  const seek = (targetBeat) => {
    if (isPlaying.value) return
    playheadPosition.value = targetBeat * BEAT_WIDTH
    seekStartBeat.value = targetBeat
  }

  watch(currentlyPlayingIndex, (newIndex, oldIndex) => {
    if (newIndex === 0 && oldIndex > newIndex) {
      seekStartBeat.value = 0 // Réinitialiser pour la boucle
      startAnimation(0)
    }
  })

  return {
    BEAT_WIDTH,
    playheadPosition,
    beatsPerMeasure,
    totalBeats,
    isPlaying,
    currentlyPlayingIndex,
    timeSignature,
    isMetronomeActive,
    isLooping,
    playEntireProgression: playWrapper,
    stopSound: stopWrapper,
    seek
  }
}
