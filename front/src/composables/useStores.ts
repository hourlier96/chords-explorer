import { useAnalysisStore } from "@/stores/analysis.ts";
import { snackStore } from "@/stores/snackbar.ts";
import { useMidiStore } from "@/stores/midi.ts";
import { useTempoStore } from "@/stores/tempo.ts";
import { preferencesStore } from "@/stores/preferences.ts";

export function useStores() {
  const snack = snackStore();
  const midi = useMidiStore();
  const analysis = useAnalysisStore();
  const tempo = useTempoStore();
  const pref = preferencesStore();
  return { snack, midi, analysis, tempo, pref };
}
