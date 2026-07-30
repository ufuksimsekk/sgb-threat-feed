# SGB FortiGate Threat Feed

Siber Güvenlik Başkanlığı tarafından yayımlanan zararlı IPv4 göstergelerini
FortiGate External Resource biçiminde sunan otomatik threat-feed projesi.

## Feed

Yayımlanan liste:

```text
https://raw.githubusercontent.com/ufuksimsekk/sgb-threat-feed/main/feeds/ip.txt
```

Kaynak dosya düz metindir; her satır tek bir IPv4 adresi içerir. Feed üretimi:

- SGB API'deki `ip` türündeki kayıtları alır.
- Kritik seviye 1–10 arasındaki tüm göstergeleri kapsar.
- Geçersiz değerleri ve yinelenen IPv4 adreslerini çıkarır.
- Başarısız veya boş API yanıtında mevcut feed'i değiştirmez.
- Çıktıyı sayısal IP sırasıyla ve satır sonu ile yazar.

IPv6, domain ve URL kayıtları bu feed'in kapsamı dışındadır. Bu türler,
FortiGate üzerinde ayrı external resource ve ilgili DNS/Web Filter
politikalarıyla yönetilmelidir.

## FortiGate External Resource

Repository public erişime açıktır. FortiGate 100F üzerinde FortiOS 7.2.13
için IPv4 external resource yapılandırması:

```cli
config system external-resource
    edit "SGB-Threat-IPs"
        set type address
        set resource "https://raw.githubusercontent.com/ufuksimsekk/sgb-threat-feed/main/feeds/ip.txt"
        set refresh-rate 60
        set status enable
        set comments "SGB API-generated IPv4 threat feed"
    next
end
```

`SGB-Threat-IPs` nesnesi, örneğin LAN'dan internete giden trafiği koruyan
engelleme politikasında destination address olarak kullanılır:

```cli
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

Engelleme policy'si, aynı trafiğe izin veren genel internet erişim
policy'lerinden önce konumlandırılmalıdır. FortiGate'in GitHub'a HTTPS
erişimi olmalıdır. FortiOS external resource listelerinde kaynak boyutu
10 MB veya 131.072 giriş ile sınırlıdır.

## Yerel geliştirme

```powershell
python -m pip install -r requirements.txt
python -m unittest discover -s tests
python scripts/generate_feed.py
```

## Repository yapısı

| Yol | Açıklama |
| --- | --- |
| `scripts/generate_feed.py` | SGB API istemcisi ve feed üreticisi |
| `feeds/ip.txt` | FortiGate tarafından indirilen yayımlanmış IPv4 listesi |
| `tests/test_generate_feed.py` | Feed doğrulama ve çıktı biçimi testleri |
| `.github/workflows/update.yml` | Saatlik GitHub Actions güncellemesi |
