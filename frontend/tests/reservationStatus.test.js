import { describe, it, expect } from 'vitest'
import {
  getStatusConfig,
  isCompletedStatus,
  isCopyAllowedStatus
} from '@/utils/reservationStatus'

describe('reservationStatus.js', () => {

  // ─── getStatusConfig ──────────────────────────────────────────────────────

  describe('getStatusConfig', () => {

    it('PENDING_ON_SITE için doğru label ve renk döner', () => {
      const config = getStatusConfig('PENDING_ON_SITE')
      expect(config.label).toBe('Ödeme Bekleniyor')
      expect(config.color).toBe('text-neon-green')
      expect(config.border).toContain('neon-green')
      expect(config.bg).toContain('neon-green')
      expect(config.glow).toBeTruthy()
    })

    it('COMPLETED için doğru label ve nötr renk döner', () => {
      const config = getStatusConfig('COMPLETED')
      expect(config.label).toBe('Tamamlandı')
      expect(config.color).toBe('text-slate-400')
      expect(config.glow).toBe('')
    })

    it('CHECKED_IN için doğru label ve mavi renk döner', () => {
      const config = getStatusConfig('CHECKED_IN')
      expect(config.label).toBe('Giriş Yapıldı')
      expect(config.color).toBe('text-neon-blue')
    })

    it('CANCELLED için doğru label ve kırmızı renk döner', () => {
      const config = getStatusConfig('CANCELLED')
      expect(config.label).toBe('İptal Edildi')
      expect(config.color).toBe('text-red-400')
    })

    it('NO_SHOW için doğru label ve turuncu renk döner', () => {
      const config = getStatusConfig('NO_SHOW')
      expect(config.label).toBe('Katılmadı')
      expect(config.color).toBe('text-orange-400')
    })

    it('bilinmeyen durum için güvenli varsayılan döner', () => {
      const config = getStatusConfig('UNKNOWN_STATUS')
      expect(config.label).toBe('UNKNOWN_STATUS')
      expect(config.color).toBe('text-slate-400')
      expect(config.border).toBe('border-slate-700')
      expect(config.bg).toBe('bg-slate-800/50')
    })

    it('boş string için "Bilinmiyor" label döner', () => {
      const config = getStatusConfig('')
      expect(config.label).toBe('Bilinmiyor')
    })

    it('null/undefined için "Bilinmiyor" label döner', () => {
      expect(getStatusConfig(null).label).toBe('Bilinmiyor')
      expect(getStatusConfig(undefined).label).toBe('Bilinmiyor')
    })

    it('dönen obje her zaman 5 alanı içerir', () => {
      const config = getStatusConfig('COMPLETED')
      expect(config).toHaveProperty('label')
      expect(config).toHaveProperty('color')
      expect(config).toHaveProperty('border')
      expect(config).toHaveProperty('bg')
      expect(config).toHaveProperty('glow')
    })
  })

  // ─── isCompletedStatus ────────────────────────────────────────────────────

  describe('isCompletedStatus', () => {
    it('COMPLETED için true döner', () => {
      expect(isCompletedStatus('COMPLETED')).toBe(true)
    })

    it('NO_SHOW için true döner', () => {
      expect(isCompletedStatus('NO_SHOW')).toBe(true)
    })

    it('CANCELLED için true döner', () => {
      expect(isCompletedStatus('CANCELLED')).toBe(true)
    })

    it('PENDING_ON_SITE için false döner', () => {
      expect(isCompletedStatus('PENDING_ON_SITE')).toBe(false)
    })

    it('CHECKED_IN için false döner', () => {
      expect(isCompletedStatus('CHECKED_IN')).toBe(false)
    })

    it('bilinmeyen durum için false döner', () => {
      expect(isCompletedStatus('ACTIVE')).toBe(false)
      expect(isCompletedStatus('')).toBe(false)
    })
  })

  // ─── isCopyAllowedStatus ──────────────────────────────────────────────────

  describe('isCopyAllowedStatus', () => {
    it('PENDING_ON_SITE için true döner', () => {
      expect(isCopyAllowedStatus('PENDING_ON_SITE')).toBe(true)
    })

    it('COMPLETED için false döner', () => {
      expect(isCopyAllowedStatus('COMPLETED')).toBe(false)
    })

    it('CANCELLED için false döner', () => {
      expect(isCopyAllowedStatus('CANCELLED')).toBe(false)
    })

    it('NO_SHOW için false döner', () => {
      expect(isCopyAllowedStatus('NO_SHOW')).toBe(false)
    })

    it('CHECKED_IN için false döner', () => {
      expect(isCopyAllowedStatus('CHECKED_IN')).toBe(false)
    })

    it('boş/null için false döner', () => {
      expect(isCopyAllowedStatus('')).toBe(false)
      expect(isCopyAllowedStatus(null)).toBe(false)
    })
  })

})
