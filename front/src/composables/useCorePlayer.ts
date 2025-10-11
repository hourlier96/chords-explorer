import { ref } from 'vue'
import * as Tone from 'tone'
import { metronome } from '@/utils/metronome.js'

/**
 * Le cœur du lecteur audio, gère la boucle de lecture et l'état.
 */
export function useCorePlayer({
  progression,
  tempoStore,
  isLooping,
  isMetronomeActive,
  beatsPerMeasure,
  onPlayItemAsync,
  onStart,
  onStop
}) {
  const isPlaying = ref(false)
  const currentlyPlayingIndex = ref(-1)

  // On garde une référence au contrôleur d'annulation
  let abortController = null

  const stop = () => {
    if (!isPlaying.value) return
    // On signale l'annulation. Ceci va déclencher l'événement 'abort' sur le signal.
    abortController?.abort()
  }

  const play = async (options = {}) => {
    if (isPlaying.value) return
    if (Tone.getContext().state !== 'running') {
      await Tone.start()
    }

    // Création d'un nouveau contrôleur pour cette session de lecture
    abortController = new AbortController()

    // On utilise le signal pour savoir quand arrêter la boucle principale
    abortController.signal.addEventListener('abort', () => {
      isPlaying.value = false
      currentlyPlayingIndex.value = -1
      if (onStop) {
        onStop()
      }
    })

    isPlaying.value = true
    let currentOptions = { ...options }

    try {
      do {
        const { startIndex = 0, startOffsetBeats = 0 } = currentOptions
        const beatsBefore = progression.value
          .slice(0, startIndex)
          .reduce((sum, chord) => sum + chord.duration, 0)
        const absoluteStartBeat = beatsBefore + startOffsetBeats

        if (onStart) {
          onStart(absoluteStartBeat)
        }

        let globalBeatCounter = absoluteStartBeat

        for (let i = startIndex; i < progression.value.length; i++) {
          // La boucle s'arrête si le signal a été "aborted"
          if (abortController.signal.aborted) break

          const item = progression.value[i]
          if (!item || !item.duration) continue

          currentlyPlayingIndex.value = i
          const isFirstItemInLoop = i === startIndex
          const currentOffset = isFirstItemInLoop ? startOffsetBeats : 0

          if (isMetronomeActive.value && !abortController.signal.aborted) {
            const beatDurationSec = tempoStore.beatDurationMs / 1000
            for (
              let localBeat = Math.floor(currentOffset);
              localBeat < item.duration;
              localBeat++
            ) {
              if (abortController.signal.aborted) break
              const time = Tone.now() + (localBeat - currentOffset) * beatDurationSec
              metronome.click(Math.floor(globalBeatCounter), beatsPerMeasure.value, time)
              globalBeatCounter++
            }
          }

          if (!abortController.signal.aborted) {
            await onPlayItemAsync({
              item,
              index: i,
              startOffsetBeats: currentOffset,
              signal: abortController.signal
            })
          }
        }

        if (isLooping.value && !abortController.signal.aborted) {
          currentOptions = { startIndex: 0, startOffsetBeats: 0 }
        }
      } while (isLooping.value && !abortController.signal.aborted)
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('Erreur durant la lecture :', error)
      }
    } finally {
      if (!abortController.signal.aborted) {
        isPlaying.value = false
        currentlyPlayingIndex.value = -1
        if (onStop) onStop()
      }
    }
  }

  return { isPlaying, currentlyPlayingIndex, play, stop }
}
