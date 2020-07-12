import Vue from 'vue'
import VueRouter from 'vue-router'
import Home from '../views/Home.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    children: [
      {
        path: 'new',
        name: 'NewDevice',
        component: () => import(/* webpackChunkName: "newDevice" */ '../views/NewDevice.vue')
      }
    ]
  },
  {
    path: '/devices/:id',
    name: 'EditDevice',
    component: () => import(/* webpackChunkName: "editDevice" */ '../views/EditDevice.vue'),
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
