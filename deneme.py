import streamlit as st
import time
import random
from datetime import datetime, timedelta

# --- YAPILANDIRMA VE STİL ---
st.set_page_config(page_title="5. Sınıf LGS Deneme Sınavı", layout="wide")

# Sağ tarafta yüzen (sticky) sayaç için özel CSS
st.markdown("""
    <style>
    .fixed-timer {
        position: fixed;
        top: 50%;
        right: 20px;
        transform: translateY(-50%);
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 15px;
        border: 2px solid #ff4b4b;
        z-index: 999;
        text-align: center;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.1);
    }
    .stRadio > label { font-size: 1.2rem; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- VERİ YAPILARI (MEB MÜFREDATI) ---
DERSLER = {
    "Türkçe": {"soru": 15, "katsayi": 4, "konular": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım Kuralları", "Noktalama"]},
    "Matematik": {"soru": 15, "katsayi": 4, "konular": ["Doğal Sayılar", "Kesirler", "Ondalık Gösterim", "Yüzdeler", "Geometri"]},
    "Fen Bilgisi": {"soru": 10, "katsayi": 4, "konular": ["Güneş Dünya Ay", "Canlılar", "Kuvvetin Ölçülmesi", "Madde ve Değişim"]},
    "Sosyal Bilgiler": {"soru": 10, "katsayi": 1, "konular": ["Birey ve Toplum", "Kültür ve Miras", "İnsanlar ve Yerler"]},
    "İngilizce": {"soru": 10, "katsayi": 1, "konular": ["Hello!", "My Town", "Games and Hobbies", "Health"]},
    "Din Kültürü": {"soru": 10, "katsayi": 1, "konular": ["Allah İnancı", "Ramazan ve Oruç", "Adap ve Nezaket"]}
}

# --- SESSION STATE (DURUM YÖNETİMİ) ---
if 'sinav_basladi' not in st.session_state:
    st.session_state.sinav_basladi = False
if 'sorular' not in st.session_state:
    st.session_state.sorular = []
if 'cevaplar' not in st.session_state:
    st.session_state.cevaplar = {}
if 'bitis_zamani' not in st.session_state:
    st.session_state.bitis_zamani = None

# --- FONKSİYONLAR ---
def soru_olustur(zorluk):
    soru_listesi = []
    id_sayac = 0
    for ders, bilgi in DERSLER.items():
        for i in range(bilgi["soru"]):
            konu = random.choice(bilgi["konular"])
            soru_listesi.append({
                "id": id_sayac,
                "ders": ders,
                "konu": konu,
                "soru_metni": f"[{zorluk}] {ders} dersi {konu} konusu ile ilgili hazırlanan 5. sınıf sorusu.",
                "secenekler": ["Seçenek A", "Seçenek B", "Seçenek C", "Seçenek D"],
                "dogru": random.choice([0, 1, 2, 3])
            })
            id_sayac += 1
    return soru_listesi

def sinavi_baslat(zorluk):
    st.session_state.sorular = soru_olustur(zorluk)
    st.session_state.cevaplar = {i: None for i in range(70)}
    st.session_state.bitis_zamani = datetime.now() + timedelta(minutes=100)
    st.session_state.sinav_basladi = True

def puan_hesapla():
    analiz = {ders: {"D": 0, "Y": 0, "B": 0, "Konular": set()} for ders in DERSLER.keys()}
    for i, soru in enumerate(st.session_state.sorular):
        cvp = st.session_state.cevaplar[i]
        ders = soru["ders"]
        if cvp is None:
            analiz[ders]["B"] += 1
            analiz[ders]["Konular"].add(soru["konu"])
        elif cvp == soru["secenekler"][soru["dogru"]]:
            analiz[ders]["D"] += 1
        else:
            analiz[ders]["Y"] += 1
            analiz[ders]["Konular"].add(soru["konu"])
    
    # LGS Puan Formülü (Tahmini)
    toplam_agirlikli_net = 0
    for ders, sonuclar in analiz.items():
        net = sonuclar["D"] - (sonuclar["Y"] / 3.0)
        toplam_agirlikli_net += max(0, net) * DERSLER[ders]["katsayi"]
    
    # 5. Sınıf LGS Projeksiyonu: 194 (Taban) + (Netler * Katsayı)
    final_puan = 194 + (toplam_agirlikli_net / 190) * 306
    return analiz, min(500, final_puan)

# --- ARAYÜZ ---

# 1. GİRİŞ EKRANI
if not st.session_state.sinav_basladi:
    st.title("🎯 5. Sınıf Deneme Sınavı Portalı")
    st.write("MEB Yeni Müfredata Uygun - 70 Soru - 100 Dakika")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🟢 KOLAY SEVİYE", use_container_width=True):
            sinavi_baslat("Kolay")
            st.rerun()
    with col2:
        if st.button("🟡 ORTA SEVİYE", use_container_width=True):
            sinavi_baslat("Orta")
            st.rerun()
    with col3:
        if st.button("🔴 ZOR SEVİYE", use_container_width=True):
            sinavi_baslat("Zor")
            st.rerun()

# 2. SINAV EKRANI
else:
    # Sayacı Göster (Sağ Orta)
    kalan_sure = st.session_state.bitis_zamani - datetime.now()
    dakika = int(kalan_sure.total_seconds() // 60)
    saniye = int(kalan_sure.total_seconds() % 60)
    
    if kalan_sure.total_seconds() <= 0:
        st.error("Süre Doldu! Sınav Sonlandırılıyor...")
        time.sleep(2)
        st.session_state.sinav_basladi = "BİTTİ"
        st.rerun()

    st.markdown(f"""
        <div class="fixed-timer">
            <h4 style='margin:0; color:#333;'>KALAN SÜRE</h4>
            <h2 style='margin:0; color:#ff4b4b;'>{dakika:02d}:{saniye:02d}</h2>
        </div>
    """, unsafe_allow_html=True)

    # Soru Gezinme
    st.title("📝 Sınav Uygulaması")
    
    # Derslere göre tablar
    tabs = st.tabs(list(DERSLER.keys()))
    
    soru_index = 0
    for idx, ders_adi in enumerate(DERSLER.keys()):
        with tabs[idx]:
            st.subheader(f"{ders_adi} Bölümü")
            ders_sorulari = [s for s in st.session_state.sorular if s["ders"] == ders_adi]
            
            for s in ders_sorulari:
                key = f"soru_{s['id']}"
                st.write(f"**Soru {soru_index + 1}:** {s['soru_metni']}")
                
                # Cevap seçimi
                secim = st.radio(
                    f"Cevabınızı seçin ({s['id']}):",
                    s["secenekler"],
                    index=None if st.session_state.cevaplar[s['id']] is None else s["secenekler"].index(st.session_state.cevaplar[s['id']]),
                    key=key,
                    label_visibility="collapsed"
                )
                st.session_state.cevaplar[s['id']] = secim
                soru_index += 1
                st.divider()

    if st.button("SINAVI BİTİR VE SONUÇLARI GÖR", type="primary", use_container_width=True):
        st.session_state.sinav_basladi = "BİTTİ"
        st.rerun()

# 3. SONUÇ EKRANI
if st.session_state.sinav_basladi == "BİTTİ":
    st.balloons()
    st.title("📊 Sınav Sonuç Analizi")
    
    analiz, puan = puan_hesapla()
    
    st.metric(label="Tahmini LGS Puanı (500 Üzerinden)", value=f"{puan:.2f}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write("### Ders Bazlı Başarı Durumu")
        for ders, veriler in analiz.items():
            st.write(f"**{ders}:** {veriler['D']} Doğru, {veriler['Y']} Yanlış, {veriler['B']} Boş")
            st.progress(veriler['D'] / DERSLER[ders]['soru'])

    with col2:
        st.write("### 📚 Çalışman Gereken Konular")
        eksik_konular = []
        for ders in analiz:
            for konu in analiz[ders]["Konular"]:
                eksik_konular.append(f"{ders} - {konu}")
        
        if eksik_konular:
            for k in eksik_konular:
                st.warning(k)
        else:
            st.success("Harika! Hiç eksiğin görünmüyor.")

    if st.button("YENİ SINAVA BAŞLA"):
        st.session_state.clear()
        st.rerun()
