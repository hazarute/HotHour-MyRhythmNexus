<script setup>
import { ref, reactive } from 'vue'

const emit = defineEmits(['create-auction'])

const form = reactive({
    title: '',
    description: '',
    start_time: '', 
    end_time: '',
    start_price: 500,
    floor_price: 200,
    drop_interval_mins: 15,
    drop_amount: 50,
    turbo_enabled: false,
    turbo_trigger_mins: 60,
    turbo_interval_mins: 5,
    turbo_drop_amount: 100
})

const loading = ref(false)

const submitForm = () => {
    loading.value = true
    // Basic formatting or validation if needed
    // Emit the payload
    emit('create-auction', { ...form })
    // Reset or handle success in parent
    loading.value = false
}
</script>

<template>
    <div class="bg-card-bg p-6 rounded-lg shadow-lg border border-neon-blue/20">
        <h2 class="text-xl font-semibold mb-4 text-neon-blue">Create New Auction</h2>
        
        <form @submit.prevent="submitForm" class="space-y-4">
            <!-- Basic Info -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Title</label>
                    <input v-model="form.title" type="text" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink"
                        placeholder="Ex: Morning Pilates @ 10:00" />
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Description</label>
                    <input v-model="form.description" type="text"
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink"
                        placeholder="Optional details..." />
                </div>
            </div>

            <!-- Time Settings -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Start Time</label>
                    <input v-model="form.start_time" type="datetime-local" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">End Time</label>
                    <input v-model="form.end_time" type="datetime-local" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
            </div>

            <!-- Price Settings -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Start Price (TL)</label>
                    <input v-model.number="form.start_price" type="number" min="0" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Floor Price (TL)</label>
                    <input v-model.number="form.floor_price" type="number" min="0" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
            </div>

            <!-- Drop Logic -->
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Drop Interval (Min)</label>
                    <input v-model.number="form.drop_interval_mins" type="number" min="1" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
                <div class="space-y-2">
                    <label class="block text-sm font-medium text-gray-300">Drop Amount (TL)</label>
                    <input v-model.number="form.drop_amount" type="number" min="1" required
                        class="w-full bg-dark-bg border border-gray-600 rounded px-3 py-2 text-white focus:outline-none focus:border-neon-pink" />
                </div>
            </div>

            <!-- Turbo Mode Toggle -->
            <div class="flex items-center space-x-3 py-2">
                <input v-model="form.turbo_enabled" type="checkbox" id="turbo-toggle"
                    class="w-5 h-5 text-neon-pink rounded focus:ring-neon-pink bg-dark-bg border-gray-600" />
                <label for="turbo-toggle" class="text-white font-medium">Enable Turbo Mode?</label>
            </div>

             <!-- Turbo Settings (Conditional) -->
            <div v-if="form.turbo_enabled" class="p-4 border border-neon-pink/50 rounded bg-neon-pink/10 space-y-4">
                <h3 class="text-neon-pink font-semibold text-sm uppercase tracking-wider">Turbo Configuration</h3>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="space-y-1">
                        <label class="block text-xs text-gray-300">Trigger (Mins Before End)</label>
                        <input v-model.number="form.turbo_trigger_mins" type="number" min="1"
                            class="w-full bg-dark-bg border border-gray-600 rounded px-2 py-1 text-white" />
                    </div>
                     <div class="space-y-1">
                        <label class="block text-xs text-gray-300">Turbo Interval (Min)</label>
                        <input v-model.number="form.turbo_interval_mins" type="number" min="1"
                            class="w-full bg-dark-bg border border-gray-600 rounded px-2 py-1 text-white" />
                    </div>
                     <div class="space-y-1">
                        <label class="block text-xs text-gray-300">Turbo Drop Amount (TL)</label>
                        <input v-model.number="form.turbo_drop_amount" type="number" min="1"
                            class="w-full bg-dark-bg border border-gray-600 rounded px-2 py-1 text-white" />
                    </div>
                </div>
            </div>

            <button type="submit" :disabled="loading"
                class="w-full py-3 px-4 bg-neon-pink hover:bg-pink-600 text-white font-bold rounded shadow-neon transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
                <span v-if="loading">Creating...</span>
                <span v-else>Create Auction Session</span>
            </button>
        </form>
    </div>
</template>
