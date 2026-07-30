# SGB → FortiGate Threat Feed

Bu repository, Türkiye Siber Güvenlik Başkanlığı API'sinden IP göstergelerini
çeker ve FortiGate'in *External Resource* olarak okuyabileceği yalın metin
listesini `feeds/ip.txt` içinde yayımlar. Her satırda tek bir IPv4 adresi
bulunur; tekrarlar ve geçersiz değerler çıkarılır.

GitHub Actions bu listeyi saatte bir üretir ve yalnızca `feeds/ip.txt`
değiştiğinde commit eder. GitHub Actions zamanlamaları UTC'dir ve yoğun
dönemlerde gecikebilir; FortiGate tarafında daha sık yenileme ayarlamak yeni
veri yaratmaz.

## FortiGate 100F / FortiOS 7.2.13 kurulumu

Repository'nin **public** olması gerekir; FortiGate, GitHub kimlik doğrulaması
yapmadan ham dosyayı indirir. Aşağıdaki URL'de `OWNER` ve `REPOSITORY`
değerlerini kendi GitHub bilgilerinle değiştir:

```
https://raw.githubusercontent.com/ufuksimsekk/sgb-threat-feed/refs/heads/main/feeds/ip.txt
```

FortiGate CLI'da bir external resource oluştur:

```
config system external-resource
    edit "SGB-Threat-IPs"
        set type address
        set resource "https://raw.githubusercontent.com/ufuksimsekk/sgb-threat-feed/refs/heads/main/feeds/ip.txt"
        set refresh-rate 60
        set status enable
        set comments "SGB API-generated IPv4 threat feed"
    next
end
```

Ardından bu nesneyi engelleme politikasında **destination address** olarak
kullan. İç ağdan internete çıkışı engellemek için örnek politika:

```
config firewall policy
    edit 0
        set name "Block-SGB-Threat-IPs"
        set srcintf "<LAN_INTERFACE>"
        set dstintf "<WAN_INTERFACE>"
        set srcaddr "all"
        set dstaddr "SGB-Threat-IPs"
        set action deny
        set schedule "always"
        set service "ALL"
        set logtraffic all
    next
end
```

Bu kuralı genel internet erişimine izin veren policy'nin **üstüne** koy.
Üretim öncesi önce sınırlı bir test istemcisiyle doğrulamak iyi olur. External
resource, HTTP/HTTPS üzerinden satır başına bir IP olacak biçimde dinamik
listeler alır; FortiOS'ta maksimum kaynak boyutu 10 MB veya 131.072 girdidir.

## Yerelde çalıştırma

```
python -m pip install -r requirements.txt
python scripts/generate_feed.py
python -m unittest discover -s tests
```

`scripts/main.py` önceki deneme betiğidir; otomasyon yalnızca
`scripts/generate_feed.py` kullanır.
