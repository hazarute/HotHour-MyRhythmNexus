<script setup>
import { onMounted, onUnmounted, computed, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useSocketStore } from '../stores/socket'
import { useAuthStore } from '../stores/auth'
import HemenKapButton from '../components/HemenKapButton.vue'
import BookingConfirmModal from '../components/BookingConfirmModal.vue'
import BookingSuccessModal from '../components/BookingSuccessModal.vue'
import { getAuctionField, getAuctionCurrentPrice, getAuctionStartPrice, getAuctionEndTime, getAuctionStatus } from '../utils/auction'
import { formatPrice, formatDateLong as formatDate } from '../utils/formatters'
import { useHead } from '@unhead/vue'

const route = useRoute()
const router = useRouter()
const auctionStore = useAuctionStore()
const socketStore = useSocketStore()
const authStore = useAuthStore()

const auction = computed(() => auctionStore.currentAuction)

// Dinamik SEO: auction verisi yüklenince otomatik güncellenir
useHead({
  title: computed(() => {
    if (!auction.value) return 'Seans Detayı — HotHour'
    const studio = getAuctionField(auction.value, 'studio', 'studio')
    const studioName = studio?.name || 'Stüdyo'
    const date = getAuctionField(auction.value, 'start_time', 'startTime')
    const dateStr = date ? new Date(date).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long' }) : ''
    return `${studioName} — ${dateStr} Pilates Seansı | HotHour`
  }),
  meta: computed(() => {
    if (!auction.value) return []
    const studio = getAuctionField(auction.value, 'studio', 'studio')
    const studioName = studio?.name || 'Stüdyo'
    const price = getAuctionCurrentPrice(auction.value)
    const formattedPrice = price ? `${price} ₺` : ''
    const description = `${studioName} seansını ${formattedPrice} ile yakala. Fiyat her an düşüyor!`
    const canonicalUrl = `https://hothour.kayraspace.com/auction/${route.params.id}`
    return [
      { name: 'description', content: description },
      { property: 'og:title', content: `${studioName} — HotHour Canlı Seans` },
      { property: 'og:description', content: description },
      { property: 'og:url', content: canonicalUrl },
      { property: 'og:type', content: 'website' },
      { name: 'twitter:title', content: `${studioName} — HotHour Canlı Seans` },
      { name: 'twitter:description', content: description },
    ]
  }),
  link: computed(() => [
    { rel: 'canonical', href: `https://hothour.kayraspace.com/auction/${route.params.id}` }
  ]),
  script: computed(() => {
    if (!auction.value) return []
    const studio = getAuctionField(auction.value, 'studio', 'studio')
    const startTime = getAuctionField(auction.value, 'start_time', 'startTime')
    const endTime = getAuctionEndTime(auction.value)
    const price = getAuctionCurrentPrice(auction.value)
    return [
      {
        type: 'application/ld+json',
        innerHTML: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Event',
          name: `${studio?.name || 'Pilates'} Seansı`,
          description: `HotHour indirimli ${studio?.name || 'Pilates'} seansı. Fiyat ${price} ₺.`,
          startDate: startTime,
          endDate: endTime,
          eventStatus: 'https://schema.org/EventScheduled',
          eventAttendanceMode: 'https://schema.org/OfflineEventAttendanceMode',
          location: {
            '@type': 'Place',
            name: studio?.name || 'Stüdyo',
            address: studio?.address || 'İstanbul, Türkiye'
          },
          organizer: {
            '@type': 'Organization',
            name: studio?.name || 'HotHour Stüdyo',
            url: 'https://hothour.kayraspace.com'
          },
          offers: {
            '@type': 'Offer',
            price: price || 0,
            priceCurrency: 'TRY',
            availability: 'https://schema.org/InStock',
            url: `https://hothour.kayraspace.com/auction/${route.params.id}`
          }
        })
      }
    ]
  })
})
const showSuccessModal = ref(false)
const showBookingConfirmModal = ref(false)
const reservation = ref(null)
const bookingLoading = ref(false)
const nowMs = ref(Date.now())
const participantConditionFx = ref(false)
let participantConditionFxTimer = null
let timerId = null

const startPriceValue = computed(() => getAuctionStartPrice(auction.value))
const currentPriceValue = computed(() => getAuctionCurrentPrice(auction.value))
const endTimeValue = computed(() => getAuctionEndTime(auction.value))
const statusValue = computed(() => getAuctionStatus(auction.value))

const discountPercent = computed(() => {
    if (startPriceValue.value <= 0) return 0
    const discount = ((startPriceValue.value - currentPriceValue.value) / startPriceValue.value) * 100
    return Math.max(0, Math.round(discount))
})

const countdown = computed(() => {
    if (!endTimeValue.value) return { hours: '00', mins: '00', secs: '00' }

    const end = new Date(endTimeValue.value).getTime()
    const diff = end - nowMs.value

    if (diff <= 0) return { hours: '00', mins: '00', secs: '00' }

    const totalSeconds = Math.floor(diff / 1000)
    const hours = Math.floor(totalSeconds / 3600)
    const mins = Math.floor((totalSeconds % 3600) / 60)
    const secs = totalSeconds % 60

    return {
        hours: String(hours).padStart(2, '0'),
        mins: String(mins).padStart(2, '0'),
        secs: String(secs).padStart(2, '0')
    }
})

const isTurbo = computed(() => Boolean(getAuctionField(auction.value, 'turbo_started_at', 'turboStartedAt')))

const allowedGenderValue = computed(() => String(getAuctionField(auction.value, 'allowed_gender', 'allowedGender') || 'ANY').toUpperCase())

const allowedGenderLabel = computed(() => {
    if (allowedGenderValue.value === 'FEMALE') return 'Kadın'
    if (allowedGenderValue.value === 'MALE') return 'Erkek'
    return 'Fark Etmez'
})

const canCurrentUserBookByGender = computed(() => {
    if (allowedGenderValue.value === 'ANY') return true
    if (!authStore.isAuthenticated) return true
    const userGender = String(authStore.user?.gender || '').toUpperCase()
    return userGender === allowedGenderValue.value
})

const canCurrentUserBookByRole = computed(() => !(authStore.isAuthenticated && authStore.isAdmin))

const bookingDisabled = computed(() => {
    return statusValue.value !== 'ACTIVE' || !canCurrentUserBookByRole.value || !canCurrentUserBookByGender.value
})

const themeClasses = computed(() => {
    if (isTurbo.value) {
        return {
            bgMain: 'bg-[#1a0505]',
            bgCard: 'bg-[#2a0808]/80',
            borderAccent: 'border-[#ff2a2a]',
            textAccent: 'text-[#ff2a2a]',
            textTurbo: 'text-[#ff7b00]',
            gradientBtn: 'from-[#ff2a2a] via-[#ff0055] to-[#ff7b00]',
            shadowNeon: 'shadow-[0_0_30px_rgba(255,42,42,0.4)]',
            glowColor: 'rgba(255, 42, 42, 0.4)'
        }
    }

    return {
        bgMain: 'bg-[#050505]',
        bgCard: 'bg-[#0a0f1a]/80',
        borderAccent: 'border-neon-blue',
        textAccent: 'text-neon-blue',
        textTurbo: 'text-white',
        gradientBtn: 'from-primary via-blue-600 to-neon-blue',
        shadowNeon: 'shadow-[0_0_30px_rgba(0,191,255,0.2)]',
        glowColor: 'rgba(0, 191, 255, 0.3)'
    }
})

const onPriceUpdate = (data) => {
    if (data.auction_id == route.params.id) {
        auctionStore.updatePrice(route.params.id, data.current_price)
    }
}

const onAuctionBooked = (data) => {
    if (data.auction_id == route.params.id && auction.value) {
        auction.value.status = 'SOLD'
    }
}

const onTurboTriggered = (data) => {
    if (!data?.auction_id) return
    if (String(data.auction_id) !== String(route.params.id)) return
    auctionStore.updateAuctionTurboStartedAt(data.auction_id, data.turbo_started_at)
}

onMounted(async () => {
    const id = route.params.id

    if (!socketStore.isConnected) {
        socketStore.connect()
    }

    socketStore.subscribeAuction(id)
    await auctionStore.fetchAuctionById(id)

    socketStore.on('price_update', onPriceUpdate)
    socketStore.on('auction_booked', onAuctionBooked)
    socketStore.on('turbo_triggered', onTurboTriggered)

    timerId = setInterval(() => {
        nowMs.value = Date.now()
    }, 1000)
})

const handleBook = async () => {
    if (!auction.value) return

    if (!authStore.isAuthenticated) {
        router.push({ name: 'login', query: { redirect: route.fullPath } })
        return
    }

    if (!canCurrentUserBookByRole.value) return

    if (!canCurrentUserBookByGender.value) return

    showBookingConfirmModal.value = true
}

const triggerParticipantConditionFx = () => {
    participantConditionFx.value = false
    if (participantConditionFxTimer) {
        clearTimeout(participantConditionFxTimer)
        participantConditionFxTimer = null
    }

    requestAnimationFrame(() => {
        participantConditionFx.value = true
        participantConditionFxTimer = setTimeout(() => {
            participantConditionFx.value = false
            participantConditionFxTimer = null
        }, 900)
    })
}

const onDisabledBookClick = () => {
    if (!canCurrentUserBookByGender.value) {
        triggerParticipantConditionFx()
    }
}

const confirmBooking = async () => {
    showBookingConfirmModal.value = false

    bookingLoading.value = true
    try {
        const result = await auctionStore.bookAuction(auction.value.id)
        reservation.value = result
        showSuccessModal.value = true
    } catch (err) {
        alert(err.message)
    } finally {
        bookingLoading.value = false
    }
}

onUnmounted(() => {
    if (route.params.id) {
        socketStore.unsubscribeAuction(route.params.id)
    }

    socketStore.off('price_update', onPriceUpdate)
    socketStore.off('auction_booked', onAuctionBooked)
    socketStore.off('turbo_triggered', onTurboTriggered)

    if (timerId) {
        clearInterval(timerId)
        timerId = null
    }

    if (participantConditionFxTimer) {
        clearTimeout(participantConditionFxTimer)
        participantConditionFxTimer = null
    }
})
</script>

<template>
  <div v-if="auctionStore.loading && !auction" class="flex flex-col items-center justify-center min-h-screen text-white">
    <div class="relative w-24 h-24 mb-6">
        <div class="absolute inset-0 rounded-full border-t-2 border-neon-blue animate-spin"></div>
        <div class="absolute inset-2 rounded-full border-r-2 border-purple-500 animate-spin opacity-70" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
    </div>
    <p class="text-neon-blue font-mono tracking-widest animate-pulse uppercase">Arena Hazırlanıyor...</p>
  </div>

  <div v-else-if="auction" 
       class="min-h-screen flex flex-col items-center justify-center py-12 px-4 sm:px-6 lg:px-8 relative transition-colors duration-1000 font-sans">
       
    <div class="absolute top-0 left-1/4 w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none transition-colors duration-1000 mix-blend-screen"
         :style="{ backgroundColor: themeClasses.glowColor }"></div>
    <div class="absolute bottom-0 right-1/4 w-[500px] h-[500px] rounded-full blur-[150px] pointer-events-none transition-colors duration-1000 mix-blend-screen"
         :style="{ backgroundColor: isTurbo ? 'rgba(255, 123, 0, 0.15)' : 'rgba(128, 0, 255, 0.15)' }"></div>

    <div class="w-full max-w-2xl relative z-10 perspective-1000">
        
        <div v-if="isTurbo" class="absolute -top-6 left-1/2 -translate-x-1/2 z-20 w-[90%] md:w-auto">
            <div class="bg-gradient-to-r from-red-600 via-orange-500 to-red-600 text-white font-black px-8 py-2 rounded-t-xl text-center uppercase tracking-[0.2em] text-sm shadow-[0_-10px_20px_rgba(255,42,42,0.3)] border-t border-x border-white/20 animate-pulse">
                🔥 Turbo Mod Aktif 🔥
            </div>
        </div>

        <div class="relative w-full rounded-3xl p-[1px] overflow-hidden transition-all duration-700"
             :class="[themeClasses.shadowNeon, isTurbo ? 'border-2 border-red-500/50 mt-4' : 'border border-white/10']">
            
            <div class="absolute inset-0 bg-gradient-to-br from-white/20 via-transparent to-transparent opacity-50 pointer-events-none"></div>
            
            <div class="rounded-[23px] p-6 sm:p-10 relative flex flex-col items-center text-center gap-6 h-full transition-colors duration-700 backdrop-blur-2xl"
                 :class="themeClasses.bgCard">
                
                <div class="w-full flex justify-between items-center mb-2">
                    <button @click="router.push('/')" class="text-slate-400 hover:text-white transition-colors flex items-center gap-1 text-xs uppercase tracking-wider font-bold">
                        <span class="material-symbols-outlined text-sm">arrow_back</span>
                        Geri
                    </button>
                    <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full border text-[10px] font-black uppercase tracking-widest"
                         :class="isTurbo ? 'bg-red-500/20 text-red-400 border-red-500/30' : 'bg-neon-blue/10 text-neon-blue border-neon-blue/30'">
                        <span class="w-2 h-2 rounded-full animate-ping" :class="isTurbo ? 'bg-red-500' : 'bg-neon-blue'"></span>
                        Canlı İhale
                    </div>
                </div>

                <div class="w-full flex flex-col items-center">
                    <h1 class="text-3xl sm:text-4xl md:text-5xl font-black text-white leading-tight mb-2 tracking-tight">{{ auction.title }}</h1>
                    <p class="text-slate-400 text-sm max-w-md">{{ auction.description || 'Stüdyo detayları ve kurallar.' }}</p>

                    <!-- Studio Info Badge -->
                    <div v-if="auction.studio" class="mt-4 flex items-center justify-center min-w-[250px] gap-3 bg-white/5 px-4 py-3 rounded-2xl border border-white/10 hover:bg-white/10 transition-colors">
                        <img v-if="auction.studio.logoUrl" :src="auction.studio.logoUrl" class="w-12 h-12 rounded-full object-cover bg-black/50 border-2 border-white/20" alt="Studio Logo" />
                        <div class="w-12 h-12 flex items-center justify-center rounded-full bg-white/10 border-2 border-white/20" v-else>
                            <span class="material-symbols-outlined text-white/50">storefront</span>
                        </div>
                        <div class="flex flex-col text-left">
                            <span class="text-white font-bold">{{ auction.studio.name }}</span>
                            <a v-if="auction.studio.googleMapsUrl" :href="auction.studio.googleMapsUrl" target="_blank" rel="noopener noreferrer" class="text-neon-blue text-xs hover:underline flex items-center gap-1 mt-0.5" @click.stop>
                                <span class="material-symbols-outlined text-[14px]">location_on</span> Haritada Gör
                            </a>
                        </div>
                    </div>
                </div>

                <div class="w-full py-8 relative flex flex-col items-center justify-center">
                    <div class="text-xs font-bold uppercase tracking-[0.3em] mb-4" :class="themeClasses.textAccent">Anlık Fiyat</div>
                    
                    <div class="relative group">
                        <h1 v-if="isTurbo" class="absolute -inset-1 text-[80px] sm:text-[100px] md:text-[120px] font-mono font-black text-red-500 opacity-50 blur-sm translate-x-1 translate-y-1 select-none pointer-events-none">
                            {{ formatPrice(currentPriceValue) }}
                        </h1>
                        
                        <h1 class="text-[80px] sm:text-[100px] md:text-[120px] font-mono font-black leading-none tracking-tighter text-white transition-all duration-300 relative z-10 tabular-nums drop-shadow-2xl"
                            style="text-shadow: 0 10px 30px rgba(0,0,0,0.5);">
                            {{ formatPrice(currentPriceValue) }}
                        </h1>
                    </div>
                </div>

                <div class="grid grid-cols-3 gap-3 w-full max-w-sm mb-4">
                    <div class="flex flex-col items-center justify-center p-3 rounded-xl bg-black/50 border border-white/5 shadow-inner">
                        <span class="text-2xl sm:text-3xl font-black text-slate-300 font-mono tabular-nums">{{ countdown.hours }}</span>
                        <span class="text-[9px] uppercase text-slate-500 font-bold tracking-widest mt-1">Saat</span>
                    </div>
                    <div class="flex flex-col items-center justify-center p-3 rounded-xl bg-black/50 border border-white/5 shadow-inner">
                        <span class="text-2xl sm:text-3xl font-black text-slate-300 font-mono tabular-nums">{{ countdown.mins }}</span>
                        <span class="text-[9px] uppercase text-slate-500 font-bold tracking-widest mt-1">Dk</span>
                    </div>
                    <div class="flex flex-col items-center justify-center p-3 rounded-xl bg-black/80 border shadow-inner relative overflow-hidden"
                         :class="isTurbo ? 'border-red-500/50 shadow-[inset_0_0_20px_rgba(255,0,0,0.2)]' : 'border-neon-blue/30'">
                        <span class="text-3xl sm:text-4xl font-black font-mono relative z-10 tabular-nums" :class="themeClasses.textAccent">
                            {{ countdown.secs }}
                        </span>
                        <span class="text-[9px] uppercase font-bold tracking-widest mt-1 relative z-10" :class="themeClasses.textAccent">Sn</span>
                    </div>
                </div>

                <div class="w-full grid grid-cols-2 gap-3 mb-6">
                    <div class="flex flex-col items-center justify-center p-4 rounded-xl bg-white/5 border border-white/5">
                        <span class="material-symbols-outlined text-slate-400 mb-1">calendar_month</span>
                        <span class="text-[10px] text-slate-500 uppercase tracking-wider font-bold">Seans Zamanı</span>
                        <span class="text-sm font-bold text-slate-200 mt-1">{{ formatDate(auction.scheduled_at) }}</span>
                    </div>
                    
                    <div class="flex flex-col items-center justify-center p-4 rounded-xl bg-white/5 border border-white/5 relative overflow-hidden">
                        <div class="absolute inset-0 bg-gradient-to-br from-green-500/10 to-transparent"></div>
                        <span class="text-[10px] text-slate-500 uppercase tracking-wider font-bold relative z-10">Piyasa Değeri</span>
                        <span class="text-sm font-bold text-slate-400 line-through decoration-red-500 mt-1 relative z-10">{{ formatPrice(startPriceValue) }}</span>
                        <div class="mt-2 px-2 py-0.5 bg-green-500/20 border border-green-500/30 rounded text-xs font-black text-green-400 relative z-10">
                            %{{ discountPercent }} İNDİRİM
                        </div>
                    </div>
                </div>

                <div class="w-full mb-6 transition-all duration-300"
                     :class="participantConditionFx ? 'scale-[1.02]' : 'scale-100'">
                    <div class="flex items-center justify-between p-4 rounded-xl border transition-all"
                         :class="participantConditionFx ? 'border-red-500 bg-red-500/10' : 'border-white/5 bg-black/30'">
                        <div class="flex items-center gap-3">
                            <span class="material-symbols-outlined" :class="participantConditionFx ? 'text-red-500' : 'text-slate-400'">group</span>
                            <div class="text-left">
                                <p class="text-[10px] uppercase tracking-wider font-bold text-slate-500">Katılımcı Kuralı</p>
                                <p class="text-sm font-bold text-white">{{ allowedGenderLabel }}</p>
                            </div>
                        </div>
                        <span v-if="participantConditionFx" class="text-xs font-bold text-red-400 animate-pulse">Koşulu Sağlamıyorsunuz</span>
                    </div>
                </div>

                <div class="w-full">
                    <HemenKapButton
                        variant="detail"
                        :loading="bookingLoading"
                        :disabled="bookingDisabled"
                        :is-active="statusValue === 'ACTIVE'"
                        :animate-icon="isTurbo"
                        :gradient-class="themeClasses.gradientBtn"
                        :shadow-class="themeClasses.shadowNeon"
                        @click="handleBook"
                        @disabled-click="onDisabledBookClick"
                        class="w-full py-5 text-xl font-black uppercase tracking-widest rounded-2xl transform transition-all hover:scale-[1.02] active:scale-[0.98]"
                    />
                </div>

                <div class="w-full mt-4 text-center">
                    <p class="text-xs text-slate-500">
                        Rezervasyon yaparak 
                        <router-link to="/terms-of-use" class="text-neon-blue hover:text-blue-400 underline transition-colors">
                            kullanım şartlarını
                        </router-link>
                        kabul etmiş olursunuz.
                    </p>
                </div>
            </div>
        </div>
    </div>

    <BookingConfirmModal
        :visible="showBookingConfirmModal"
        :price="currentPriceValue"
        :discount-percent="discountPercent"
        :target-time="endTimeValue"
        :loading="bookingLoading"
        :title="auction.title"
        :description="auction.description"
        @cancel="showBookingConfirmModal = false"
        @confirm="confirmBooking"
    />

    <BookingSuccessModal
        :visible="showSuccessModal"
        :reservation="reservation"
        @close="showSuccessModal = false"
    />

  </div>
  
  <div v-else class="min-h-screen flex flex-col items-center justify-center text-white">
        <span class="material-symbols-outlined text-6xl text-slate-600 mb-4">search_off</span>
        <h2 class="text-2xl font-bold text-slate-400 mb-6">Oturum bulunamadı veya süresi dolmuş</h2>
        <button @click="router.push('/')" class="px-8 py-3 rounded-xl bg-white/5 border border-white/10 hover:bg-white/10 transition-colors font-bold uppercase tracking-wider text-sm">
            Arenaya Dön
        </button>
  </div>
</template>

<style scoped>
/* Tabular nums helps monospaced numbers align perfectly in timers and prices */
.tabular-nums {
    font-variant-numeric: tabular-nums;
}
</style>