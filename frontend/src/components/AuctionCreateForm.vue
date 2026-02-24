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
    <div class="space-y-5">
        <div>
            <p class="text-neon-blue text-xs uppercase tracking-widest mb-2">Create Auction</p>
            <h3 class="text-2xl font-bold text-white">New Session Setup</h3>
            <p class="text-slate-400 text-sm mt-1">Configure timeline, pricing, and turbo behavior for this session.</p>
        </div>

        <form @submit.prevent="submitForm" class="space-y-5">
            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Basic Info</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Title</label>
                        <input
                            v-model="form.title"
                            type="text"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                            placeholder="Ex: Morning Pilates @ 10:00"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Description</label>
                        <input
                            v-model="form.description"
                            type="text"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                            placeholder="Optional details..."
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Schedule</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Start Time</label>
                        <input
                            v-model="form.start_time"
                            type="datetime-local"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">End Time</label>
                        <input
                            v-model="form.end_time"
                            type="datetime-local"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Pricing Engine</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Start Price (TL)</label>
                        <input
                            v-model.number="form.start_price"
                            type="number"
                            min="0"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Floor Price (TL)</label>
                        <input
                            v-model.number="form.floor_price"
                            type="number"
                            min="0"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Drop Interval (Min)</label>
                        <input
                            v-model.number="form.drop_interval_mins"
                            type="number"
                            min="1"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Drop Amount (TL)</label>
                        <input
                            v-model.number="form.drop_amount"
                            type="number"
                            min="1"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <div class="flex items-center justify-between gap-3">
                    <div>
                        <h4 class="text-white font-semibold">Turbo Mode</h4>
                        <p class="text-xs text-slate-400">Accelerate price drops near session end.</p>
                    </div>
                    <label for="turbo-toggle" class="inline-flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                        <input
                            v-model="form.turbo_enabled"
                            type="checkbox"
                            id="turbo-toggle"
                            class="w-5 h-5 rounded bg-dark-bg border-slate-600"
                        />
                        Enable
                    </label>
                </div>

                <div v-if="form.turbo_enabled" class="p-4 border border-neon-magenta/40 rounded-lg bg-neon-magenta/10 space-y-4">
                    <h5 class="text-neon-magenta font-semibold text-xs uppercase tracking-wider">Turbo Configuration</h5>
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div class="space-y-1">
                            <label class="block text-xs text-slate-300">Trigger (Mins Before End)</label>
                            <input
                                v-model.number="form.turbo_trigger_mins"
                                type="number"
                                min="1"
                                class="w-full bg-dark-bg/70 border border-slate-600 rounded-lg px-2.5 py-2 text-white"
                            />
                        </div>
                        <div class="space-y-1">
                            <label class="block text-xs text-slate-300">Turbo Interval (Min)</label>
                            <input
                                v-model.number="form.turbo_interval_mins"
                                type="number"
                                min="1"
                                class="w-full bg-dark-bg/70 border border-slate-600 rounded-lg px-2.5 py-2 text-white"
                            />
                        </div>
                        <div class="space-y-1">
                            <label class="block text-xs text-slate-300">Turbo Drop Amount (TL)</label>
                            <input
                                v-model.number="form.turbo_drop_amount"
                                type="number"
                                min="1"
                                class="w-full bg-dark-bg/70 border border-slate-600 rounded-lg px-2.5 py-2 text-white"
                            />
                        </div>
                    </div>
                </div>
            </div>

            <button type="submit" :disabled="loading" class="w-full hh-btn-primary py-3 disabled:opacity-50 disabled:cursor-not-allowed">
                <span v-if="loading">Creating...</span>
                <span v-else>Create Auction Session</span>
            </button>
        </form>
    </div>
</template>
