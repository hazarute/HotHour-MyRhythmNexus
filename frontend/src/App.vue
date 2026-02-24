<script setup>
</script>

<template>
  <div class="app-container font-sans text-white min-h-screen bg-dark-bg">
    <header class="p-4 flex justify-between items-center border-b border-gray-800 bg-card-bg">
      <router-link to="/" class="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neon-blue to-neon-pink">
        HotHour
      </router-link>
      <nav class="space-x-4">
        <router-link to="/" class="hover:text-neon-blue transition-colors">Home</router-link>
        <router-link to="/admin" class="hover:text-neon-pink transition-colors">Admin</router-link>
      </nav>
    </header>

    <main class="container mx-auto py-8 px-4">
      <RouterView />
    </main>
  </div>
</template>

<style>
/* Global styles can go here or in style.css */
</style>
