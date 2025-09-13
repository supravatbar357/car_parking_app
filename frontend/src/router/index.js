import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/components/HomeView.vue'
import LoginView from '@/components/LoginView.vue'
import RegisterView from '@/components/RegisterView.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import UserDashboard from '@/components/UserDashboard.vue'
import AddParkinglots from '@/components/AddParkinglots.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },

    // Admin Dashboard
    { 
      path: '/admindashboard',
      name: 'AdminDashboard', 
      component: AdminDashboard, 
      meta: { requiresAuth: true, adminOnly: true }
    },
    { 
      path: '/admindashboard/add-parking-lot',
      name: 'AddParkinglots', 
      component: AddParkinglots,
      meta: { requiresAuth: true, adminOnly: true }
    },

    // User Dashboard
    { 
      path: '/user',
      name: 'UserDashboard', 
      component: UserDashboard,
      meta: { requiresAuth: true }
    },
  ],
})

// Navigation guards
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const user = JSON.parse(localStorage.getItem('user') || '{}')

  if (to.meta.requiresAuth && !token) {
    return next('/login')
  }

  if (to.meta.adminOnly && !user.is_admin) {
    return next('/user')
  }

  next()
})

export default router
