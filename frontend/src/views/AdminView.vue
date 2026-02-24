<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter, RouterLink, RouterView } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const logout = () => {
    authStore.logout()
    router.push({ name: 'home' })
}
</script>

<template>
  <div class="relative flex min-h-screen w-full flex-row overflow-hidden bg-background-light dark:bg-background-dark text-slate-900 dark:text-gray-100 font-display">
    
    <!-- Sidebar -->
    <aside class="fixed left-0 top-0 h-full w-64 border-r border-slate-200 dark:border-slate-800 bg-white dark:bg-background-dark z-20 flex flex-col justify-between p-4">
        <div class="flex flex-col gap-8">
            <!-- Logo / Brand -->
            <div class="flex items-center gap-3 px-2">
                <div class="relative flex items-center justify-center size-10 rounded-xl bg-gradient-to-br from-primary to-blue-600 shadow-lg shadow-primary/20">
                    <span class="material-symbols-outlined text-white" style="font-size: 24px;">hourglass_top</span>
                </div>
                <div class="flex flex-col">
                    <h1 class="text-slate-900 dark:text-white text-lg font-bold leading-tight tracking-tight">HotHour</h1>
                    <p class="text-slate-500 dark:text-slate-400 text-xs font-medium">Stüdyo Kontrol</p>
                </div>
            </div>

            <!-- Navigation -->
            <nav class="flex flex-col gap-2">
                <RouterLink :to="{ name: 'admin-dashboard' }" 
                   class="group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200"
                   active-class="bg-primary/10 text-primary dark:text-white dark:bg-[#232d3f] border-l-4 border-primary shadow-sm"
                   :class="[$route.name === 'admin-dashboard' || $route.name === 'admin' ? 'bg-primary/10 text-primary dark:text-white dark:bg-[#232d3f] border-l-4 border-primary shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#232d3f] hover:text-primary dark:hover:text-white', {'!bg-transparent !text-slate-600 !border-0 !shadow-none': $route.name !== 'admin-dashboard' && $route.name !== 'admin'}]">
                    <span class="material-symbols-outlined group-hover:text-primary transition-colors" style="font-size: 24px;">dashboard</span>
                    <span class="text-sm font-medium">Panel</span>
                </RouterLink>

                <RouterLink :to="{ name: 'admin-reservations' }" 
                   class="group flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-200"
                   active-class="bg-primary/10 text-primary dark:text-white dark:bg-[#232d3f] border-l-4 border-primary shadow-sm"
                   :class="[$route.name === 'admin-reservations' ? 'bg-primary/10 text-primary dark:text-white dark:bg-[#232d3f] border-l-4 border-primary shadow-sm' : 'text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#232d3f] hover:text-primary dark:hover:text-white']">
                    <span class="material-symbols-outlined group-hover:text-primary transition-colors" style="font-size: 24px;">calendar_month</span>
                    <span class="text-sm font-medium">Rezervasyonlar</span>
                </RouterLink>

                <a href="#" class="group flex items-center gap-3 px-3 py-2.5 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-[#232d3f] hover:text-primary dark:hover:text-white transition-all duration-200">
                    <span class="material-symbols-outlined group-hover:text-primary transition-colors" style="font-size: 24px;">settings</span>
                    <span class="text-sm font-medium">Ayarlar</span>
                </a>
            </nav>
        </div>

        <!-- User Profile -->
        <div class="flex items-center gap-3 px-3 py-3 rounded-xl bg-slate-50 dark:bg-[#1a2230] border border-slate-200 dark:border-slate-800">
            <div class="bg-center bg-no-repeat bg-cover rounded-full size-9 ring-2 ring-slate-200 dark:ring-slate-700" style="background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAXnMuRQFY36QcSLgusa3MwDPhOahlpgvV7-fqRP1ycZDfQt-nVJTVPIVMI8rZ2Juo-PBPsTdR5GBtm6MxOQAWbRk9C3fxKrfQoiwlgZaJmi2Ds1_z0OdSEI5pMIz-Aool-E3HE6NeFFNwoues6o9a8SMSFTiLEYPIG-WS8SYmIelhL0NwhfmoUTF4M3t_Y-2O-G5tIp6cGHWKLPPrwvE69q3kzUVlGQLnhVx2wqtiT2IzJF6gummhHRMGb--VNGXWcpTWzNMw1PN4');"></div>
            <div class="flex flex-col overflow-hidden">
                <p class="text-slate-900 dark:text-white text-sm font-semibold truncate">{{ authStore.user?.full_name || 'Yönetici' }}</p>
                <p class="text-slate-500 dark:text-slate-400 text-xs truncate">{{ authStore.user?.role || 'Sahip' }}</p>
            </div>
            <button @click="logout" class="ml-auto text-slate-400 hover:text-primary transition-colors" title="Çýkýþ Yap">
                <span class="material-symbols-outlined" style="font-size: 20px;">logout</span>
            </button>
        </div>
    </aside>

    <!-- Main Content -->
    <main class="ml-64 flex-1 flex flex-col h-full min-h-screen">
        <RouterView />
    </main>
  </div>
</template>
