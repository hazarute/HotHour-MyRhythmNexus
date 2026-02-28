import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/SignUpView.vue')
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: () => import('../views/VerifyEmailView.vue')
    },
    {
      path: '/auction/:id',
      name: 'auction-detail',
      component: () => import('../views/AuctionDetailView.vue'),
      props: true
    },
    {
      path: '/auctions',
      name: 'all-auctions',
      component: () => import('../views/AllAuctionsView.vue')
    },
    {
      path: '/all-auctions',
      redirect: '/auctions'
    },
    {
      path: '/how-it-works',
      name: 'how-it-works',
      component: () => import('../views/HowItWorksView.vue')
    },
    {
      path: '/terms-of-use',
      name: 'terms-of-use',
      component: () => import('../views/TermsOfUseView.vue')
    },
    {
      path: '/my-reservations',
      name: 'my-reservations',
      component: () => import('../views/MyReservationsView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('../views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/admin/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '', // Default to dashboard
          name: 'admin-dashboard',
          component: () => import('../views/admin/AdminDashboardView.vue')
        },
        {
          path: 'auctions/create',
          name: 'admin-auction-create',
          component: () => import('../views/admin/AdminAuctionFormView.vue')
        },
        {
          path: 'auctions/:id/edit',
          name: 'admin-auction-edit',
          component: () => import('../views/admin/AdminAuctionFormView.vue')
        },
        {
          path: 'reservations',
          name: 'admin-reservations',
          component: () => import('../views/admin/AdminReservationsView.vue')
        },
        {
          path: 'reservations/:id',
          name: 'admin-reservation-detail',
          component: () => import('../views/admin/AdminReservationDetailView.vue')
        },
        {
          path: 'auctions/:id',
          name: 'admin-auction-detail',
          component: () => import('../views/admin/AdminAuctionDetailView.vue')
        }
      ]
    }
  ]
})

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  // Check auth requirement
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
  } 
  // Check admin role requirement
  else if (to.meta.requiresAdmin && !authStore.isAdmin) {
    // If logged in but not admin, redirect home (or 403 page)
    next({ name: 'home' })
  }
  else {
    next()
  }
})

export default router
