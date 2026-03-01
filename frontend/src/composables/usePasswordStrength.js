/**
 * usePasswordStrength — Şifre gücü hesaplama composable'ı.
 *
 * SignUpView ve ProfileView'daki tekrar eden şifre gücü fonksiyonlarını
 * tek bir yerde toplar.
 *
 * Kullanım:
 *   import { usePasswordStrength } from '@/composables/usePasswordStrength'
 *   const { getPasswordStrength, getPasswordStrengthLabel, getPasswordStrengthColor } = usePasswordStrength(passwordRef)
 */

/**
 * @param {import('vue').Ref<string>} passwordRef  - Şifre değerini tutan ref
 */
export function usePasswordStrength(passwordRef) {
  /**
   * 0–5 arası sayısal güç skoru döner.
   * @returns {number}
   */
  const getPasswordStrength = () => {
    const pwd = passwordRef.value ?? ''
    let strength = 0
    if (pwd.length >= 8) strength++
    if (pwd.length >= 12) strength++
    if (/[a-z]/.test(pwd) && /[A-Z]/.test(pwd)) strength++
    if (/\d/.test(pwd)) strength++
    if (/[^a-zA-Z\d]/.test(pwd)) strength++
    return strength
  }

  /**
   * Güç skoruna karşılık gelen Türkçe etiketi döner.
   * @returns {string}
   */
  const getPasswordStrengthLabel = () => {
    const labels = ['', 'Zayıf', 'Orta', 'İyi', 'Güçlü', 'Çok Güçlü']
    return labels[getPasswordStrength()] || ''
  }

  /**
   * Güç skoruna karşılık gelen Tailwind metin renk sınıfını döner.
   * @returns {string}
   */
  const getPasswordStrengthColor = () => {
    const colors = ['', 'text-red-500', 'text-amber-500', 'text-yellow-400', 'text-neon-green', 'text-green-400']
    return colors[getPasswordStrength()] || ''
  }

  return {
    getPasswordStrength,
    getPasswordStrengthLabel,
    getPasswordStrengthColor
  }
}
