import { defineStore } from "pinia";
import { defaultLocale } from "@/../i18n/index.js";
import { i18n } from "@/main.ts";

export const preferencesStore = defineStore("preferences", {
  state: () => ({
    lang: defaultLocale,
    railExpanded: false,
  }),
  actions: {
    setLang(lang) {
      this.lang = lang;
      i18n.global.locale.value = lang;
    },
    setRail(expanded) {
      this.railExpanded = expanded;
    },
  },
  persist: true,
});
