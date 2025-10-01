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
        to="/"
        prepend-icon="mdi-music-note"
        :title="$t('navigation.simple_explorer')"
        value="simplified"
      />
      <v-list-item
        to="/advanced"
        prepend-icon="mdi-music"
        :title="$t('navigation.advanced_explorer')"
        value="advanced"
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
