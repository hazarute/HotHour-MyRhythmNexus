import sys
import os
import asyncio
from datetime import datetime, timedelta, timezone

# Add parent directory to sys.path to import app module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.db import db

async def seed_auctions():
    print("Veritabanına bağlanılıyor...")
    await db.connect()
    
    print("Mevcut oturumlar temizleniyor...")
    # İsteğe bağlı: Temiz bir sayfa için önceki verileri silebiliriz ama 
    # foreign key constrainleri (reservations) yüzünden dikkatli olmalıyız.
    # Şimdilik sadece ekiyoruz.
    
    now = datetime.now(timezone.utc)
    
    auctions_data = [
        {
            "title": "Sabah Pilates Reformer",
            "description": "Güne enerjik başlamak için birebir. Esra Hoca ile core bölgesini güçlendir.",
            "startPrice": 500.00,
            "floorPrice": 250.00,
            "currentPrice": 480.00, # Biraz düşmüş
            "startTime": now - timedelta(minutes=15), # 15 dk önce başladı
            "endTime": now + timedelta(minutes=45),   # 45 dk sonra bitecek
            "dropIntervalMins": 5,
            "dropAmount": 10.00,
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboTriggerMins": 10,
            "turboDropAmount": 20.00,
            "turboIntervalMins": 2
        },
        {
            "title": "Advanced Yoga Flow",
            "description": "İleri seviye asanalar ve akış serileri. Deneyimli katılımcılar için.",
            "startPrice": 400.00,
            "floorPrice": 200.00,
            "currentPrice": 400.00,
            "startTime": now + timedelta(hours=2), # 2 saat sonra başlayacak
            "endTime": now + timedelta(hours=3),
            "dropIntervalMins": 10,
            "dropAmount": 20.00,
            "status": "ACTIVE", # Henüz başlamadı ama 'ACTIVE' statüsünde listelenebilir (veya DRAFT/SCHEDULED mantığına göre değişir, şimdilik ACTIVE yapalım ki listede görünsün ama fiyatı düşmesin)
            "turboEnabled": False
        },
        {
            "title": "HIIT Cardio Burn",
            "description": "30 dakikalık yüksek yoğunluklu antrenman. Terlemeye hazır olun!",
            "startPrice": 300.00,
            "floorPrice": 100.00,
            "currentPrice": 120.00, 
            "startTime": now - timedelta(minutes=50),
            "endTime": now + timedelta(minutes=10), 
            "dropIntervalMins": 2,
            "dropAmount": 5.00,
            "status": "ACTIVE",
            "turboEnabled": True,
            "turboStartedAt": now - timedelta(minutes=5), # Turbo 5 dk önce başladı
        },
        {
            "title": "Akşam Yogası - Rahatlama",
            "description": "Günün stresini atmak için yavaş akış ve meditasyon.",
            "startPrice": 350.00,
            "floorPrice": 150.00,
            "currentPrice": 350.00,
            "startTime": now + timedelta(days=1, hours=19), # Yarın akşam
            "endTime": now + timedelta(days=1, hours=20),
            "dropIntervalMins": 15,
            "dropAmount": 15.00,
            "status": "ACTIVE",
            "turboEnabled": False
        },
        {
            "title": "Özel Hamile Pilatesi",
            "description": "Güvenli ve etkili egzersizlerle hamilelik sürecini destekleyin.",
            "startPrice": 600.00,
            "floorPrice": 400.00,
            "currentPrice": 450.00,
            "startTime": now - timedelta(hours=3),
            "endTime": now - timedelta(hours=2),
            "dropIntervalMins": 10,
            "dropAmount": 25.00,
            "status": "SOLD", # Satılmış
            "turboEnabled": False
        },
        {
            "title": "Total Body Strength",
            "description": "Tüm vücut kas gruplarını çalıştıran ağırlık antrenmanı.",
            "startPrice": 450.00,
            "floorPrice": 225.00,
            "currentPrice": 225.00,
            "startTime": now - timedelta(days=1),
            "endTime": now - timedelta(days=1, hours=1),
            "dropIntervalMins": 5,
            "dropAmount": 10.00,
            "status": "EXPIRED", # Süresi dolmuş
            "turboEnabled": False
        }
    ]

    for data in auctions_data:
        try:
            auction = await db.auction.create(data=data)
            print(f"Oluşturuldu: {auction.title} - ID: {auction.id}")
        except Exception as e:
            print(f"Hata oluştu ({data['title']}): {e}")

    await db.disconnect()
    print("\nVeri ekleme tamamlandı! 🚀")

if __name__ == "__main__":
    asyncio.run(seed_auctions())
