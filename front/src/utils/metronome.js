import * as Tone from "tone";

// Crée deux synthétiseurs pour les deux sons différents du métronome.
// Un son plus grave pour le premier temps (le "downbeat").
const strongBeatSynth = new Tone.MembraneSynth({
  pitchDecay: 0.005,
  octaves: 10,
  oscillator: { type: "sine" },
  envelope: { attack: 0.001, decay: 0.15, sustain: 0.01, release: 0.05 },
}).toDestination();
strongBeatSynth.volume.value = -2; // Un peu plus fort

// Un son plus aigu pour les autres temps (les "upbeats").
const weakBeatSynth = new Tone.MembraneSynth({
  pitchDecay: 0.01,
  octaves: 4,
  oscillator: { type: "sine" },
  envelope: { attack: 0.001, decay: 0.1, sustain: 0, release: 0.05 },
}).toDestination();
weakBeatSynth.volume.value = -12; // Moins fort

/**
 * Joue un son de métronome.
 * Détermine s'il faut jouer un temps fort ou un temps faible.
 * @param {number} beatIndex - L'index du temps actuel dans la boucle (commence à 0).
 * @param {number} beatsPerMeasure - Le nombre de temps par mesure (ex: 3, 4).
 * @param {number} time - L'heure précise (Tone.Time) à laquelle le son doit être joué.
 */
function click(beatIndex, beatsPerMeasure, time) {
  if (beatIndex % beatsPerMeasure === 0) {
    strongBeatSynth.triggerAttackRelease("C2", "8n", time);
  } else {
    weakBeatSynth.triggerAttackRelease("G2", "8n", time);
  }
}

export const metronome = {
  click,
};
