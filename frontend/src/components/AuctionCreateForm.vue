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

const DISCOUNT_OPTIONS = [10, 20, 30, 40, 50, 60, 70, 80, 90]
const TURBO_TRIGGER_DEFAULT = 120
const TURBO_INTERVAL_DEFAULT = 10

const selectedDiscountRate = ref(null)
const showDiscountDropdown = ref(false)
const loading = ref(false)

const form = reactive({
    title: '',
    description: '',
    start_time: '',
    end_time: '',
    start_price: null,
    floor_price: null,
    drop_interval_mins: null,
    drop_amount: null,
    turbo_enabled: false,
    turbo_trigger_mins: TURBO_TRIGGER_DEFAULT,
    turbo_interval_mins: TURBO_INTERVAL_DEFAULT,
    turbo_drop_amount: null
})

const roundMoney = (value) => Number(Number(value || 0).toFixed(2))
const floorMoney = (value) => Math.floor(Number(value || 0) * 100) / 100

const formatDateForInput = (isoString) => {
    if (!isoString) return ''
    const date = new Date(isoString)
    if (isNaN(date.getTime())) return ''

    const year = date.getFullYear()
    const month = String(date.getMonth() + 1).padStart(2, '0')
    const day = String(date.getDate()).padStart(2, '0')
    const hours = String(date.getHours()).padStart(2, '0')
    const minutes = String(date.getMinutes()).padStart(2, '0')

    return `${year}-${month}-${day}T${hours}:${minutes}`
}

const inferDiscountRate = (startPrice, floorPrice) => {
    if (!startPrice || startPrice <= 0) return 50
    const raw = ((startPrice - floorPrice) / startPrice) * 100
    const roundedTo10 = Math.round(raw / 10) * 10
    const bounded = Math.min(90, Math.max(10, roundedTo10))
    return DISCOUNT_OPTIONS.includes(bounded) ? bounded : 50
}

const calculateDurationMinutes = () => {
    const startDate = new Date(form.start_time)
    const endDate = new Date(form.end_time)
    if (isNaN(startDate.getTime()) || isNaN(endDate.getTime()) || endDate <= startDate) {
        return null
    }
    return Math.max(1, Math.floor((endDate - startDate) / 60000))
}

const isTurboEligible = () => {
    const durationMins = calculateDurationMinutes()
    return durationMins !== null && durationMins >= 180
}

const chooseOptimalInterval = (durationMins) => {
    if (durationMins <= 30) return 2
    if (durationMins <= 60) return 5
    if (durationMins <= 120) return 10
    if (durationMins <= 240) return 15
    if (durationMins <= 480) return 30
    if (durationMins <= 720) return 45
    return 60
}

const calculateDropCount = (durationMins, intervalMins) => {
    if (!durationMins || !intervalMins) return 1
    return Math.max(1, Math.floor(durationMins / intervalMins))
}

const applyAutomaticPricing = () => {
    const startPrice = Number(form.start_price) || 0
    const discountRate = Number(selectedDiscountRate.value)
    const durationMins = calculateDurationMinutes()

    const hasPricingInputs = startPrice > 0 && Number.isFinite(discountRate)
    const hasSchedulingInputs = durationMins !== null

    if (!hasPricingInputs || !hasSchedulingInputs) {
        form.floor_price = null
        form.drop_interval_mins = null
        form.drop_amount = null
        form.turbo_trigger_mins = TURBO_TRIGGER_DEFAULT
        form.turbo_interval_mins = TURBO_INTERVAL_DEFAULT
        form.turbo_drop_amount = null
        return
    }

    const floorPrice = roundMoney(startPrice * (1 - (discountRate / 100)))
    const totalDiscountAmount = Math.max(0, startPrice - floorPrice)

    form.floor_price = floorPrice

    if (form.turbo_enabled && !isTurboEligible()) {
        form.turbo_enabled = false
    }

    const turboActive = form.turbo_enabled && isTurboEligible()

    if (turboActive) {
        const triggerMins = TURBO_TRIGGER_DEFAULT
        const intervalTurbo = TURBO_INTERVAL_DEFAULT
        const normalDurationMins = Math.max(1, durationMins - triggerMins)

        // Turbo always more frequent than normal mode
        const normalIntervalBase = chooseOptimalInterval(normalDurationMins)
        const normalInterval = Math.max(intervalTurbo + 5, normalIntervalBase)

        const normalDrops = calculateDropCount(normalDurationMins, normalInterval)
        const turboDrops = calculateDropCount(triggerMins, intervalTurbo)

        // Turbo steps should be smaller than normal steps.
        // ratio=0.65 => turbo drop amount is 65% of normal drop amount.
        const turboToNormalRatio = 0.65

        const normalDropRaw = totalDiscountAmount / (normalDrops + (turboDrops * turboToNormalRatio))
        const turboDropRaw = normalDropRaw * turboToNormalRatio

        const normalDropAmount = roundMoney(Math.max(0.01, normalDropRaw))
        const turboDropAmount = roundMoney(Math.max(0.01, Math.min(turboDropRaw, normalDropRaw - 0.01)))

        form.drop_interval_mins = normalInterval
        form.drop_amount = normalDropAmount
        form.turbo_trigger_mins = triggerMins
        form.turbo_interval_mins = intervalTurbo
        form.turbo_drop_amount = turboDropAmount
    } else {
        const intervalMins = chooseOptimalInterval(durationMins)
        const normalDrops = calculateDropCount(durationMins, intervalMins)
        const normalDropAmount = roundMoney(Math.max(0.01, totalDiscountAmount / normalDrops))

        form.drop_interval_mins = intervalMins
        form.drop_amount = normalDropAmount
        form.turbo_trigger_mins = TURBO_TRIGGER_DEFAULT
        form.turbo_interval_mins = TURBO_INTERVAL_DEFAULT
        form.turbo_drop_amount = null
    }
}

const populateForm = (data) => {
    const newData = { ...data }

    const startPrice = Number(newData.start_price ?? newData.startPrice ?? form.start_price)
    const floorPrice = Number(newData.floor_price ?? newData.floorPrice ?? form.floor_price)
    selectedDiscountRate.value = inferDiscountRate(startPrice, floorPrice)

    if (newData.start_time || newData.startTime) {
        newData.start_time = formatDateForInput(newData.start_time || newData.startTime)
    }
    if (newData.end_time || newData.endTime) {
        newData.end_time = formatDateForInput(newData.end_time || newData.endTime)
    }

    Object.assign(form, {
        ...newData,
        start_price: startPrice,
        floor_price: floorPrice,
        drop_interval_mins: Number(newData.drop_interval_mins ?? newData.dropIntervalMins ?? form.drop_interval_mins),
        drop_amount: Number(newData.drop_amount ?? newData.dropAmount ?? form.drop_amount),
        turbo_enabled: Boolean(newData.turbo_enabled ?? newData.turboEnabled ?? form.turbo_enabled),
        turbo_trigger_mins: Number(newData.turbo_trigger_mins ?? newData.turboTriggerMins ?? form.turbo_trigger_mins),
        turbo_interval_mins: Number(newData.turbo_interval_mins ?? newData.turboIntervalMins ?? form.turbo_interval_mins),
        turbo_drop_amount: Number(newData.turbo_drop_amount ?? newData.turboDropAmount ?? form.turbo_drop_amount)
    })

    applyAutomaticPricing()
}

onMounted(() => {
    if (props.initialData) {
        populateForm(props.initialData)
    }
})

watch(() => props.initialData, (newVal) => {
    if (newVal) {
        populateForm(newVal)
    }
}, { deep: true })

watch(
    () => [form.start_price, selectedDiscountRate.value, form.start_time, form.end_time, form.turbo_enabled],
    () => applyAutomaticPricing(),
    { deep: false }
)

watch(
    () => [form.start_time, form.end_time],
    () => {
        if (form.turbo_enabled && !isTurboEligible()) {
            form.turbo_enabled = false
        }
    }
)

const submitForm = () => {
    loading.value = true
    applyAutomaticPricing()

    if (!form.start_time || !form.end_time || !form.start_price || !selectedDiscountRate.value) {
        loading.value = false
        alert('Lütfen önce Zamanlama, Başlangıç Fiyatı ve İndirim Yüzdesi alanlarını doldurun.')
        return
    }

    const payload = { ...form }

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
                <h4 class="text-white font-semibold">Fiyatlandırma Motoru (Basitleştirilmiş)</h4>
                <p class="text-xs text-slate-400">
                    Sadece başlangıç fiyatı ve indirim yüzdesi seçin. Taban fiyat, düşüş aralığı ve düşüş miktarı otomatik hesaplanır.
                </p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Başlangıç Fiyatı (TL)</label>
                        <input
                            v-model.number="form.start_price"
                            type="number"
                            min="1"
                            required
                            placeholder="Örn: 1000 TL"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">İndirim Yüzdesi</label>
                        <div class="relative">
                            <button
                                type="button"
                                @click="showDiscountDropdown = !showDiscountDropdown"
                                class="w-full flex items-center justify-between px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors"
                            >
                                <span>{{ selectedDiscountRate ? `%${selectedDiscountRate}` : 'İndirim Yüzdesi Seçin' }}</span>
                                <span class="material-symbols-outlined" style="font-size: 18px;">expand_more</span>
                            </button>
                            <div v-if="showDiscountDropdown" class="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1 max-h-56 overflow-y-auto">
                                <button
                                    v-for="rate in DISCOUNT_OPTIONS"
                                    :key="rate"
                                    type="button"
                                    @click="selectedDiscountRate = rate; showDiscountDropdown = false"
                                    class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]"
                                >
                                    %{{ rate }}
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Taban Fiyat (Otomatik)</label>
                        <input
                            :value="form.floor_price ?? ''"
                            type="number"
                            readonly
                            placeholder="Otomatik hesaplanacak"
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Düşüş Aralığı (Otomatik)</label>
                        <input
                            :value="form.drop_interval_mins ?? ''"
                            type="number"
                            readonly
                            placeholder="Otomatik hesaplanacak"
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Düşüş Miktarı (Otomatik)</label>
                        <input
                            :value="form.drop_amount ?? ''"
                            type="number"
                            readonly
                            placeholder="Otomatik hesaplanacak"
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
                        />
                    </div>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <div class="flex items-center justify-between gap-3">
                    <div>
                        <h4 class="text-white font-semibold">Turbo Mod</h4>
                        <p class="text-xs text-slate-400">Açılırsa sabit kural uygulanır: Son 2 saat, 10 dk aralıklarla otomatik turbo düşüş.</p>
                        <p v-if="!isTurboEligible()" class="text-[11px] text-amber-400 mt-1">Turbo için başlangıç ve bitiş arasında en az 3 saat olmalı.</p>
                    </div>
                    <label for="turbo-toggle" class="inline-flex items-center gap-2 text-sm text-slate-300 cursor-pointer">
                        <input
                            v-model="form.turbo_enabled"
                            type="checkbox"
                            id="turbo-toggle"
                            :disabled="!isTurboEligible()"
                            class="w-5 h-5 rounded border-slate-600 text-neon-blue focus:ring-neon-blue bg-dark-bg/60"
                        />
                        <span>Aktif</span>
                    </label>
                </div>
            
                <div v-if="form.turbo_enabled" class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4 border-t border-slate-700/50">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Tetikleyici (Sabit)</label>
                        <input
                            :value="form.turbo_trigger_mins"
                            type="number"
                            readonly
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Turbo Aralığı (Sabit)</label>
                        <input
                            :value="form.turbo_interval_mins"
                            type="number"
                            readonly
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
                        />
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">Turbo Düşüş Miktarı (Otomatik)</label>
                        <input
                            :value="form.turbo_drop_amount ?? ''"
                            type="number"
                            readonly
                            placeholder="Otomatik hesaplanacak"
                            class="w-full bg-dark-bg/40 border border-slate-700 rounded-lg px-3 py-2.5 text-slate-200"
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
