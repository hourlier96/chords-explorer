// La structure des touches que vous aviez dans PianoKeyboard.vue
export const whiteKeys = [
  // Octave 3
  { note: 'C3', blackKey: 'C#3' },
  { note: 'D3', blackKey: 'D#3' },
  { note: 'E3' },
  { note: 'F3', blackKey: 'F#3' },
  { note: 'G3', blackKey: 'G#3' },
  { note: 'A3', blackKey: 'A#3' },
  { note: 'B3' },
  // Octave 4
  { note: 'C4', blackKey: 'C#4' },
  { note: 'D4', blackKey: 'D#4' },
  { note: 'E4' },
  { note: 'F4', blackKey: 'F#4' },
  { note: 'G4', blackKey: 'G#4' },
  { note: 'A4', blackKey: 'A#4' },
  { note: 'B4' },
  // Octave 5
  { note: 'C5', blackKey: 'C#5' },
  { note: 'D5', blackKey: 'D#5' },
  { note: 'E5' },
  { note: 'F5', blackKey: 'F#5' },
  { note: 'G5', blackKey: 'G#5' },
  { note: 'A5', blackKey: 'A#5' },
  { note: 'B5' },
  // Début de l'octave 6
  { note: 'C6' }
]

// On génère un tableau de toutes les notes jouables sur ce clavier
export const ALL_PLAYABLE_NOTES = whiteKeys.reduce((acc, key) => {
  acc.push(key.note)
  if (key.blackKey) {
    acc.push(key.blackKey)
  }
  return acc
}, [])
