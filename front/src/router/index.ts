import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import AnalyzeView from '@/views/AnalyzeView.vue'
import HarmonizeView from '@/views/HarmonizeView.vue'
import ExploreView from '@/views/ExploreView.vue'
import NotFound from '@/views/NotFound.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      meta: { requiresAuth: false },
      component: HomeView
    },
    {
      path: '/analyzer',
      name: 'analyzer',
      meta: { requiresAuth: false },
      component: AnalyzeView
    },
    {
      path: '/harmonizer',
      name: 'harmonizer',
      meta: { requiresAuth: false },
      component: HarmonizeView
    },
    {
      path: '/explorer',
      name: 'explorer',
      meta: { requiresAuth: false },
      component: ExploreView
    },
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
  ]
})

export default router
