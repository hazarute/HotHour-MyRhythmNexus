/**
 * Rezervasyon durum yardımcıları.
 * Durum → label / renk / border / arka plan / glow eşlemesi burada merkezi tutulur.
 * MyReservationsView ve benzeri bileşenler bu dosyadan import eder.
 */

/**
 * @typedef {Object} StatusConfig
 * @property {string} label    - Türkçe görünen metin
 * @property {string} color    - Tailwind metin renk sınıfı
 * @property {string} border   - Tailwind border renk sınıfı
 * @property {string} bg       - Tailwind arka plan renk sınıfı
 * @property {string} glow     - Tailwind shadow/glow sınıfı (boş olabilir)
 */

/** @type {Record<string, StatusConfig>} */
const STATUS_MAP = {
  PENDING_ON_SITE: {
    label: 'Ödeme Bekleniyor',
    color: 'text-neon-green',
    border: 'border-neon-green/50',
    bg: 'bg-neon-green/10',
    glow: 'shadow-[0_0_15px_rgba(54,211,153,0.15)]'
  },
  COMPLETED: {
    label: 'Tamamlandı',
    color: 'text-slate-400',
    border: 'border-slate-700',
    bg: 'bg-slate-800/50',
    glow: ''
  },
  CHECKED_IN: {
    label: 'Giriş Yapıldı',
    color: 'text-neon-blue',
    border: 'border-neon-blue/50',
    bg: 'bg-neon-blue/10',
    glow: ''
  },
  CANCELLED: {
    label: 'İptal Edildi',
    color: 'text-red-400',
    border: 'border-red-900/50',
    bg: 'bg-red-900/10',
    glow: ''
  },
  NO_SHOW: {
    label: 'Katılmadı',
    color: 'text-orange-400',
    border: 'border-orange-900/50',
    bg: 'bg-orange-900/10',
    glow: ''
  }
}

/**
 * Verilen durum için görsel yapılandırmayı döner.
 * Bilinmeyen durumlarda güvenli varsayılan döner.
 * @param {string} status
 * @returns {StatusConfig}
 */
export const getStatusConfig = (status) => {
  return STATUS_MAP[status] ?? {
    label: status || 'Bilinmiyor',
    color: 'text-slate-400',
    border: 'border-slate-700',
    bg: 'bg-slate-800/50',
    glow: ''
  }
}

/**
 * Rezervasyonun "tamamlanmış" (aktif değil) kategorisine girip girmediğini kontrol eder.
 * @param {string} status
 * @returns {boolean}
 */
export const isCompletedStatus = (status) => {
  return ['COMPLETED', 'NO_SHOW', 'CANCELLED'].includes(status)
}

/**
 * Giriş kodu kopyalamanın bu durum için izinli olup olmadığını döner.
 * @param {string} status
 * @returns {boolean}
 */
export const isCopyAllowedStatus = (status) => status === 'PENDING_ON_SITE'
