import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
import unicodedata
from typing import List, Optional

# Sayfa konfigürasyonu
st.set_page_config(
    page_title="Excel Dönüştürücü", 
    page_icon="📊", 
    layout="wide"
)

# CSS için stil
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    .stButton > button {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(45deg, #5a6fd8, #6a4190);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    .info-box {
        background: linear-gradient(135deg, #667eea20, #764ba220);
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def normalize_str(s: str) -> str:
    """String normalizasyonu"""
    if not isinstance(s, str):
        return ""
    s = s.strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s

def find_column(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    """Sütun bulma fonksiyonu"""
    col_map = {normalize_str(c): c for c in df.columns}
    for cand in candidates:
        n = normalize_str(cand)
        if n in col_map:
            return col_map[n]
    return None

def transform_df(df: pd.DataFrame) -> pd.DataFrame:
    """Excel dönüştürme fonksiyonu"""
    # Sütun adayları
    barkod_col = find_column(df, ['Barkod', 'barcode', 'barkod'])
    urun_adi_col = find_column(df, ['Ürün Adı', 'Urun Adı', 'Ürün adı', 'urun adı', 'product name', 'ürün adı'])
    tedarikci_col = find_column(df, ['Tedarikçi Stok Kodu', 'Tedarikci Stok Kodu', 'Satıcı Stok Kodu', 'Satici Stok Kodu', 'supplier stock code'])

    if barkod_col is None:
        raise ValueError("❌ Girdi dosyasında 'Barkod' sütunu bulunamadı!")

    # Barkod'ı string'e çevir
    barkod_series = df[barkod_col].fillna('').astype(str).str.strip()

    # Satıcı/Tedarikçi sütunu
    if tedarikci_col is not None and tedarikci_col in df.columns:
        raw_satici = df[tedarikci_col]
        satici_series = raw_satici.fillna('').astype(str).str.strip()
        satici_series = satici_series.replace(to_replace=r'^\s*nan\s*$', value='', regex=True)
    else:
        satici_series = pd.Series([''] * len(df), index=df.index)

    # Boş olanları barkod ile doldur
    empty_mask = satici_series.fillna('').astype(str).str.strip() == ''
    satici_series = satici_series.where(~empty_mask, barkod_series)

    # Ürün adı
    if urun_adi_col is not None and urun_adi_col in df.columns:
        urun_adi_series = df[urun_adi_col].fillna('').astype(str).str.strip()
    else:
        urun_adi_series = pd.Series([''] * len(df), index=df.index)

    # Çıktı DataFrame'i oluştur
    output_df = pd.DataFrame({
        'Barkod': barkod_series,
        'Ürün Adı': urun_adi_series,
        'Satıcı Stok Kodu': satici_series,
        'İdefix Satış Fiyatı': 0,
        'Piyasa Satış Fiyatı': 0,
        'Ürün Stok Adedi': 0,
    })

    # Temizlik
    for c in ['Barkod', 'Satıcı Stok Kodu', 'Ürün Adı']:
        output_df[c] = output_df[c].astype(str).str.strip()

    return output_df

def create_sample_excel() -> BytesIO:
    """Örnek Excel dosyası oluştur"""
    col_order = ['Barkod', 'Model Kodu', 'Ürün Rengi', 'Beden', 'Boyut/Ebat', 'Cinsiyet', 'Marka', 'Kategori İsmi',
                 'Tedarikçi Stok Kodu', 'Ürün Adı', 'Ürün Açıklaması', 'KDV Oranı', 'Desi', 'Görsel 1', 'Sevkiyat Süresi']
    
    sample = pd.DataFrame([
        ['111', 'M1', 'Kırmızı', 'L', 'M', 'Erkek', 'MarkaA', 'KategoriA', pd.NA, 'Ürün A', 'Açıklama', 18, 1.0, 'img1.jpg', '3 gün'],
        ['222', 'M2', 'Mavi', 'M', 'M', 'Kadın', 'MarkaB', 'KategoriB', 'ABC-222', 'Ürün B', 'Açıklama B', 8, 1.2, 'img2.jpg', '2 gün'],
        ['333', 'M3', 'Siyah', 'S', 'S', 'Unisex', 'MarkaC', 'KategoriC', '', 'Ürün C', '', 1, 0.5, 'img3.jpg', '1 gün'],
    ], columns=col_order)

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine='openpyxl') as writer:
        sample.to_excel(writer, index=False, sheet_name='Sheet1')
    bio.seek(0)
    return bio

# Şifre kontrolü
def check_password():
    """Şifre kontrolü"""
    if 'password_correct' not in st.session_state:
        st.session_state.password_correct = False
    
    if not st.session_state.password_correct:
        st.title("🔐 Excel Dönüştürücü")
        st.markdown('<div class="info-box"><b>Giriş yapmak için şifre gerekli</b></div>', unsafe_allow_html=True)
        
        password = st.text_input("Şifreyi giriniz:", type="password", key="password_input")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("Giriş Yap", key="login_btn"):
                if password == "idepim65":
                    st.session_state.password_correct = True
                    st.rerun()
                else:
                    st.error("❌ Hatalı şifre!")
        
        return False
    return True

# Ana uygulama
def main():
    if not check_password():
        return
    
    # Başlık
    st.title("📊 Excel Dönüştürücü")
    st.markdown("**Trendyol → İdefix Format Dönüştürücü**")
    
    # Çıkış butonu
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("🚪 Çıkış", key="logout_btn"):
            st.session_state.password_correct = False
            st.rerun()
    
    # Bilgi kutusu
    st.markdown("""
    <div class="info-box">
        <h4>📋 Dönüştürme Formatı:</h4>
        <p><b>Girdi:</b> Trendyol formatı (25 sütun)</p>
        <p><b>Çıktı:</b> İdefix formatı (6 sütun)</p>
        <p><b>Özellik:</b> Tedarikçi Stok Kodu boşsa Barkod ile doldurulur</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Dosya yükleme ve örnek indirme
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "📁 Excel dosyasını yükleyin", 
            type=["xlsx", "xls"],
            help="Trendyol formatındaki Excel dosyanızı seçin"
        )
    
    with col2:
        st.download_button(
            label="📥 Örnek Excel İndir",
            data=create_sample_excel(),
            file_name="ornek_trendyol_format.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    # Dosya işleme
    if uploaded_file is not None:
        try:
            # Dosyayı oku
            with st.spinner("📖 Dosya okunuyor..."):
                df = pd.read_excel(uploaded_file)
            
            st.success(f"✅ Dosya başarıyla okundu! ({len(df)} satır)")
            
            # Sütun bilgilerini göster
            with st.expander("📊 Dosya Bilgileri"):
                st.write(f"**Satır sayısı:** {len(df)}")
                st.write(f"**Sütun sayısı:** {len(df.columns)}")
                st.write("**İlk 5 sütun:**", list(df.columns[:5]))
            
            # Dönüştürme
            with st.spinner("🔄 Dönüştürme yapılıyor..."):
                output_df = transform_df(df)
            
            st.success(f"🎉 Dönüştürme tamamlandı! ({len(output_df)} satır)")
            
            # Önizleme
            st.subheader("👀 Önizleme (İlk 10 satır)")
            st.dataframe(output_df.head(10), use_container_width=True)
            
            # İndirme
            towrite = BytesIO()
            with pd.ExcelWriter(towrite, engine='openpyxl') as writer:
                output_df.to_excel(writer, index=False, sheet_name='İdefix Format')
            towrite.seek(0)
            
            # Dosya adı oluştur
            import datetime
            now = datetime.datetime.now()
            date_str = now.strftime("%Y-%m-%d")
            original_name = uploaded_file.name.replace('.xlsx', '').replace('.xls', '')
            new_filename = f"{original_name}_dönüşmüş_{date_str}.xlsx"
            
            st.download_button(
                label="📥 Dönüştürülmüş Excel'i İndir",
                data=towrite,
                file_name=new_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
        except Exception as e:
            st.error(f"❌ Hata: {str(e)}")
            
if __name__ == "__main__":
    main()
