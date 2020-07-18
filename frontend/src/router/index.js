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
    children: [
      {
        path: 'edit',
        name: 'EditDeviceInfo',
        component: () => import(/* webpackChunkName: "editDeviceInfo" */ '../views/EditDeviceInfo.vue')
      },
      {
        path: 'scenes/new',
        name: 'DeviceNewScene',
        component: () => import(/* webpackChunkName: "newScene" */ '../views/NewScene.vue')
      }
    ]
  },
  {
    path: '/scenes',
    name: 'Scenes',
    component: () => import(/* webpackChunkName: "scenes" */ '../views/Scenes.vue'),
    children: [
      {
        path: 'new',
        name: 'NewScene',
        component: () => import(/* webpackChunkName: "newScene" */ '../views/NewScene.vue')
      }
    ]
  },
  {
    path: '/scenes/:scene',
    name: 'EditScene',
    component: () => import(/* webpackChunkName: "editScene" */ '../views/EditScene.vue'),
  },
  {
    path: '/devices/:device/scenes/:scene',
    name: 'DeviceEditScene',
    component: () => import(/* webpackChunkName: "editScene" */ '../views/EditScene.vue'),
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router
