/**
 * useReservations — Kullanıcı rezervasyonları composable'ı.
 *
 * MyReservationsView'daki tüm fetch, cancel, kopyalama ve
 * onay akışı mantığını view dışına taşır. View yalnızca template'e odaklanır.
 *
 * Kullanım:
 *   import { useReservations } from '@/composables/useReservations'
 *   const {
 *     reservations, loading, error,
 *     copiedReservationId, cancellingReservationId,
 *     confirmCancelReservationId, cancellationFeedback, cancellationFeedbackReservationId,
 *     fetchMyReservations, cancelReservation, copyBookingCode,
 *     openCancelConfirmation, closeCancelConfirmation
 *   } = useReservations()
 */

import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

export function useReservations() {
  const router = useRouter()
  const authStore = useAuthStore()

  const reservations = ref([])
  const loading = ref(false)
  const error = ref(null)
  const copiedReservationId = ref(null)
  const cancellingReservationId = ref(null)
  const confirmCancelReservationId = ref(null)
  const cancellationFeedback = ref(null)
  const cancellationFeedbackReservationId = ref(null)

  // --- API yardımcısı ---

  const getBaseUrl = () => import.meta.env.VITE_API_URL || ''

  const authHeaders = () => ({ Authorization: `Bearer ${authStore.token}` })

  const guardAuth = () => {
    if (!authStore.token) {
      router.push('/login')
      return false
    }
    return true
  }

  // --- Rezervasyonları getir ---

  const fetchMyReservations = async () => {
    loading.value = true
    error.value = null
    try {
      if (!guardAuth()) return

      const response = await fetch(`${getBaseUrl()}/api/v1/reservations/my/all`, {
        headers: authHeaders()
      })

      if (!response.ok) {
        if (response.status === 401) {
          authStore.logout()
          router.push('/login')
          return
        }
        throw new Error('Rezervasyonlar getirilemedi. Lütfen bağlantınızı kontrol edin.')
      }

      const data = await response.json()
      reservations.value = data.reservations
    } catch (err) {
      console.error(err)
      error.value = err.message
    } finally {
      loading.value = false
    }
  }

  // --- İptal onay penceresi ---

  const openCancelConfirmation = (reservationId) => {
    confirmCancelReservationId.value = reservationId
    cancellationFeedback.value = null
    cancellationFeedbackReservationId.value = null
  }

  const closeCancelConfirmation = () => {
    confirmCancelReservationId.value = null
  }

  // --- Rezervasyonu iptal et ---

  const cancelReservation = async (reservationId) => {
    if (!reservationId || confirmCancelReservationId.value !== reservationId) {
      console.warn('Cancel action ignored due to ID mismatch or missing ID', {
        reservationId,
        confirmCancelReservationId: confirmCancelReservationId.value
      })
      return
    }

    try {
      if (!guardAuth()) return

      cancellingReservationId.value = reservationId
      cancellationFeedback.value = null
      cancellationFeedbackReservationId.value = null

      const response = await fetch(`${getBaseUrl()}/api/v1/reservations/${reservationId}`, {
        method: 'DELETE',
        headers: authHeaders()
      })

      if (!response.ok) {
        if (response.status === 401) {
          authStore.logout()
          router.push('/login')
          return
        }

        let detail = 'Rezervasyon iptal edilemedi. Lütfen tekrar deneyin.'
        try {
          const errData = await response.json()
          if (errData?.detail) detail = errData.detail
        } catch {
          // no-op
        }
        throw new Error(detail)
      }

      await fetchMyReservations()

      if (copiedReservationId.value === reservationId) {
        copiedReservationId.value = null
      }

      cancellationFeedback.value = {
        type: 'success',
        message: 'Rezervasyonunuz iptal edildi. Bu seans hakkınızı yeniden kazanamazsınız.'
      }
      cancellationFeedbackReservationId.value = reservationId
      confirmCancelReservationId.value = null
    } catch (cancelError) {
      console.error('Rezervasyon iptal hatası:', cancelError)
      cancellationFeedback.value = {
        type: 'error',
        message: cancelError.message || 'Rezervasyon iptal edilemedi.'
      }
      cancellationFeedbackReservationId.value = reservationId
    } finally {
      cancellingReservationId.value = null
    }
  }

  // --- Giriş kodunu kopyala ---

  const copyBookingCode = async (reservationId, bookingCode) => {
    const code = String(bookingCode ?? '').trim()
    if (!code) return

    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(code)
      } else {
        const textArea = document.createElement('textarea')
        textArea.value = code
        textArea.setAttribute('readonly', '')
        textArea.style.position = 'absolute'
        textArea.style.left = '-9999px'
        document.body.appendChild(textArea)
        textArea.select()
        document.execCommand('copy')
        document.body.removeChild(textArea)
      }

      copiedReservationId.value = reservationId
      setTimeout(() => {
        if (copiedReservationId.value === reservationId) {
          copiedReservationId.value = null
        }
      }, 1500)
    } catch (copyError) {
      console.error('Giriş kodu kopyalanamadı:', copyError)
    }
  }

  return {
    // State
    reservations,
    loading,
    error,
    copiedReservationId,
    cancellingReservationId,
    confirmCancelReservationId,
    cancellationFeedback,
    cancellationFeedbackReservationId,
    // Actions
    fetchMyReservations,
    cancelReservation,
    copyBookingCode,
    openCancelConfirmation,
    closeCancelConfirmation
  }
}
