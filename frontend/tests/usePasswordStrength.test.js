import { ref } from 'vue'
import { describe, it, expect } from 'vitest'
import { usePasswordStrength } from '@/composables/usePasswordStrength'

describe('usePasswordStrength', () => {

  const make = (initialValue = '') => {
    const pw = ref(initialValue)
    const helpers = usePasswordStrength(pw)
    return { pw, ...helpers }
  }

  // ─── getPasswordStrength ─────────────────────────────────────────────────

  describe('getPasswordStrength', () => {
    it('boş şifre için 0 döner', () => {
      const { getPasswordStrength } = make('')
      expect(getPasswordStrength()).toBe(0)
    })

    it('7 karakterli şifre (sadece küçük harf) için 0 döner', () => {
      const { getPasswordStrength } = make('abcdefg')
      expect(getPasswordStrength()).toBe(0)
    })

    it('sadece 8 küçük harf için 1 döner', () => {
      const { getPasswordStrength } = make('abcdefgh')
      expect(getPasswordStrength()).toBe(1)
    })

    it('8+ karakter ve büyük/küçük harf için 2 döner', () => {
      const { getPasswordStrength } = make('Abcdefgh')
      expect(getPasswordStrength()).toBe(2)
    })

    it('8+ karakter, büyük/küçük harf ve rakam için 3 döner', () => {
      const { getPasswordStrength } = make('Abcdefg1')
      expect(getPasswordStrength()).toBe(3)
    })

    it('12+ karakter, büyük/küçük harf, rakam için 4 döner', () => {
      const { getPasswordStrength } = make('Abcdefghijk1')
      expect(getPasswordStrength()).toBe(4)
    })

    it('tüm kriterler sağlandığında 5 döner', () => {
      const { getPasswordStrength } = make('Abcdefghijk1!')
      expect(getPasswordStrength()).toBe(5)
    })

    it('ref değeri değişince sonuç güncellenir (reaktivite)', () => {
      const { pw, getPasswordStrength } = make('')
      expect(getPasswordStrength()).toBe(0)
      pw.value = 'Abcdefghijk1!'
      expect(getPasswordStrength()).toBe(5)
    })
  })

  // ─── getPasswordStrengthLabel ─────────────────────────────────────────────

  describe('getPasswordStrengthLabel', () => {
    it('güç 0 için boş string döner', () => {
      const { getPasswordStrengthLabel } = make('')
      expect(getPasswordStrengthLabel()).toBe('')
    })

    it('güç 1 için "Zayıf" döner', () => {
      const { getPasswordStrengthLabel } = make('abcdefgh')
      expect(getPasswordStrengthLabel()).toBe('Zayıf')
    })

    it('güç 2 için "Orta" döner', () => {
      const { getPasswordStrengthLabel } = make('Abcdefgh')
      expect(getPasswordStrengthLabel()).toBe('Orta')
    })

    it('güç 3 için "İyi" döner', () => {
      const { getPasswordStrengthLabel } = make('Abcdefg1')
      expect(getPasswordStrengthLabel()).toBe('İyi')
    })

    it('güç 4 için "Güçlü" döner', () => {
      const { getPasswordStrengthLabel } = make('Abcdefghijk1')
      expect(getPasswordStrengthLabel()).toBe('Güçlü')
    })

    it('güç 5 için "Çok Güçlü" döner', () => {
      const { getPasswordStrengthLabel } = make('Abcdefghijk1!')
      expect(getPasswordStrengthLabel()).toBe('Çok Güçlü')
    })
  })

  // ─── getPasswordStrengthColor ─────────────────────────────────────────────

  describe('getPasswordStrengthColor', () => {
    it('güç 0 için boş string döner', () => {
      const { getPasswordStrengthColor } = make('')
      expect(getPasswordStrengthColor()).toBe('')
    })

    it('güç 1 için text-red-500 döner', () => {
      const { getPasswordStrengthColor } = make('abcdefgh')
      expect(getPasswordStrengthColor()).toBe('text-red-500')
    })

    it('güç 2 için text-amber-500 döner', () => {
      const { getPasswordStrengthColor } = make('Abcdefgh')
      expect(getPasswordStrengthColor()).toBe('text-amber-500')
    })

    it('güç 3 için text-yellow-400 döner', () => {
      const { getPasswordStrengthColor } = make('Abcdefg1')
      expect(getPasswordStrengthColor()).toBe('text-yellow-400')
    })

    it('güç 4 için text-neon-green döner', () => {
      const { getPasswordStrengthColor } = make('Abcdefghijk1')
      expect(getPasswordStrengthColor()).toBe('text-neon-green')
    })

    it('güç 5 için text-green-400 döner', () => {
      const { getPasswordStrengthColor } = make('Abcdefghijk1!')
      expect(getPasswordStrengthColor()).toBe('text-green-400')
    })
  })

  // ─── Dönen API Yapısı ─────────────────────────────────────────────────────

  describe('dönen obje yapısı', () => {
    it('üç fonksiyon barındırır', () => {
      const result = usePasswordStrength(ref(''))
      expect(typeof result.getPasswordStrength).toBe('function')
      expect(typeof result.getPasswordStrengthLabel).toBe('function')
      expect(typeof result.getPasswordStrengthColor).toBe('function')
    })
  })

})
