import { ref, reactive, watch, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'

export const DISCOUNT_OPTIONS = [10, 20, 30, 40, 50, 60, 70, 80, 90]
export const GENDER_OPTIONS = [
    { value: 'FEMALE', label: 'Kadın' },
    { value: 'MALE', label: 'Erkek' },
    { value: 'ANY', label: 'Fark Etmez' }
]

export function useAuctionForm(props, emit) {
    const TURBO_TRIGGER_DEFAULT = 120
    const TURBO_INTERVAL_DEFAULT = 10

    const selectedDiscountRate = ref(null)
    const showDiscountDropdown = ref(false)
    const showGenderDropdown = ref(false)
    const loading = ref(false)

    const minDateTime = ref('')

    const form = reactive({
        title: '',
        description: '',
        allowed_gender: 'ANY',
        start_time: '',
        end_time: '',
        scheduled_at: '',
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

    const getAllowedGenderLabel = (value) => {
        return GENDER_OPTIONS.find((item) => item.value === value)?.label || 'Fark Etmez'
    }

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

    // Validation helper - is start time valid
    const isStartTimeValidCheck = () => {
        return form.start_time !== '' && new Date(form.start_time) > new Date()
    }

    // Validation helper - is end time valid
    const isEndTimeValidCheck = () => {
        if (!form.end_time || !form.start_time) return false
        const end = new Date(form.end_time)
        const start = new Date(form.start_time)
        return end > start
    }

    // Validation helper - is scheduled time valid
    const isScheduledAtValidCheck = () => {
        if (!form.scheduled_at || !form.end_time) return true
        const scheduled = new Date(form.scheduled_at)
        const end = new Date(form.end_time)
        return scheduled >= end
    }

    const isTurboEligible = () => {
        const durationMins = calculateDurationMinutes()
        return durationMins !== null && durationMins >= 180
    }

    // Comprehensive validation before submit
    const validateFormCompleteness = () => {
        const errors = []

        if (!form.start_time) {
            errors.push('Açık Artırma Başlangıcı zorunludur.')
        }
        if (!form.end_time) {
            errors.push('Açık Artırma Bitişi zorunludur.')
        } else if (!isEndTimeValidCheck()) {
            errors.push('Açık Artırma Bitişi, Başlangıcından sonra olmalıdır.')
        }

        if (form.scheduled_at && !isScheduledAtValidCheck()) {
            const endTime = new Date(form.end_time)
            const scheduledTime = new Date(form.scheduled_at)
            errors.push(
                `Hizmet Zamanı (${scheduledTime.toLocaleString('tr-TR')}) ` +
                `Açık Artırma Bitişi (${endTime.toLocaleString('tr-TR')}) ` +
                `tarihinden öncesine ayarlanamaz.`
            )
        }

        if (!form.start_price || form.start_price <= 0) {
            errors.push('Başlangıç Fiyatı pozitif bir sayı olmalıdır.')
        }
        if (selectedDiscountRate.value === null || selectedDiscountRate.value === undefined) {
            errors.push('İndirim Yüzdesi seçilmelidir.')
        }

        return errors
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
        if (newData.scheduled_at || newData.scheduledAt) {
            newData.scheduled_at = formatDateForInput(newData.scheduled_at || newData.scheduledAt)
        }

        Object.assign(form, {
            ...newData,
            allowed_gender: newData.allowed_gender ?? newData.allowedGender ?? form.allowed_gender,
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
        // Set minimal date to current time
        const now = new Date()
        now.setMinutes(now.getMinutes() - now.getTimezoneOffset())
        minDateTime.value = now.toISOString().slice(0, 16)

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

        // Comprehensive validation
        const validationErrors = validateFormCompleteness()
        if (validationErrors.length > 0) {
            loading.value = false
            alert('Form Hataları:\n\n' + validationErrors.join('\n'))
            return
        }

        const authStore = useAuthStore()
        const payload = { ...form }

        // Adminin bağlı olduğu studyo ID'sini ekle
        if (authStore.user?.studioId) {
            payload.studioId = authStore.user.studioId
        }

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

        if (payload.scheduled_at && payload.scheduled_at.length === 16) {
            const d = new Date(payload.scheduled_at)
            if (!isNaN(d.getTime())) {
                payload.scheduled_at = d.toISOString()
            }
        }

        if (props.isEdit) {
            emit('update-auction', { ...payload, id: props.initialData.id })
        } else {
            emit('create-auction', { ...payload })
        }

        loading.value = false
    }

    return {
        form,
        loading,
        minDateTime,
        selectedDiscountRate,
        showDiscountDropdown,
        showGenderDropdown,
        getAllowedGenderLabel,
        isTurboEligible,
        isStartTimeValidCheck,
        isEndTimeValidCheck,
        isScheduledAtValidCheck,
        submitForm
    }
}
