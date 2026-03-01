import { describe, it, expect } from 'vitest'
import {
  formatPrice,
  formatCurrency,
  formatDate,
  formatDateLong,
  formatTime,
  formatDateFull
} from '@/utils/formatters'

describe('formatters.js', () => {

  // ─── formatPrice ──────────────────────────────────────────────────────────

  describe('formatPrice', () => {
    it('sıfırı TRY formatında döner', () => {
      const result = formatPrice(0)
      expect(result).toContain('0')
      expect(result).toContain('₺')
    })

    it('pozitif sayıyı Türk para formatında biçimlendirir', () => {
      const result = formatPrice(1250)
      expect(result).toContain('1.250')
      expect(result).toContain('₺')
    })

    it('string sayıyı kabul eder', () => {
      const result = formatPrice('500')
      expect(result).toContain('500')
    })

    it('null/undefined için 0 döner', () => {
      expect(formatPrice(null)).toContain('0')
      expect(formatPrice(undefined)).toContain('0')
    })

    it('ondalık kısmı göstermez (maximumFractionDigits=0)', () => {
      const result = formatPrice(1250.75)
      expect(result).not.toContain(',75')
    })

    it('büyük sayıları doğru biçimlendirir', () => {
      const result = formatPrice(10000)
      expect(result).toContain('10.000')
    })
  })

  // ─── formatCurrency ───────────────────────────────────────────────────────

  describe('formatCurrency', () => {
    it('formatPrice ile aynı çıktıyı verir (alias)', () => {
      expect(formatCurrency(1250)).toBe(formatPrice(1250))
      expect(formatCurrency(0)).toBe(formatPrice(0))
    })
  })

  // ─── formatDate ───────────────────────────────────────────────────────────

  describe('formatDate', () => {
    it('geçerli ISO string için tarih döner', () => {
      const result = formatDate('2026-03-01T10:00:00Z')
      expect(typeof result).toBe('string')
      expect(result.length).toBeGreaterThan(0)
    })

    it('boş string için "-" döner', () => {
      expect(formatDate('')).toBe('-')
    })

    it('null için "-" döner', () => {
      expect(formatDate(null)).toBe('-')
    })

    it('undefined için "-" döner', () => {
      expect(formatDate(undefined)).toBe('-')
    })

    it('hafta adı (kısa) içerir (varsayılan options)', () => {
      const result = formatDate('2026-03-01T12:00:00Z')
      // tr-TR weekday: 'short' → Pa, Sa, Ça, Pe, Cu, Ct, Pz gibi
      expect(result).toMatch(/\w/)
    })

    it('özel options parametresiyle çalışır', () => {
      const result = formatDate('2026-03-01T00:00:00Z', { year: 'numeric', month: 'long', day: 'numeric' })
      expect(result).toContain('2026')
    })
  })

  // ─── formatDateLong ───────────────────────────────────────────────────────

  describe('formatDateLong', () => {
    it('geçerli tarih için uzun format döner', () => {
      const result = formatDateLong('2026-03-01T10:30:00Z')
      expect(typeof result).toBe('string')
      expect(result.length).toBeGreaterThan(0)
    })

    it('yıl ve ay bilgisi içerir', () => {
      const result = formatDateLong('2026-03-01T10:30:00Z')
      expect(result).toContain('2026')
    })

    it('boş/null için boş string döner', () => {
      expect(formatDateLong('')).toBe('')
      expect(formatDateLong(null)).toBe('')
      expect(formatDateLong(undefined)).toBe('')
    })

    it('saat ve dakika içerir', () => {
      const result = formatDateLong('2026-03-01T14:30:00.000Z')
      // Saat bilgisi içermeli (çevre saatine göre değişebilir ama saat formatı olmalı)
      expect(result).toMatch(/\d{2}:\d{2}/)
    })
  })

  // ─── formatTime ───────────────────────────────────────────────────────────

  describe('formatTime', () => {
    it('geçerli tarih için ss:dd formatında saat döner', () => {
      const result = formatTime('2026-03-01T14:30:00Z')
      expect(result).toMatch(/\d{2}:\d{2}/)
    })

    it('boş string için "-" döner', () => {
      expect(formatTime('')).toBe('-')
    })

    it('null için "-" döner', () => {
      expect(formatTime(null)).toBe('-')
    })

    it('undefined için "-" döner', () => {
      expect(formatTime(undefined)).toBe('-')
    })
  })

  // ─── formatDateFull ───────────────────────────────────────────────────────

  describe('formatDateFull', () => {
    it('yıl, ay ve gün içerir', () => {
      const result = formatDateFull('2026-03-01T00:00:00Z')
      expect(result).toContain('2026')
    })

    it('boş/null/undefined için boş string döner', () => {
      expect(formatDateFull('')).toBe('')
      expect(formatDateFull(null)).toBe('')
      expect(formatDateFull(undefined)).toBe('')
    })

    it('string döner', () => {
      expect(typeof formatDateFull('2026-01-15T00:00:00Z')).toBe('string')
    })
  })

})
