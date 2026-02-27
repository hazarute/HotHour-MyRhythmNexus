export const getAuctionField = (auction, snakeKey, camelKey) => {
  if (!auction) return null
  return auction[snakeKey] ?? auction[camelKey] ?? null
}

export const getAuctionStatus = (auction) => {
  return String(auction?.status || '').toUpperCase()
}

export const isAuctionActive = (auction) => getAuctionStatus(auction) === 'ACTIVE'

export const getAuctionCurrentPrice = (auction) => {
  const value =
    getAuctionField(auction, 'current_price', 'currentPrice') ??
    auction?.computedPrice ??
    getAuctionField(auction, 'start_price', 'startPrice') ??
    0
  return Number(value || 0)
}

export const getAuctionStartPrice = (auction) => {
  const value = getAuctionField(auction, 'start_price', 'startPrice')
  if (value !== null && value !== undefined) return Number(value)
  return getAuctionCurrentPrice(auction)
}

export const getAuctionEndTime = (auction) => {
  return getAuctionField(auction, 'end_time', 'endTime')
}

export const isAuctionTurbo = (auction) => {
  const turboStartedAt = getAuctionField(auction, 'turbo_started_at', 'turboStartedAt')
  if (turboStartedAt) return true

  return Boolean(auction?.turboActive)
}
