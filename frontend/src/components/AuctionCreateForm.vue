<script setup>
import { ref, reactive, watch, onMounted } from 'vue'

const props = defineProps({
    initialData: {
        type: Object,
        default: null
    },
    isEdit: {
        type: Boolean,
        default: false
    }
})

const emit = defineEmits(['create-auction', 'update-auction', 'cancel'])

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

// If initialData is provided, populate the form
onMounted(() => {
    if (props.initialData) {
        populateForm(props.initialData)
    }
})

// Watch for changes in initialData if it changes dynamically
watch(() => props.initialData, (newVal) => {
    if (newVal) {
        populateForm(newVal)
    }
}, { deep: true })

const loading = ref(false)

const formatDateForInput = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    
    // Check if date is valid
    if (isNaN(date.getTime())) return ''

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')
    
    return `${year}-${month}-${day}T${hours}:${minutes}`
}

const populateForm = (data) => {
    // Clone object to avoid mutation issues
    const newData = { ...data }
    
    // Format dates specifically
    if (newData.start_time) newData.start_time = formatDateForInput(newData.start_time)
    if (newData.end_time) newData.end_time = formatDateForInput(newData.end_time)
    
    Object.assign(form, newData)
}

// If initialData is provided, populate the form
onMounted(() => {
    if (props.initialData) {
        populateForm(props.initialData)
    }
})

const submitForm = () => {
    loading.value = true
    
    // Create copy of form data
    const payload = { ...form }
    
    // Convert local time strings back to ISO if they are in 'YYYY-MM-DDTHH:mm' format
    if (payload.start_time && payload.start_time.length === 16) {
        const d = new Date(payload.start_time)
        if (!isNaN(d.getTime())) {
             payload.start_time = d.toISOString()
        }
    }
    
    if (payload.end_time && payload.end_time.length === 16) {
        const d = new Date(payload.end_time)
        if (!isNaN(d.getTime())) {
             payload.end_time = d.toISOString()
        }
    }

    if (props.isEdit) {
        emit('update-auction', { ...payload, id: props.initialData.id })
    } else {
        emit('create-auction', { ...payload })
    }
    loading.value = false
}
</script>

<template>
    <div class="space-y-5">
        <div>
            <p class="text-neon-blue text-xs uppercase tracking-widest mb-2">Oturum Oluştur</p>
            <h3 class="text-2xl font-bold text-white">Yeni Oturum Kurulumu</h3>
            <p class="text-slate-400 text-sm mt-1">Bu oturum için zaman çizelgesi, fiyatlandırma ve turbo davranışını yapılandırın.</p>
        </div>

        <form @submit.prevent="submitForm" class="space-y-5">
            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Temel Bilgiler</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Başlık</label>
                        <input
                            v-model="form.title"
                            type="text"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                            placeholder="Örn: Sabah Pilatesi @ 10:00"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Açıklama</label>
                        <input
                            v-model="form.description"
                            type="text"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                            placeholder="İsteğe bağlı detaylar..."
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Zamanlama</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Başlangıç Zamanı</label>
                        <input
                            v-model="form.start_time"
                            type="datetime-local"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue cursor-pointer"
                            @click="$event.target.showPicker && $event.target.showPicker()"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Bitiş Zamanı</label>
                        <input
                            v-model="form.end_time"
                            type="datetime-local"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue cursor-pointer"
                            @click="$event.target.showPicker && $event.target.showPicker()"
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Fiyatlandırma Motoru</h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Başlangıç Fiyatı (TL)</label>
                        <input
                            v-model.number="form.start_price"
                            type="number"
                            min="0"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Taban Fiyat (TL)</label>
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
                        <label class="block text-sm font-medium text-slate-300">Düşüş Aralığı (Dk)</label>
                        <input
                            v-model.number="form.drop_interval_mins"
                            type="number"
                            min="1"
                            required
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Düşüş Miktarı (TL)</label>
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
                        <h4 class="text-white font-semibold">Turbo Mod</h4>
                        <p class="text-xs text-slate-400">Oturum sonuna yaklaşınca fiyat düşüşünü hızlandırın.</p>
                    </div>
                    <label for="turbo-toggle" class="inline-flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                        <input
                            v-model="form.turbo_enabled"
                            type="checkbox"
                            id="turbo-toggle"
                            class="w-5 h-5 rounded border-slate-600 text-neon-blue focus:ring-neon-blue bg-dark-bg/60"
                        />
                        <span>Aktif</span>
                    </label>
                </div>
            
                <div v-if="form.turbo_enabled" class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-700/50">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Tetikleyici (Son X Dk)</label>
                        <input
                            v-model.number="form.turbo_trigger_mins"
                            type="number"
                            min="1"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Turbo Aralığı (Dk)</label>
                        <input
                            v-model.number="form.turbo_interval_mins"
                            type="number"
                            min="1"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Turbo Miktarı (TL)</label>
                        <input
                            v-model.number="form.turbo_drop_amount"
                            type="number"
                            min="1"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                </div>
            </div>

            <div class="flex justify-end pt-4">
                <button
                    type="submit"
                    :disabled="loading"
                    class="bg-gradient-to-r from-neon-blue to-primary hover:to-blue-600 text-white font-bold py-3 px-8 rounded-lg shadow-lg shadow-neon-blue/20 transform transition hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <span v-if="loading" class="flex items-center gap-2">
                        <svg class="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
                        Oluşturuluyor...
                    </span>
                    <span v-else>Oturumu Başlat</span>
                </button>
            </div>
        </form>
    </div>
</template>
