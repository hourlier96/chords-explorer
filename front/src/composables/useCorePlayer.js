import { ref } from 'vue'
import * as Tone from 'tone'
import { metronome } from '@/metronome.js'

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

  const stopFlag = ref(false)

  const stop = () => {
    if (!isPlaying.value) return
    stopFlag.value = true
  }

  /**
   * La fonction play accepte maintenant des options pour démarrer à un endroit précis.
   */
  const play = async (options = {}) => {
    if (isPlaying.value) return
    if (Tone.getContext().state !== 'running') {
      await Tone.start()
    }

    let currentOptions = { ...options }
    stopFlag.value = false
    isPlaying.value = true

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
          if (stopFlag.value) break

          const item = progression.value[i]
          if (!item || !item.duration) continue

          currentlyPlayingIndex.value = i

          const isFirstItemInLoop = i === startIndex
          const currentOffset = isFirstItemInLoop ? startOffsetBeats : 0

          if (isMetronomeActive.value && !stopFlag.value) {
            const beatDurationSec = tempoStore.beatDurationMs / 1000
            for (
              let localBeat = Math.floor(currentOffset);
              localBeat < item.duration;
              localBeat++
            ) {
              if (stopFlag.value) break
              const time = Tone.now() + (localBeat - currentOffset) * beatDurationSec
              metronome.click(Math.floor(globalBeatCounter), beatsPerMeasure.value, time)
              globalBeatCounter++
            }
          }

          if (!stopFlag.value) {
            await onPlayItemAsync({
              item,
              index: i,
              startOffsetBeats: currentOffset
            })
          }
        }

        if (isLooping.value && !stopFlag.value) {
          currentOptions = { startIndex: 0, startOffsetBeats: 0 }
        }
      } while (isLooping.value && !stopFlag.value)
    } catch (error) {
      console.error('Erreur durant la lecture :', error)
    } finally {
      // Nettoyage final
      isPlaying.value = false
      currentlyPlayingIndex.value = -1
      if (onStop) {
        onStop()
      }
    }
  }

  return { isPlaying, currentlyPlayingIndex, play, stop }
}
