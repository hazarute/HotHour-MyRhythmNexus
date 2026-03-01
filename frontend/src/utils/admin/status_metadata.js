export const AUCTION_STATUS_LABELS = {
    'DRAFT': 'TASLAK',
    'ACTIVE': 'AKTİF',
    'SOLD': 'SATILDI',
    'EXPIRED': 'SÜRESİ DOLDU',
    'CANCELLED': 'İPTAL EDİLDİ'
}

export const getAuctionStatusMeta = (status) => {
    switch (status) {
        case 'ACTIVE':
            return { label: 'AKTİF', class: 'bg-primary/10 text-primary border-primary/20 shadow-[0_0_10px_rgba(37,106,244,0.15)]', dot: 'bg-primary' }
        case 'SOLD':
            return { label: 'SATILDI', class: 'bg-[#0bda5e]/10 text-[#0bda5e] border-[#0bda5e]/20 shadow-[0_0_10px_rgba(11,218,94,0.15)]', dot: 'bg-[#0bda5e]' }
        case 'EXPIRED':
            return { label: 'SÜRESİ DOLDU', class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300 border-amber-200 dark:border-amber-800', dot: 'bg-amber-500' }
        case 'CANCELLED':
            return { label: 'İPTAL EDİLDİ', class: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300 border-red-200 dark:border-red-800', dot: 'bg-red-500' }
        case 'DRAFT':
        default:
            return { label: status === 'DRAFT' ? 'TASLAK' : (status || 'BİLİNMİYOR'), class: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300 border-slate-200 dark:border-slate-700', dot: 'bg-slate-500' }
    }
}

export const getReservationStatusMeta = (status) => {
    switch(status) {
        case 'COMPLETED':
        case 'CHECKED_IN':
            return { label: 'Giriş Yapıldı', class: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300', dot: 'bg-green-500' }
        case 'PENDING_ON_SITE':
        case 'CONFIRMED':
            return { label: 'Bekliyor', class: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300', dot: 'bg-amber-500' }
        case 'CANCELLED':
            return { label: 'İptal', class: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300', dot: 'bg-red-500' }
        default:
            return { label: status, class: 'bg-slate-100 text-slate-800 dark:bg-slate-800 dark:text-slate-300', dot: 'bg-slate-500' }
    }
}

export const getAllowedGenderLabel = (auction) => {
    const value = String(auction?.allowed_gender || auction?.allowedGender || 'ANY').toUpperCase()
    if (value === 'FEMALE') return 'Kadın'
    if (value === 'MALE') return 'Erkek'
    return 'Karışık'
}

export const RESERVATION_FILTERS = {
    'ALL': 'Tümü',
    'PENDING_ON_SITE': 'Bekliyor',
    'CONFIRMED': 'Onaylandı',
    'COMPLETED': 'Giriş Yapıldı',
    'CHECKED_IN': 'Giriş Yapıldı',
    'CANCELLED': 'İptal'
}