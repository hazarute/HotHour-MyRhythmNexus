import { expect, test } from '@playwright/test'

const auctions = [
  {
    id: 1,
    title: 'Sector X Firsat 1',
    description: 'Ilk rezervasyon yapilan firsat',
    allowedGender: 'ANY',
    status: 'ACTIVE',
    currentPrice: 123,
    startPrice: 200,
    endTime: '2026-03-28T09:50:00Z',
    scheduled_at: '2026-03-28T09:50:00Z',
    studio: { name: 'Studio A' }
  },
  {
    id: 2,
    title: 'Sector X Firsat 2',
    description: 'Ayni sektor farkli hizmet',
    allowedGender: 'ANY',
    status: 'ACTIVE',
    currentPrice: 111,
    startPrice: 220,
    endTime: '2026-03-28T10:50:00Z',
    scheduled_at: '2026-03-28T10:50:00Z',
    studio: { name: 'Studio B' }
  }
]

async function seedAuthenticatedUser(page) {
  await page.addInitScript(() => {
    localStorage.setItem('token', 'E2E_TOKEN')
    localStorage.setItem('refresh_token', 'E2E_REFRESH')
    localStorage.setItem('user', JSON.stringify({ id: 9, role: 'USER', gender: 'FEMALE' }))
  })
}

test.describe('booking abuse flows', () => {
  test('home listesinde ayni sektor kisiti kullaniciya gosterilir', async ({ page }) => {
    await seedAuthenticatedUser(page)

    await page.route('**/api/v1/auctions/**', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(auctions)
      })
    })

    await page.route('**/api/v1/reservations/eligible/2', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz. 10 gun dolmadan ayni sektorden tekrar rezervasyon yapamazsiniz.'
        })
      })
    })

    await page.goto('/')

    await expect(page.getByText('Sector X Firsat 2')).toBeVisible()
    await page.getByRole('button', { name: /Hemen Kap/i }).nth(1).click()

    await expect(page.getByText('Rezervasyon Yapılamıyor')).toBeVisible()
    await expect(page.getByText(/10 gun dolmadan ayni sektorden tekrar rezervasyon yapamazsiniz/i)).toBeVisible()
  })

  test('detay sayfasinda ayni sektor kisiti rezervasyon modalindan once durdurulur', async ({ page }) => {
    await seedAuthenticatedUser(page)

    await page.route('**/api/v1/auctions/2', async (route) => {
      await route.fulfill({
        status: 200,
        contentType: 'application/json',
        body: JSON.stringify(auctions[1])
      })
    })

    await page.route('**/api/v1/reservations/eligible/2', async (route) => {
      await route.fulfill({
        status: 400,
        contentType: 'application/json',
        body: JSON.stringify({
          detail: 'Bu sektorde son 10 gun icinde bir firsat rezerve ettiniz. 10 gun dolmadan ayni sektorden tekrar rezervasyon yapamazsiniz.'
        })
      })
    })

    await page.goto('/auction/2')

    await expect(page.getByText('Sector X Firsat 2')).toBeVisible()
    await page.getByRole('button', { name: /Hemen Kap/i }).click()

    await expect(page.getByText('Rezervasyon Yapılamıyor')).toBeVisible()
    await expect(page.getByText(/ayni sektorden tekrar rezervasyon yapamazsiniz/i)).toBeVisible()
  })
})