import { createRouter, createWebHistory } from 'vue-router'
import FormView from '@/views/AdvancedExplorer.vue'
import TableView from '@/views/SimpleExplorer.vue'
import NotFound from '@/views/NotFound.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'simple',
      meta: { requiresAuth: false },
      component: TableView
    },
    {
      path: '/advanced',
      name: '',
      meta: { requiresAuth: false },
      component: FormView
    },
    { path: '/:pathMatch(.*)*', name: 'NotFound', component: NotFound }
  ]
})

export default router
