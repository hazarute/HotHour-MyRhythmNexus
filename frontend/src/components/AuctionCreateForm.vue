<script setup>
import { useAuctionForm, DISCOUNT_OPTIONS, GENDER_OPTIONS } from '@/composables/admin/useAuctionForm'

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

const {
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
} = useAuctionForm(props, emit)
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

                <div class="space-y-2">
                    <label class="block text-sm font-medium text-slate-300">Katılımcı Cinsiyet Koşulu</label>
                    <div class="relative">
                        <button
                            type="button"
                            @click="showGenderDropdown = !showGenderDropdown"
                            class="w-full flex items-center justify-between px-4 py-2.5 rounded-lg border border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-background-dark text-sm font-medium transition-colors"
                        >
                            <span>{{ getAllowedGenderLabel(form.allowed_gender) }}</span>
                            <span class="material-symbols-outlined" style="font-size: 18px;">expand_more</span>
                        </button>
                        <div v-if="showGenderDropdown" class="absolute top-full right-0 mt-2 w-full bg-white dark:bg-[#1a2230] rounded-lg shadow-xl border border-slate-200 dark:border-slate-800 z-50 py-1">
                            <button
                                v-for="option in GENDER_OPTIONS"
                                :key="option.value"
                                type="button"
                                @click="form.allowed_gender = option.value; showGenderDropdown = false"
                                class="w-full text-left px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-[#232d3f]"
                            >
                                {{ option.label }}
                            </button>
                        </div>
                    </div>
                    <p class="text-xs text-slate-400">Bu koşul, oturumu kimlerin “Hemen Kap” yapabileceğini belirler.</p>
                </div>
            </div>

            <div class="hh-glass-card rounded-xl p-4 space-y-4">
                <h4 class="text-white font-semibold">Zamanlama</h4>
                <p class="text-xs text-slate-400">Alanları sırasıyla doldurun. Her bir alan bir öncekinin doldurulmasını gerektirmektedir.</p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="space-y-2">
                        <label class="block text-sm font-medium text-slate-300">
                            Açık Artırma Başlangıcı
                            <span v-if="isStartTimeValidCheck()" class="text-green-400 ml-1">✓</span>
                        </label>
                        <input
                            v-model="form.start_time"
                            type="datetime-local"
                            required
                            :min="minDateTime"
                            class="w-full bg-dark-bg/60 border border-slate-600 rounded-lg px-3 py-2.5 text-white focus:outline-none focus:border-neon-blue cursor-pointer"
                            @click="$event.target.showPicker && $event.target.showPicker()"
                            @focus="$event.target.showPicker && $event.target.showPicker()"
                            @keydown.prevent
                            @paste.prevent
                            @drop.prevent
                        />
                        <p class="text-xs text-slate-400">Açık artırmanın başlayacağı zaman</p>
                    </div>
                    <div class="space-y-2">
                        <label class="block text-sm font-medium" :class="isStartTimeValidCheck() ? 'text-slate-300' : 'text-slate-500'">
                            Açık Artırma Bitişi
                            <span v-if="isEndTimeValidCheck()" class="text-green-400 ml-1">✓</span>
                            <span v-else-if="!isStartTimeValidCheck()" class="text-slate-400 ml-1">🔒</span>
                        </label>
                        <input
                            v-model="form.end_time"
                            type="datetime-local"
                            required
                            :disabled="!isStartTimeValidCheck()"
                            :min="form.start_time || minDateTime"
                            :class="[
                                'w-full rounded-lg px-3 py-2.5 focus:outline-none transition-colors',
                                isStartTimeValidCheck()
                                    ? 'bg-dark-bg/60 border border-slate-600 text-white focus:border-neon-blue cursor-pointer'
                                    : 'bg-slate-700/30 border border-slate-700 text-slate-400 cursor-not-allowed opacity-60'
                            ]"
                            @click="$event.target.showPicker && $event.target.showPicker()"
                            @focus="$event.target.showPicker && $event.target.showPicker()"
                            @keydown.prevent
                            @paste.prevent
                            @drop.prevent
                        />
                        <p v-if="!isStartTimeValidCheck()" class="text-xs text-slate-500">
                            ⓘ Açık Artırma Başlangıcını seçtikten sonra etkinleştirilecek
                        </p>
                        <p v-else class="text-xs text-slate-400">Açık artırmanın sona ereceği zaman</p>
                    </div>
                </div>

                <div class="space-y-2">
                    <label class="block text-sm font-medium" :class="isEndTimeValidCheck() ? 'text-slate-300' : 'text-slate-500'">
                        Hizmet Zamanı (Oturum Saati)
                        <span v-if="isScheduledAtValidCheck()" class="text-green-400 ml-1">✓</span>
                        <span v-else-if="!isEndTimeValidCheck()" class="text-slate-400 ml-1">🔒</span>
                    </label>
                    <input
                        v-model="form.scheduled_at"
                        type="datetime-local"
                        :disabled="!isEndTimeValidCheck()"
                        :min="form.end_time || minDateTime"
                        :class="[
                            'w-full rounded-lg px-3 py-2.5 focus:outline-none transition-colors',
                            isEndTimeValidCheck()
                                ? 'bg-dark-bg/60 border border-slate-600 text-white focus:border-neon-blue cursor-pointer'
                                : 'bg-slate-700/30 border border-slate-700 text-slate-400 cursor-not-allowed opacity-60'
                        ]"
                        @click="$event.target.showPicker && $event.target.showPicker()"
                        @focus="$event.target.showPicker && $event.target.showPicker()"
                    />
                    <p v-if="!isEndTimeValidCheck()" class="text-xs text-slate-500">
                        ⓘ Açık Artırma Bitişini seçtikten sonra etkinleştirilecek
                    </p>
                    <p v-else class="text-xs text-slate-400">Hizmetin fiilen gerçekleşeceği zaman. <strong>Açık Artırma Bitişi'nden sonra</strong> olmalıdır. Boş bırakılırsa Açık Artırma Bitişi tarihi kullanılır.</p>
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
