const toTimestamp = (value) => {
  if (!value) return 0
  const timestamp = new Date(value).getTime()
  return Number.isNaN(timestamp) ? 0 : timestamp
}

const sortByNewestFields = (list, dateFields) => {
  return [...list].sort((a, b) => {
    const aTime = toTimestamp(dateFields.map((field) => a?.[field]).find(Boolean))
    const bTime = toTimestamp(dateFields.map((field) => b?.[field]).find(Boolean))

    if (bTime !== aTime) return bTime - aTime
    return Number(b?.id || 0) - Number(a?.id || 0)
  })
}

export const sortAuctionsByNewest = (auctions) => {
  return sortByNewestFields(auctions, ['updated_at', 'updatedAt', 'created_at', 'createdAt'])
}

export const sortReservationsByNewest = (reservations) => {
  return sortByNewestFields(reservations, ['reserved_at', 'reservedAt', 'created_at', 'createdAt'])
}
