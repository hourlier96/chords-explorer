<template>
  <v-navigation-drawer
    id="sidebar"
    v-model="drawer"
    :rail="rail"
    :rail-width="56"
    :width="230"
    permanent
    @click="expandRail(true)"
  >
    <v-btn
      variant="text"
      :icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
      @click.stop="expandRail(!rail)"
    />
    <v-divider />
    <v-list
      density="compact"
      nav
    >
      <v-list-item
        to="/analyzer"
        prepend-icon="mdi-magnify"
        :title="$t('navigation.analyze_view')"
        value="analyze"
      />
      <v-list-item
        to="/harmonizer"
        prepend-icon="mdi-music-note-plus"
        :title="$t('navigation.harmonize_view')"
        value="harmonize"
      />
      <v-list-item
        to="/explorer"
        prepend-icon="mdi-book-open"
        :title="$t('navigation.explore_view')"
        value="explore"
      />
    </v-list>
  </v-navigation-drawer>
</template>

<script setup lang="ts">
import { nextTick, onMounted, ref } from 'vue'

let drawer = ref(true)
let rail = ref(true)

const emit = defineEmits(['expand'])

onMounted(() => {
  nextTick(() => {
    expandRail(true)
  })
})

function expandRail(expand) {
  rail.value = expand
  emit('expand', expand)
}
</script>
