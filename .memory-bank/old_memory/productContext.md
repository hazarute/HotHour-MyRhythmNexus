# Ürün Bağlamı (Product Context)

## Problem
Boş kalan hizmet slotları doğrudan gelir kaybına dönüşür. HotHour bunu düşen fiyat mantığıyla son dakika talebine çevirir.

## v1.5 Ürün Yönü
Ürün tek dikeyden çıkıp çok sektörlü hizmet platformuna dönüştürülüyor.

İki ana soru artık ürünün merkezinde:
- işletme hangi sektörlerde faaliyet gösteriyor?
- fırsat hangi hizmet kategorisine ait?

## UX Hedefleri
- fiyat düşüşü ve Turbo hissi korunmalı
- canlı veri akışı bozulmamalı
- keşif, sektör ve hizmet kategorisi üzerinden yapılabilmeli
- admin sadece kendi işletmesini yönetebilmeli
- işletme seviyesi veri ile fırsat seviyesi veri birbirine karıştırılmamalı

## Ürün Kararları
- `Studio` tenant çekirdeği olarak kalır
- sektör ve hizmet kategorisi relation tabanlı çözülür
- master taxonomy owner tarafından yönetilir
- admin paneli seçim tabanlıdır, serbest metin yoktur
- işletme sektörleri panelden değiştirilemez; owner müdahalesi gerekir

## Güncel Operasyonel Durum
Şu an hedef yeni özellik eklemekten çok, yapılan köklü değişiklikleri manuel testlerle sağlamlaştırmaktır.

## Operasyonel Riskler
- tenant izolasyonu bozulmamalı
- yanlış sektör/hizmet gösterimi kullanıcı güvenini bozar
- backend ve frontend filtre mantığı ayrışmamalı
- gereksiz açıklama ve dağınık hafıza, sonraki AI için bağlam kaybı üretir
