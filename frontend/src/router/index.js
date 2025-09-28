import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/components/HomeView.vue'
import LoginView from '@/components/LoginView.vue'
import RegisterView from '@/components/RegisterView.vue'
import AdminDashboard from '@/components/AdminDashboard.vue'
import UserDashboard from '@/components/UserDashboard.vue'
import AddParkinglots from '@/components/AddParkinglots.vue'
import EditParkinglots from '@/components/EditParkinglots.vue'
import ReservationForm from '@/components/ReservationForm.vue'
import ProfileView from '@/components/ProfileView.vue' 
import AboutView from '@/components/AboutView.vue'
import ReleaseForm from '@/components/ReleaseForm.vue'
import UserSummary from '@/components/charts/UserSummary.vue'
import AdminSummary from '@/components/charts/AdminSummary.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/Home' },
    { path: '/Home', name: 'Home', component: HomeView },
    { path: '/about', name: 'About', component: AboutView },

    // Auth
    { path: '/login', name: 'login', component: LoginView },
    { path: '/register', name: 'register', component: RegisterView },

    // Profile
    {
      path: '/profile',
      name: 'Profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },

    // Admin Dashboard with nested Summary
    { 
      path: '/admindashboard',
      component: AdminDashboard,
      meta: { requiresAuth: true, adminOnly: true },
      children: [
        { path: '', name: 'AdminHome', component: AdminDashboard },
        { path: 'summary', name: 'AdminSummary', component: AdminDashboard }
      ]
    },
    { 
      path: '/admindashboard/add-parking-lot',
      name: 'AddParkinglots', 
      component: AddParkinglots,
      meta: { requiresAuth: true, adminOnly: true }
    },
    { 
      path: '/admindashboard/edit-parking-lot/:id',
      name: 'EditParkinglots', 
      component: EditParkinglots,
      meta: { requiresAuth: true, adminOnly: true }
    },

    // User Dashboard with nested Summary
    { 
      path: '/userdashboard',
      component: UserDashboard,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'UserHome', component: UserDashboard },
        { path: 'summary', name: 'UserSummary', component: UserDashboard }
      ]
    },

    // Reservation and Release
    { 
      path: '/reservation/:lotId',
      name: 'ReservationForm',
      component: ReservationForm,
      props: true,
      meta: { requiresAuth: true }
    },
    { 
      path: '/release/:id',
      name: 'ReleaseForm',
      component: ReleaseForm,
      props: true,
      meta: { requiresAuth: true }
    },
    {
     path: "/user/summary",
     name: "UserSummary",
     component: UserSummary,
     meta: { requiresAuth: true }
    },
    {
     path: "/admin/summary",
     name: "AdminSummary",
     component: AdminSummary,
     meta: { requiresAuth: true, adminOnly: true }
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
    return next('/userdashboard')
  }

  next()
})

export default router
