/**
 * Merkezi format yardımcı fonksiyonları.
 * Tüm view ve composable'larda bu dosyadan import edilmeli;
 * inline tanımlama yapılmamalıdır.
 */

/**
 * Sayıyı TRY para birimi formatına çevirir.
 * @param {number|string} val
 * @returns {string} ör: "₺1.250"
 */
export const formatPrice = (val) => {
  return new Intl.NumberFormat('tr-TR', {
    style: 'currency',
    currency: 'TRY',
    maximumFractionDigits: 0
  }).format(Number(val || 0))
}

/** formatPrice'ın alias'ı — MyReservationsView uyumluluğu için */
export const formatCurrency = formatPrice

/**
 * ISO tarih string'ini Türkçe tarih olarak formatlar.
 * @param {string} dateStr
 * @param {Intl.DateTimeFormatOptions} [options]
 * @returns {string}
 */
export const formatDate = (dateStr, options = null) => {
  if (!dateStr) return '-'
  const defaultOptions = {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  }
  return new Date(dateStr).toLocaleDateString('tr-TR', options ?? defaultOptions)
}

/**
 * ISO tarih string'ini uzun Türkçe tarih + saat formatına çevirir.
 * AuctionDetailView gibi detay sayfaları için.
 * @param {string} dateStr
 * @returns {string}
 */
export const formatDateLong = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleDateString('tr-TR', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * ISO tarih string'inden sadece saat:dakika çıkarır.
 * @param {string} dateStr
 * @returns {string} ör: "14:30"
 */
export const formatTime = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleTimeString('tr-TR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * ISO tarih string'ini kısa tarih formatına çevirir (yıl dahil).
 * ProfileView / hesap sayfaları için.
 * @param {string} dateString
 * @returns {string}
 */
export const formatDateFull = (dateString) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleDateString('tr-TR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}
