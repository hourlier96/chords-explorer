import { reactive, toRefs, onUnmounted } from "vue";
import { WebMidi } from "webmidi";
import * as Tone from "tone";
import { piano } from "@/utils/sampler.js";

export interface MidiCallbacks {
  onNoteOn?: (note: any) => void;
  onNoteOff?: (note: any) => void;
}

export function useMidiInput() {
  const state = reactive({
    isEnabled: false,
    liveMidiNotes: new Set(),
  });

  // Le reste des variables non-réactives
  let activeInput = null;
  let isSustainPedalDown = false;
  const sustainedNotes = new Set();

  async function enableMidi(callbacks: MidiCallbacks = {}) {
    if (state.isEnabled) return;
    try {
      await WebMidi.enable();
      console.log("WebMidi enabled!");

      if (WebMidi.inputs.length < 1) {
        console.error("Aucun appareil d'entrée MIDI trouvé.");
        return;
      }

      activeInput = WebMidi.inputs[0];
      console.log(`Écoute sur : ${activeInput.name}`);

      activeInput.addListener("noteon", (e) => {
        const newNotes = new Set(state.liveMidiNotes);
        newNotes.add(e.note.identifier);
        state.liveMidiNotes = newNotes;

        sustainedNotes.delete(e.note.identifier);
        piano.triggerAttack(e.note.identifier, Tone.now(), e.velocity);
        callbacks.onNoteOn?.(e.note);
      });

      activeInput.addListener("controlchange", (e) => {
        if (e.controller.number === 64) {
          isSustainPedalDown = e.value >= 0.5;
          if (!isSustainPedalDown && sustainedNotes.size > 0) {
            piano.triggerRelease(Array.from(sustainedNotes), Tone.now());
            sustainedNotes.clear();
          }
        }
      });

      activeInput.addListener("noteoff", (e) => {
        if (isSustainPedalDown) {
          sustainedNotes.add(e.note.identifier);
        } else {
          piano.triggerRelease(e.note.identifier, Tone.now());
        }
        const newNotes = new Set(state.liveMidiNotes);
        newNotes.delete(e.note.identifier);
        state.liveMidiNotes = newNotes;
        callbacks.onNoteOff?.(e.note);
      });

      state.isEnabled = true;
    } catch (err) {
      console.error("Could not enable WebMidi.", err);
    }
  }

  function disableMidi() {
    if (!state.isEnabled || !activeInput) return;
    activeInput.removeListener();
    WebMidi.disable();
    activeInput = null;
    state.isEnabled = false;
    piano.releaseAll();
    console.log("WebMidi disabled.");
  }

  onUnmounted(disableMidi);

  // 3. On utilise toRefs pour que les propriétés puissent être déstructurées
  // tout en restant réactives dans le composant qui les utilise.
  return {
    ...toRefs(state),
    enableMidi,
    disableMidi,
  };
}
