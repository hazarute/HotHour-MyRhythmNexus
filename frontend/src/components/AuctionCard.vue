<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

const props = defineProps({
  auction: {
    type: Object,
    required: true
  }
})

const router = useRouter()

const formatPrice = (p) => {
  return new Intl.NumberFormat('tr-TR', { style: 'currency', currency: 'TRY' }).format(p)
}

const formattedTime = computed(() => {
  if (!props.auction.startTime) return 'Invalid Date'
  return new Date(props.auction.startTime).toLocaleString('tr-TR', { 
    hour: '2-digit', minute: '2-digit', day: 'numeric', month: 'short' 
  })
})

const goToDetail = () => {
    router.push({ name: 'auction-detail', params: { id: props.auction.id } })
}
</script>

<template>
  <div 
    class="auction-card bg-card-bg rounded-lg overflow-hidden shadow-neon transform hover:scale-105 transition-all duration-300 cursor-pointer border border-transparent hover:border-neon-blue group"
    @click="goToDetail"
  >
    <div class="h-32 bg-gray-800 relative overflow-hidden">
        <!-- Placeholder Image / Gradient -->
        <div class="absolute inset-0 bg-gradient-to-br from-gray-900 to-gray-800 flex items-center justify-center">
            <span class="text-4xl">🧘</span>
        </div>
        <div class="absolute top-2 right-2 bg-black/60 px-2 py-1 rounded text-xs font-bold font-mono tracking-widest"
             :class="auction.status === 'ACTIVE' ? 'text-green-400' : 'text-gray-400'">
            {{ auction.status }}
        </div>
    </div>
    
    <div class="p-4">
        <h3 class="text-xl font-bold mb-1 group-hover:text-neon-blue transition-colors">{{ auction.title }}</h3>
        <p class="text-sm text-gray-400 mb-4">{{ auction.instructor }} • {{ formattedTime }}</p>
        
        <div class="flex justify-between items-end mt-4">
            <div>
                <span class="text-xs text-gray-500 block">Current Price</span>
                <span class="text-2xl font-bold font-mono text-white">{{ formatPrice(auction.currentPrice) }}</span>
            </div>
             <button class="bg-neon-blue text-black px-4 py-2 rounded font-bold text-sm transform transition-transform active:scale-95 group-hover:bg-cyan-300">
                VIEW
            </button>
        </div>
    </div>
  </div>
</template>

<style scoped>
.shadow-neon:hover {
    box-shadow: 0 0 15px rgba(0, 243, 255, 0.2);
}
</style>
