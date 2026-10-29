# SimpleMtkWlan - MT7920 test sürümü

Laptop: Acer Nitro V15 ANV15-52, Wi-Fi kartı MediaTek MT7920 (PCI 14c3:7920).

## Durum

- PCI ID eklendi (`Info.plist`, `MtkMwx.cpp`).
- MT7920 için firmware seçimi eklendi (`mwx-mt7961_patch_mcu_1a_2_hdr`, `mwx-mt7961_ram_code_1a`).
- Firmware dosyaları gömüldü (`include/FwBinary.cpp`): `WIFI_RAM_CODE_MT7961_1a.bin` (802 808 bayt) ve `WIFI_MT7961_patch_mcu_1a_2_hdr.bin` (100 384 bayt). Dizi boyutları bildirilen uzunluklarla eşleşiyor.
- Derlenmedi. Derleme macOS ister.
- Donanımda test edilmedi.

## Değişiklik dayanakları

Linux mt76 (commit 8114eea) MT7920'yi MT7921 ile aynı connac2 ailesinde sayıyor ve `MT7920_FIRMWARE_WM` / `MT7920_ROM_PATCH` değerlerini kullanıyor. Repo: https://github.com/morrownr/mt76

## Dosyalar

- `MT7920-changes.diff`: Kod değişikliklerinin diff'i. `FwBinary.cpp` içindeki firmware dizileri diff'te yok (çok büyük).
- `.github/workflows/build-kext.yml`: GitHub Actions macOS çalıştırıcısında kext'i derler ve artifact olarak yükler. İlk çalıştırmada Xcode/SDK hataları çıkabilir.
- `test-mt7920.sh`: Kurulumdan sonra kext'i `kmutil` ile yükler, kartı ve sürücü günlüğünü gösterir. OpenCore'a dokunmaz. Geri almak için: `sudo rm -rf "/Library/Application Support/MtkWlan"` ve yeniden başlatma.
- `embed_mt7920_fw.py`: Firmware'i `FwBinary.cpp` içine gömer. Zaten gömülüyse durur.

## Hâlâ eksik

1. Derleme: GitHub deposu (build-kext.yml) ya da macOS + Xcode.
2. Kurulumu tamamlanmış bir macOS (test için).

## Riskler

- Firmware sürümü ve kart davranışı MT7920 için doğrulanmadı. Kart bağlantıyı reddedebilir.
- Firmware çökerse kartı kapatmak için tam kapanış ve 10–15 sn bekleme gerekebilir (upstream README).
- Kötü bir durumda kernel panic olabilir. Kext'i kaldırmak ve yeniden başlatmak yeterli.
- Bluetooth bu kext ile çalışmaz.

## Kaynaklar

- Upstream: https://github.com/eiyuumiru/SimpleMtkWlan
- Linux mt76: https://github.com/morrownr/mt76
