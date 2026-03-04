import streamlit as st
import pandas as pd
import random
import time
import os
from datetime import datetime, timedelta

st.set_page_config(page_title="5. Sınıf Deneme Sınavı", layout="wide")

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

DERSLER = {
"Türkçe": {"soru": 15, "katsayi": 4, "konular": ["Sözcükte Anlam", "Cümlede Anlam", "Paragraf", "Yazım Kuralları", "Noktalama"]},
"Matematik": {"soru": 15, "katsayi": 4, "konular": ["Doğal Sayılar", "Kesirler", "Ondalık Gösterim", "Yüzdeler", "Geometri"]},
"Fen Bilgisi": {"soru": 10, "katsayi": 4, "konular": ["Güneş Dünya Ay", "Canlılar", "Kuvvetin Ölçülmesi", "Madde ve Değişim"]},
"Sosyal Bilgiler": {"soru": 10, "katsayi": 1, "konular": ["Birey ve Toplum", "Kültür ve Miras", "İnsanlar ve Yerler"]},
"İngilizce": {"soru": 10, "katsayi": 1, "konular": ["Hello!", "My Town", "Games and Hobbies", "Health"]},
"Din Kültürü": {"soru": 10, "katsayi": 1, "konular": ["Allah İnancı", "Ramazan ve Oruç", "Adap ve Nezaket"]}
}

if 'sinav_basladi' not in st.session_state:
st.session_state.sinav_basladi = False
if 'sorular' not in st.session_state:
st.session_state.sorular = []
if 'cevaplar' not in st.session_state:
st.session_state.cevaplar = {}
if 'bitis_zamani' not in st.session_state:
st.session_state.bitis_zamani = None

@st.cache_data
def excel_sorularini_yukle():
try:
df = pd.read_excel("soru_bankasi.xlsx")
return df
except Exception as e:
return None

def soru_olustur(zorluk):
df = excel_sorularini_yukle()
soru_listesi = []
id_sayac = 0

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

if not st.session_state.sinav_basladi:
st.title("🎯 5. Sınıf Deneme Sınavı Portalı")
st.info("💡 Hazırladığınız 'soru_bankasi.xlsx' ve varsa soru görsellerini GitHub'a yüklemeyi unutmayın.")

else:
kalan_sure = st.session_state.bitis_zamani - datetime.now()
dakika = int(kalan_sure.total_seconds() // 60)
saniye = int(kalan_sure.total_seconds() % 60)

if st.session_state.sinav_basladi == "BİTTİ":
st.balloons()
st.title("📊 Sınav Sonuç Analizi")
