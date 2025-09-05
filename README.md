# 📊 Excel Dönüştürücü

Trendyol formatındaki Excel dosyalarını İdefix formatına dönüştüren web uygulaması.

## 🚀 Canlı Demo

[Uygulamayı Kullan](https://your-app-name.streamlit.app) 

**Şifre:** `idepim65`

## ✨ Özellikler

- 🔐 Şifre korumalı erişim
- 📁 Excel dosya yükleme (.xlsx, .xls)
- 🔄 Otomatik format dönüştürme
- 📥 Dönüştürülmüş dosyayı indirme
- 👀 Canlı önizleme
- 📊 Dosya bilgilerini görüntüleme

## 📋 Dönüştürme Formatı

### Girdi (Trendyol Formatı)
25 sütunlu format:
- Barkod, Model Kodu, Ürün Rengi, Beden, vb.

### Çıktı (İdefix Formatı)  
6 sütunlu format:
1. **Barkod** ← Barkod
2. **Ürün Adı** ← Ürün Adı
3. **Satıcı Stok Kodu** ← Tedarikçi Stok Kodu (boşsa Barkod)
4. **İdefix Satış Fiyatı** ← 0
5. **Piyasa Satış Fiyatı** ← 0
6. **Ürün Stok Adedi** ← 0

## 🛠 Yerel Kurulum

```bash
# Repository'yi klonlayın
git clone https://github.com/your-username/excel-donusturucu.git
cd excel-donusturucu

# Gerekli kütüphaneleri yükleyin
pip install -r requirements.txt

# Uygulamayı çalıştırın
streamlit run app.py
```

## 📧 İletişim

Sorular için: [GitHub Issues](https://github.com/your-username/excel-donusturucu/issues)

---
Made with ❤️ for productivity