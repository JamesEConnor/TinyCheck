import Vue from 'vue'
import VueRouter from 'vue-router'


Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'loader',
    component: () => import('../views/splash-screen.vue'),
    props: true
  },
  {
    path: '/home',
    name: 'home',
    component: () => import('../views/home.vue'),
    props: true
  },
  {
    path: '/update',
    name: 'update',
    component: () => import('../views/update.vue'),
    props: true
  },
  {
    path: '/generate-proxy',
    name: 'generate-proxy',
    component: () => import('../views/generate-proxy.vue'),
    props: true
  },
  {
    path: '/capture',
    name: 'capture',
    component: () => import('../views/capture.vue'),
    props: true
  },
  {
    path: '/save-capture',
    name: 'save-capture',
    component: () => import('../views/save-capture.vue'),
    props: true
  },
  {
    path: '/analysis',
    name: 'analysis',
    component: () => import('../views/analysis.vue'),
    props: true
  },
  {
    path: '/report',
    name: 'report',
    component: () => import('../views/report.vue'),
    props: true
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
