<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuctionStore } from '../stores/auction'
import { useAuctionSocket } from '../composables/useAuctionSocket'
import AuctionCard from '../components/AuctionCard.vue'
import BookingSuccessModal from '../components/BookingSuccessModal.vue'
import { getAuctionStatus, getAuctionField } from '../utils/auction'
import { useHead } from '@unhead/vue'

useHead({
  title: 'Canlı Açık Artırma Fırsatları — HotHour',
  meta: [
    { name: 'description', content: 'Şu an aktif olan tüm hizmet ve işletme fırsatlarını keşfet. Fiyatlar gerçek zamanlı düşüyor — en uygun fırsatı yakala.' },
    { property: 'og:title', content: 'Canlı Açık Artırma Fırsatları — HotHour' },
    { property: 'og:description', content: 'Aktif tüm fırsatları keşfet, daha fırsat dolmadan kazan.' },
    { property: 'og:url', content: 'https://hothour.kayraspace.com/auctions' },
  ],
  link: [{ rel: 'canonical', href: 'https://hothour.kayraspace.com/auctions' }],
})

const router = useRouter()
const route = useRoute()
const store = useAuctionStore()

// Socket bağlantısı, event handler'lar ve yaşam döngüsü composable'da yönetilir
useAuctionSocket(store)

const searchQuery = ref('')
const filterStatus = ref('ACTIVE')
const selectedSector = ref('')
const selectedServiceCategory = ref('')
const selectedAllowedGender = ref('')
const routeSyncLocked = ref(false)
const showFiltersPanel = ref(false)
const showSectorDropdown = ref(false)
const showServiceCategoryDropdown = ref(false)
const showAllowedGenderDropdown = ref(false)
const filtersPanelRef = ref(null)
const sectorDropdownRef = ref(null)
const serviceCategoryDropdownRef = ref(null)
const allowedGenderDropdownRef = ref(null)

const statusOptions = [
  { id: 'ALL', label: 'Tümü', icon: 'apps' },
  { id: 'ACTIVE', label: 'Aktif Olanlar', icon: 'local_fire_department' },
  { id: 'SOLD', label: 'Satıldı', icon: 'check_circle' }
]

const allowedGenderOptions = [
  { id: '', label: 'Tüm Katılımcı Kuralları', hint: 'Tüm fırsatları gösterir.' },
  { id: 'ANY', label: 'Karışık', hint: 'Herkesin katılabildiği fırsatlar.' },
  { id: 'FEMALE', label: 'Kadın', hint: 'Yalnızca kadın katılımcılar için.' },
  { id: 'MALE', label: 'Erkek', hint: 'Yalnızca erkek katılımcılar için.' }
]

const sectorOptions = computed(() => Array.isArray(store.sectors) ? store.sectors : [])
const serviceCategoryOptions = computed(() => Array.isArray(store.serviceCategories) ? store.serviceCategories : [])
const hasActiveFilters = computed(() => Boolean(searchQuery.value.trim() || filterStatus.value !== 'ACTIVE' || selectedSector.value || selectedServiceCategory.value || selectedAllowedGender.value))
const activeFilterCount = computed(() => {
  let count = 0

  if (searchQuery.value.trim()) count += 1
  if (filterStatus.value !== 'ACTIVE') count += 1
  if (selectedSector.value) count += 1
  if (selectedServiceCategory.value) count += 1
  if (selectedAllowedGender.value) count += 1

  return count
})
const selectedSectorLabel = computed(() => {
  return sectorOptions.value.find((sector) => sector.slug === selectedSector.value)?.name || ''
})
const selectedServiceCategoryLabel = computed(() => {
  return serviceCategoryOptions.value.find((category) => category.slug === selectedServiceCategory.value)?.name || ''
})
const selectedStatusLabel = computed(() => {
  return statusOptions.find((status) => status.id === filterStatus.value)?.label || 'Aktif Olanlar'
})
const selectedAllowedGenderLabel = computed(() => {
  return allowedGenderOptions.find((option) => option.id === selectedAllowedGender.value)?.label || ''
})
const sectorButtonLabel = computed(() => selectedSectorLabel.value || 'Tüm İşletme Sektörleri')
const serviceCategoryButtonLabel = computed(() => selectedServiceCategoryLabel.value || 'Tüm Hizmet Kategorileri')
const allowedGenderButtonLabel = computed(() => selectedAllowedGenderLabel.value || 'Tüm Katılımcı Kuralları')

const buildRouteQuery = () => {
  const query = {}

  if (searchQuery.value.trim()) {
    query.q = searchQuery.value.trim()
  }

  if (filterStatus.value !== 'ACTIVE') {
    query.status = filterStatus.value
  }

  if (selectedSector.value) {
    query.sector = selectedSector.value
  }

  if (selectedServiceCategory.value) {
    query.service_category = selectedServiceCategory.value
  }

  if (selectedAllowedGender.value) {
    query.participant_rule = selectedAllowedGender.value
  }

  return query
}

const syncStateFromRoute = (query) => {
  routeSyncLocked.value = true
  searchQuery.value = typeof query.q === 'string' ? query.q : ''
  filterStatus.value = typeof query.status === 'string' ? query.status : 'ACTIVE'
  selectedSector.value = typeof query.sector === 'string' ? query.sector : ''
  selectedServiceCategory.value = typeof query.service_category === 'string' ? query.service_category : ''
  selectedAllowedGender.value = typeof query.participant_rule === 'string' ? query.participant_rule.toUpperCase() : ''
  routeSyncLocked.value = false
}

const refreshTaxonomyFilters = async () => {
  await store.fetchSectors()
  await store.fetchServiceCategories({ sector: selectedSector.value || null })

  if (
    selectedServiceCategory.value &&
    !serviceCategoryOptions.value.some((item) => item?.slug === selectedServiceCategory.value)
  ) {
    selectedServiceCategory.value = ''
  }
}

const refreshAuctions = async () => {
  await store.fetchAuctions({
    sector: selectedSector.value || null,
    serviceCategory: selectedServiceCategory.value || null,
    allowedGender: selectedAllowedGender.value || null,
  })
}

const syncRouteAndData = async () => {
  if (routeSyncLocked.value) return

  routeSyncLocked.value = true
  await router.replace({ query: buildRouteQuery() })
  routeSyncLocked.value = false

  await refreshTaxonomyFilters()
  await refreshAuctions()
}

syncStateFromRoute(route.query)

watch(
  () => route.query,
  async (query) => {
    if (routeSyncLocked.value) return
    syncStateFromRoute(query)
    await refreshTaxonomyFilters()
    await refreshAuctions()
  },
  { immediate: true }
)

watch([selectedSector, selectedServiceCategory, selectedAllowedGender], async ([newSector], [oldSector]) => {
  if (routeSyncLocked.value) return

  if (newSector !== oldSector) {
    selectedServiceCategory.value = ''
  }

  await syncRouteAndData()
})

watch([searchQuery, filterStatus], async () => {
  if (routeSyncLocked.value) return
  routeSyncLocked.value = true
  await router.replace({ query: buildRouteQuery() })
  routeSyncLocked.value = false
})

const filteredAuctions = computed(() => {
  const oneMonthAgo = new Date()
  oneMonthAgo.setMonth(oneMonthAgo.getMonth() - 1)

  const isWithinLastMonth = (auction) => {
    const dateValue =
      getAuctionField(auction, 'scheduled_at', 'scheduledAt') ??
      getAuctionField(auction, 'start_time', 'startTime') ??
      getAuctionField(auction, 'created_at', 'createdAt')

    if (!dateValue) return true
    const auctionDate = new Date(dateValue)
    if (Number.isNaN(auctionDate.getTime())) return true
    return auctionDate >= oneMonthAgo
  }

  let result = Array.isArray(store.auctions)
    ? store.auctions.filter((auction) => auction && typeof auction === 'object')
    : []

  result = result.filter(isWithinLastMonth)

  if (filterStatus.value === 'ALL') {
    // "Tümü" seçildiğinde taslak gibi durumları göstermeyip
    // yalnızca ACTIVE veya SOLD durumundaki oturumları göster.
    result = result.filter(a => {
      const status = getAuctionStatus(a)
      return status === 'ACTIVE' || status === 'SOLD'
    })
  } else {
    result = result.filter(a => getAuctionStatus(a) === filterStatus.value)
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase()
    const matchStudio = (a) => {
      return String(
        a?.studio?.name || a?.studioName || a?.studio_name || a?.studio?.title || ''
      ).toLowerCase().includes(query)
    }

    result = result.filter(a =>
      String(a?.title ?? '').toLowerCase().includes(query) ||
      String(a?.description ?? '').toLowerCase().includes(query) ||
      matchStudio(a)
    )
  }

  return result
})

const handleFilterChange = (status) => {
  filterStatus.value = status
}

const clearFilters = async () => {
  searchQuery.value = ''
  filterStatus.value = 'ACTIVE'
  selectedSector.value = ''
  selectedServiceCategory.value = ''
  selectedAllowedGender.value = ''
  showSectorDropdown.value = false
  showServiceCategoryDropdown.value = false
  showAllowedGenderDropdown.value = false
  await syncRouteAndData()
}

const closeFilterPopups = () => {
  showSectorDropdown.value = false
  showServiceCategoryDropdown.value = false
  showAllowedGenderDropdown.value = false
}

const handleOutsideClick = (event) => {
  const target = event.target

  if (!filtersPanelRef.value?.contains(target)) {
    showFiltersPanel.value = false
    closeFilterPopups()
    return
  }

  if (!sectorDropdownRef.value?.contains(target)) {
    showSectorDropdown.value = false
  }

  if (!serviceCategoryDropdownRef.value?.contains(target)) {
    showServiceCategoryDropdown.value = false
  }

  if (!allowedGenderDropdownRef.value?.contains(target)) {
    showAllowedGenderDropdown.value = false
  }
}

onMounted(() => {
  document.addEventListener('click', handleOutsideClick)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', handleOutsideClick)
})

const showSuccessModal = ref(false)
const bookingResult = ref(null)

const onBookingSuccess = (reservation) => {
  bookingResult.value = reservation
  showSuccessModal.value = true
}
</script>

<template>
  <div class="w-full min-h-screen bg-[#050505] font-sans text-slate-200 selection:bg-neon-blue/30 selection:text-white">
    
    <header class="relative px-6 py-12 md:py-16 overflow-hidden border-b border-white/5">
      <div class="absolute inset-0 bg-gradient-to-b from-neon-blue/5 via-transparent to-transparent pointer-events-none"></div>
      <div class="absolute top-0 right-1/4 w-96 h-96 bg-neon-blue/10 rounded-full blur-[100px] pointer-events-none"></div>
      
      <div class="max-w-7xl mx-auto relative z-10 flex flex-col md:flex-row md:items-end justify-between gap-6">
        <div>
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 text-xs font-medium text-neon-blue mb-4">
            <span class="w-2 h-2 rounded-full bg-neon-blue animate-pulse"></span>
            Canlı Pazar
          </div>
          <h1 class="text-4xl md:text-5xl lg:text-6xl font-black text-white tracking-tight mb-2">
            Fırsatları <span class="text-transparent bg-clip-text bg-gradient-to-r from-neon-blue to-purple-500 drop-shadow-[0_0_15px_rgba(0,191,255,0.3)]">Keşfet</span>
          </h1>
          <p class="text-slate-400 text-sm md:text-base max-w-xl">
            Çeşitli hizmetler şu an hollanda usulü açık artırmada. Zaman geçtikçe fiyat düşer, ilk basan kazanır.
          </p>
        </div>
        
        <div class="flex items-center gap-2 px-4 py-2 bg-black/50 border border-white/10 rounded-xl backdrop-blur-md">
          <span class="material-symbols-outlined text-neon-blue animate-pulse">sensors</span>
          <span class="text-xs font-bold text-slate-300 tracking-wider uppercase">Canlı Fiyat Akışı Aktif</span>
        </div>
      </div>
    </header>

    <main class="max-w-7xl mx-auto px-6 py-8">
      
      <section ref="filtersPanelRef" class="mb-8 sticky top-4 z-20">
        <div class="rounded-[26px] border border-white/8 bg-[linear-gradient(180deg,rgba(12,17,29,0.94),rgba(8,12,21,0.92))] p-3 sm:p-4 shadow-[0_18px_50px_rgba(0,0,0,0.28)] backdrop-blur-xl">
          <div class="flex flex-col gap-3 lg:flex-row lg:items-center">
            <div class="relative min-w-0 flex-1 group">
              <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <span class="material-symbols-outlined text-slate-500 group-focus-within:text-neon-blue transition-colors">search</span>
              </div>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Hizmet veya işletme ara..."
                class="w-full rounded-2xl border border-slate-700 bg-[#0d1424]/90 py-3.5 pl-12 pr-4 text-sm text-white placeholder:text-sm placeholder-slate-500 focus:border-neon-blue focus:outline-none focus:ring-1 focus:ring-neon-blue sm:text-base sm:placeholder:text-base"
              />
            </div>

            <div class="flex w-full items-center gap-2 sm:gap-3 lg:w-auto">
              <button
                type="button"
                @click="showFiltersPanel = !showFiltersPanel; closeFilterPopups()"
                :class="hasActiveFilters ? 'flex-1' : 'w-full'"
                class="inline-flex items-center justify-between gap-3 rounded-2xl border border-slate-700 bg-[#0d1424]/90 px-4 py-3.5 text-sm font-bold text-white transition-colors hover:border-neon-blue/50 hover:bg-[#10192d] sm:min-w-[150px] lg:w-auto"
              >
                <span class="inline-flex items-center gap-2">
                  <span class="material-symbols-outlined text-[18px] text-neon-blue">tune</span>
                  Filtrele
                  <span v-if="activeFilterCount" class="inline-flex h-6 min-w-6 items-center justify-center rounded-full bg-neon-blue px-1.5 text-[11px] font-black text-black">{{ activeFilterCount }}</span>
                </span>
                <span class="material-symbols-outlined text-[18px] text-slate-400 transition-transform" :class="showFiltersPanel ? 'rotate-180' : ''">expand_more</span>
              </button>

              <button
                v-if="hasActiveFilters"
                type="button"
                @click="clearFilters"
                class="inline-flex shrink-0 items-center justify-center gap-2 rounded-2xl border border-white/10 bg-white/5 px-4 py-3.5 text-sm font-bold text-slate-200 transition-colors hover:bg-white/10"
              >
                <span class="material-symbols-outlined text-[18px]">filter_alt_off</span>
                <span class="hidden sm:inline">Temizle</span>
              </button>
            </div>
          </div>

          <div v-if="hasActiveFilters" class="mt-3 flex flex-wrap gap-2">
            <span v-if="searchQuery.trim()" class="rounded-full border border-neon-blue/20 bg-neon-blue/10 px-3 py-1 text-xs font-semibold text-neon-blue">
              Arama: {{ searchQuery }}
            </span>
            <span v-if="selectedSectorLabel" class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">
              Sektör: {{ selectedSectorLabel }}
            </span>
            <span v-if="selectedServiceCategoryLabel" class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">
              Kategori: {{ selectedServiceCategoryLabel }}
            </span>
            <span v-if="selectedAllowedGenderLabel" class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">
              Katılımcı kuralı: {{ selectedAllowedGenderLabel }}
            </span>
            <span v-if="filterStatus !== 'ACTIVE'" class="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs font-semibold text-slate-200">
              Durum: {{ selectedStatusLabel }}
            </span>
          </div>

          <transition
            enter-active-class="transition duration-200 ease-out"
            enter-from-class="opacity-0 -translate-y-2"
            enter-to-class="opacity-100 translate-y-0"
            leave-active-class="transition duration-150 ease-in"
            leave-from-class="opacity-100 translate-y-0"
            leave-to-class="opacity-0 -translate-y-2"
          >
            <div v-if="showFiltersPanel" class="mt-4 rounded-[22px] border border-white/8 bg-black/20 p-4 sm:p-5">
              <div class="grid grid-cols-1 gap-4 lg:grid-cols-3">
                <div ref="sectorDropdownRef" class="space-y-2">
                  <label class="block text-sm font-medium text-slate-300">İşletme Sektörü</label>
                  <div class="relative">
                    <button
                      type="button"
                      @click="showSectorDropdown = !showSectorDropdown; showServiceCategoryDropdown = false"
                      class="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors"
                    >
                      <span class="truncate text-left">{{ sectorButtonLabel }}</span>
                      <span class="material-symbols-outlined" style="font-size: 18px;">expand_more</span>
                    </button>
                    <div v-if="showSectorDropdown" class="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1 max-h-64 overflow-y-auto">
                      <button
                        type="button"
                        @click="selectedSector = ''; showSectorDropdown = false"
                        class="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f] transition-colors"
                      >
                        <span class="block font-medium">Tüm İşletme Sektörleri</span>
                        <span class="block text-xs text-slate-500 dark:text-slate-400 mt-1">Tüm işletmeler gösterilir.</span>
                      </button>
                      <button
                        v-for="sector in sectorOptions"
                        :key="sector.id"
                        type="button"
                        @click="selectedSector = sector.slug; showSectorDropdown = false"
                        class="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f] transition-colors"
                      >
                        <span class="block font-medium">{{ sector.name }}</span>
                        <span class="block text-xs text-slate-500 dark:text-slate-400 mt-1">Bu sektöre bağlı işletmeleri gösterir.</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div ref="serviceCategoryDropdownRef" class="space-y-2">
                  <label class="block text-sm font-medium text-slate-300">Hizmet Kategorisi</label>
                  <div class="relative">
                    <button
                      type="button"
                      @click="showServiceCategoryDropdown = !showServiceCategoryDropdown; showSectorDropdown = false"
                      class="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors"
                    >
                      <span class="truncate text-left">{{ serviceCategoryButtonLabel }}</span>
                      <span class="material-symbols-outlined" style="font-size: 18px;">expand_more</span>
                    </button>
                    <div v-if="showServiceCategoryDropdown" class="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1 max-h-64 overflow-y-auto">
                      <button
                        type="button"
                        @click="selectedServiceCategory = ''; showServiceCategoryDropdown = false"
                        class="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f] transition-colors"
                      >
                        <span class="block font-medium">Tüm Hizmet Kategorileri</span>
                        <span class="block text-xs text-slate-500 dark:text-slate-400 mt-1">Seçili sektördeki tüm hizmetleri gösterir.</span>
                      </button>
                      <button
                        v-for="category in serviceCategoryOptions"
                        :key="category.id"
                        type="button"
                        @click="selectedServiceCategory = category.slug; showServiceCategoryDropdown = false"
                        class="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f] transition-colors"
                      >
                        <span class="block font-medium">{{ category.name }}</span>
                        <span v-if="category.sector?.name" class="block text-xs text-slate-500 dark:text-slate-400 mt-1">{{ category.sector.name }}</span>
                      </button>
                    </div>
                  </div>
                </div>

                <div ref="allowedGenderDropdownRef" class="space-y-2">
                  <label class="block text-sm font-medium text-slate-300">Katılımcı Kuralı</label>
                  <div class="relative">
                    <button
                      type="button"
                      @click="showAllowedGenderDropdown = !showAllowedGenderDropdown; showSectorDropdown = false; showServiceCategoryDropdown = false"
                      class="w-full flex items-center justify-between px-4 py-3 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors"
                    >
                      <span class="truncate text-left">{{ allowedGenderButtonLabel }}</span>
                      <span class="material-symbols-outlined" style="font-size: 18px;">expand_more</span>
                    </button>
                    <div v-if="showAllowedGenderDropdown" class="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1 max-h-64 overflow-y-auto">
                      <button
                        v-for="option in allowedGenderOptions"
                        :key="option.id || 'all'"
                        type="button"
                        @click="selectedAllowedGender = option.id; showAllowedGenderDropdown = false"
                        class="w-full text-left px-4 py-3 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f] transition-colors"
                      >
                        <span class="block font-medium">{{ option.label }}</span>
                        <span class="block text-xs text-slate-500 dark:text-slate-400 mt-1">{{ option.hint }}</span>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="mt-4 space-y-2">
                <label class="block text-sm font-medium text-slate-300">Fırsat Durumu</label>
                <div class="flex p-1.5 bg-slate-900/60 border border-slate-700 rounded-2xl backdrop-blur-md overflow-x-auto hide-scrollbar">
                  <button
                    v-for="status in statusOptions"
                    :key="status.id"
                    @click="handleFilterChange(status.id)"
                    class="flex items-center gap-2 px-5 py-2.5 rounded-xl whitespace-nowrap text-sm font-bold transition-all"
                    :class="filterStatus === status.id
                      ? 'bg-neon-blue text-black shadow-[0_0_15px_rgba(0,191,255,0.4)]'
                      : 'text-slate-400 hover:text-white hover:bg-white/5'"
                  >
                    <span class="material-symbols-outlined text-sm" :class="filterStatus === status.id ? 'text-black' : ''">{{ status.icon }}</span>
                    {{ status.label }}
                  </button>
                </div>
                <p class="text-xs text-slate-500">Seçimler anında uygulanır. Panel yalnızca daha sade bir kullanım için açılır yapıda sunulur.</p>
              </div>
            </div>
          </transition>
        </div>
      </section>

      <div v-if="store.loading" class="flex flex-col justify-center items-center py-24">
        <div class="relative w-20 h-20">
          <div class="absolute inset-0 rounded-full border-t-2 border-neon-blue animate-spin"></div>
          <div class="absolute inset-2 rounded-full border-r-2 border-purple-500 animate-spin opacity-70" style="animation-direction: reverse; animation-duration: 1.5s;"></div>
        </div>
        <p class="text-slate-400 mt-6 font-medium animate-pulse">Fırsatlar aranıyor...</p>
      </div>

      <div v-else-if="store.error" class="bg-red-950/30 border border-red-900/50 rounded-2xl p-8 text-center max-w-lg mx-auto backdrop-blur-sm mt-12">
        <div class="w-16 h-16 bg-red-900/30 rounded-full flex items-center justify-center mx-auto mb-4">
          <span class="material-symbols-outlined text-red-500 text-3xl">wifi_off</span>
        </div>
        <h3 class="text-xl font-bold text-white mb-2">Bağlantı Hatası</h3>
        <p class="text-red-200 mb-6">{{ store.error }}</p>
        <button @click="refreshAuctions()" class="px-6 py-3 bg-red-900/50 hover:bg-red-800/50 text-white rounded-xl transition-colors border border-red-700/50 text-sm font-bold">
          Tekrar Dene
        </button>
      </div>

      <div v-else-if="filteredAuctions.length === 0" class="flex flex-col items-center justify-center py-24 text-center border-2 border-dashed border-slate-800 rounded-3xl bg-slate-900/20">
        <div class="relative w-24 h-24 mb-6">
          <div class="absolute inset-0 bg-neon-blue/10 rounded-full animate-ping opacity-50"></div>
          <div class="relative flex items-center justify-center w-full h-full bg-slate-900 border border-slate-700 rounded-full">
            <span class="material-symbols-outlined text-4xl text-slate-500">radar</span>
          </div>
        </div>
        <h3 class="text-2xl font-bold text-white mb-2">Radarımızda Bir Şey Yok</h3>
        <p class="text-slate-400 mb-8 max-w-md">
          {{ searchQuery ? `"${searchQuery}" aramasıyla eşleşen bir fırsat bulamadık.` : 'Seçtiğiniz filtrelere uygun bir fırsat bulunmuyor. Radarımız açık, beklemede kal!' }}
        </p>
        <button 
          v-if="searchQuery || filterStatus !== 'ACTIVE' || selectedSector || selectedServiceCategory || selectedAllowedGender"
          @click="clearFilters"
          class="px-6 py-3 bg-white/5 hover:bg-white/10 border border-white/10 text-white font-bold rounded-xl transition-colors flex items-center gap-2"
        >
          <span class="material-symbols-outlined text-sm">filter_alt_off</span>
          Filtreleri Temizle
        </button>
      </div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 pb-12">
        <AuctionCard 
          v-for="auction in filteredAuctions" 
          :key="auction.id" 
          :auction="auction" 
          class="transform hover:-translate-y-1 transition-all duration-300"
          @booking-success="onBookingSuccess"
        />
      </div>

    </main>

  <BookingSuccessModal
    :visible="showSuccessModal"
    :reservation="bookingResult"
    @close="showSuccessModal = false"
  />
  </div>
</template>

<style scoped>
/* Scrollbar'ı gizlemek için utility class (Filter sekmelerinde yatay kaydırma için) */
.hide-scrollbar::-webkit-scrollbar {
  display: none;
}
.hide-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>