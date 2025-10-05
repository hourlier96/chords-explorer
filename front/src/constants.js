export const NOTES = [
  'C',
  'C# / Db',
  'D',
  'D# / Eb',
  'E',
  'F',
  'F# / Gb',
  'G',
  'G# / Ab',
  'A',
  'A# / Bb',
  'B'
]
export const NOTES_FLAT = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
export const ENHARMONIC_EQUIVALENTS = {
  'C#': 'Db',
  'D#': 'Eb',
  'F#': 'Gb',
  'G#': 'Ab',
  'A#': 'Bb',
  Db: 'C#',
  Eb: 'D#',
  Gb: 'F#',
  Ab: 'G#',
  Bb: 'A#'
}
export const QUALITIES = [
  {
    label: 'Majeurs',
    options: [
      { value: '', text: 'Majeur' },
      { value: '6', text: 'Majeur 6' },
      { value: 'add9', text: 'Add 9' },
      { value: '6/9', text: 'Majeur 6/9' },
      { value: 'maj7', text: 'Majeur 7' },
      { value: 'maj9', text: 'Majeur 9' },
      { value: 'maj13', text: 'Majeur 13' },
      { value: 'maj7#5', text: 'Majeur 7#5' }, // Augmented Major
      { value: 'maj7b5', text: 'Majeur 7b5' }, // Lydian dominant related
      { value: 'maj7#11', text: 'Majeur 7#11' } // Lydian related
    ]
  },
  {
    label: 'Mineurs',
    options: [
      { value: 'm', text: 'Mineur' },
      { value: 'm6', text: 'Mineur 6' },
      { value: 'm(add9)', text: 'm(add9)' },
      { value: 'm7', text: 'Mineur 7' },
      { value: 'm9', text: 'Mineur 9' },
      { value: 'm11', text: 'Mineur 11' },
      { value: 'm13', text: 'Mineur 13' },
      { value: 'm(maj7)', text: 'm(maj7)' }
    ]
  },
  {
    label: 'Dominantes',
    options: [
      { value: '7', text: '7' },
      { value: '9', text: '9' },
      { value: '11', text: '11' },
      { value: '13', text: '13' },
      { value: '7b5', text: '7♭5' },
      { value: '7#5', text: '7♯5' },
      { value: '7b9', text: '7♭9' },
      { value: '7#9', text: '7♯9' },
      { value: '7#11', text: '7♯11' },
      { value: '7b13', text: '7♭13' },
      { value: '13#11', text: '13♯11' }
    ]
  },
  {
    label: 'Dominantes Altérées',
    options: [
      { value: '7b9b5', text: '7♭9♭5' },
      { value: '7b9#5', text: '7♭9♯5' },
      { value: '7#9b5', text: '7♯9♭5' },
      { value: '7#9#5', text: '7♯9♯5' },
      { value: '7b9#11', text: '7♭9♯11' },
      { value: '7#9#11', text: '7♯9♯11' },
      { value: '7b9b13', text: '7♭9♭13' },
      { value: '7#9b13', text: '7♯9♭13' }
    ]
  },
  {
    label: 'Suspendus',
    options: [
      { value: 'sus2', text: 'sus2' },
      { value: 'sus4', text: 'sus4' },
      { value: '7sus2', text: '7sus2' },
      { value: '7sus4', text: '7sus4' },
      { value: '9sus4', text: '9sus4' },
      { value: '13sus4', text: '13sus4' }
    ]
  },
  {
    label: 'Diminués',
    options: [
      { value: 'dim', text: 'Diminué' },
      { value: 'dim7', text: 'Diminué 7' },
      { value: 'm7b5', text: 'm7b5' } // Half-diminished often grouped here
    ]
  },
  {
    label: 'Augmentés',
    options: [{ value: 'aug', text: 'Augmenté' }]
  },
  {
    label: 'Autres',
    options: [{ value: '5', text: 'Power Chord' }]
  }
]

export const CHORD_FORMULAS = {
  '': [0, 4, 7],
  M: [0, 4, 7],
  maj: [0, 4, 7],
  m: [0, 3, 7],
  min: [0, 3, 7],
  dim: [0, 3, 6],
  d: [0, 3, 6],
  aug: [0, 4, 8],
  '+': [0, 4, 8],
  5: [0, 7],

  sus2: [0, 2, 7],
  sus4: [0, 5, 7],
  '7sus2': [0, 2, 7, 10],
  '7sus4': [0, 5, 7, 10],
  '9sus4': [0, 5, 7, 10, 14],
  '13sus4': [0, 5, 7, 10, 14, 21],

  add9: [0, 4, 7, 14],
  'm(add9)': [0, 3, 7, 14],

  6: [0, 4, 7, 9],
  m6: [0, 3, 7, 9],
  '6/9': [0, 4, 7, 9, 14],

  7: [0, 4, 7, 10],
  maj7: [0, 4, 7, 11],
  m7: [0, 3, 7, 10],
  dim7: [0, 3, 6, 9],
  m7b5: [0, 3, 6, 10],
  'm(maj7)': [0, 3, 7, 11],
  maj7b5: [0, 4, 6, 11],
  'maj7#5': [0, 4, 8, 11],
  'maj7#11': [0, 4, 7, 11, 18],

  '7b5': [0, 4, 6, 10],
  '7#5': [0, 4, 8, 10],
  '7b9': [0, 4, 7, 10, 13],
  '7b13': [0, 4, 7, 10, 20],
  '7#9': [0, 4, 7, 10, 15],
  '7#11': [0, 4, 7, 10, 18],
  '7alt': [0, 4, 10, 13, 18],
  '7b9b5': [0, 4, 6, 10, 13],
  '7b9#5': [0, 4, 8, 10, 13],
  '7#9b5': [0, 4, 6, 10, 15],
  '7#9#5': [0, 4, 8, 10, 15],
  '7b9#9': [0, 4, 7, 10, 13, 15],
  '7b9#11': [0, 4, 7, 10, 13, 18],
  '7#9#11': [0, 4, 7, 10, 15, 18],
  '7b9b13': [0, 4, 7, 10, 13, 20],
  '7#9b13': [0, 4, 7, 10, 15, 20],
  9: [0, 4, 7, 10, 14],
  maj9: [0, 4, 7, 11, 14],
  m9: [0, 3, 7, 10, 14],
  11: [0, 4, 7, 10, 14, 17],
  m11: [0, 3, 7, 10, 14, 17],
  13: [0, 4, 7, 10, 14, 21],
  '13#11': [0, 4, 7, 10, 14, 18, 21],
  m13: [0, 3, 7, 10, 14, 21],
  maj13: [0, 4, 7, 11, 14, 21]
}
