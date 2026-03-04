import tkinter as tk
from tkinter import messagebox
import random

# 5. Sınıf MEB Müfredatı Örnek Konuları
MEB_KONULARI = {
    "Türkçe": ["Sözcükte Anlam", "Cümlede Anlam", "Paragrafta Anlam", "Yazım Kuralları", "Noktalama İşaretleri"],
    "Sosyal Bilgiler": ["Birey ve Toplum", "Kültür ve Miras", "İnsanlar, Yerler ve Çevreler", "Bilim, Teknoloji ve Toplum"],
    "Matematik": ["Doğal Sayılar", "Kesirler", "Ondalık Gösterim", "Yüzdeler", "Temel Geometrik Kavramlar"],
    "Fen Bilgisi": ["Güneş, Dünya ve Ay", "Canlılar Dünyası", "Kuvvetin Ölçülmesi", "Madde ve Değişim", "Işığın Yayılması"],
    "İngilizce": ["Hello!", "My Town", "Games and Hobbies", "Health", "Movies"],
    "Din Kültürü": ["Allah İnancı", "Ramazan ve Oruç", "Adap ve Nezaket", "Hz. Muhammed ve Aile Hayatı"]
}

DERS_DAGILIMI = {
    "Türkçe": {"soru_sayisi": 15, "katsayi": 4},
    "Matematik": {"soru_sayisi": 15, "katsayi": 4},
    "Fen Bilgisi": {"soru_sayisi": 10, "katsayi": 4},
    "Sosyal Bilgiler": {"soru_sayisi": 10, "katsayi": 1},
    "İngilizce": {"soru_sayisi": 10, "katsayi": 1},
    "Din Kültürü": {"soru_sayisi": 10, "katsayi": 1}
}

class SinavUygulamasi:
    def __init__(self, root):
        self.root = root
        self.root.title("5. Sınıf Deneme Sınavı")
        self.root.geometry("900x600")
        
        self.sorular = []
        self.kullanici_cevaplari = {}
        self.su_anki_soru_index = 0
        self.kalan_sure = 100 * 60  # 100 dakika
        self.zamanlayici_id = None
        
        self.zorluk_ekrani_olustur()

    def soru_uret(self, zorluk):
        """Seçilen zorluğa göre taslak sorular oluşturur."""
        self.sorular = []
        soru_no = 1
        for ders, detay in DERS_DAGILIMI.items():
            for _ in range(detay["soru_sayisi"]):
                konu = random.choice(MEB_KONULARI[ders])
                soru = {
                    "no": soru_no,
                    "ders": ders,
                    "konu": konu,
                    "soru_metni": f"({zorluk} Seviye) {ders} dersi, {konu} konusu ile ilgili örnek soru metnidir.\nAşağıdakilerden hangisi doğrudur?",
                    "secenekler": ["A) Seçenek 1", "B) Seçenek 2", "C) Seçenek 3", "D) Seçenek 4"],
                    "dogru_cevap": random.choice([0, 1, 2, 3])
                }
                self.sorular.append(soru)
                soru_no += 1

    def zorluk_ekrani_olustur(self):
        self.temizle()
        frame = tk.Frame(self.root)
        frame.pack(expand=True)
        
        tk.Label(frame, text="Deneme Sınavına Hoş Geldiniz", font=("Arial", 20, "bold")).pack(pady=20)
        tk.Label(frame, text="Lütfen sınav zorluk derecesini seçin:", font=("Arial", 14)).pack(pady=10)
        
        tk.Button(frame, text="Kolay", width=20, font=("Arial", 12), command=lambda: self.sinavi_baslat("Kolay")).pack(pady=5)
        tk.Button(frame, text="Orta", width=20, font=("Arial", 12), command=lambda: self.sinavi_baslat("Orta")).pack(pady=5)
        tk.Button(frame, text="Zor", width=20, font=("Arial", 12), command=lambda: self.sinavi_baslat("Zor")).pack(pady=5)

    def sinavi_baslat(self, zorluk):
        self.soru_uret(zorluk)
        self.kullanici_cevaplari = {i: -1 for i in range(len(self.sorular))}  # -1 boş bırakılmış demek
        self.su_anki_soru_index = 0
        self.kalan_sure = 100 * 60
        self.arayuzu_olustur()
        self.zamanlayiciyi_baslat()
        self.soruyu_goster()

    def arayuzu_olustur(self):
        self.temizle()
        
        # Ana Bölme Düzeni
        self.sol_frame = tk.Frame(self.root, padx=20, pady=20)
        self.sol_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.sag_frame = tk.Frame(self.root, width=200, bg="#f0f0f0", relief=tk.RAISED, borderwidth=2)
        self.sag_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.sag_frame.pack_propagate(False)

        # Sağ Taraf - Sayaç (Sayfanın sağ orta kısmı)
        ortala_frame = tk.Frame(self.sag_frame, bg="#f0f0f0")
        ortala_frame.pack(expand=True)
        
        tk.Label(ortala_frame, text="Kalan Süre", font=("Arial", 14), bg="#f0f0f0").pack()
        self.sure_etiketi = tk.Label(ortala_frame, text="100:00", font=("Arial", 24, "bold"), fg="red", bg="#f0f0f0")
        self.sure_etiketi.pack(pady=10)
        
        tk.Button(ortala_frame, text="Sınavı Bitir", font=("Arial", 12), bg="#ff4c4c", fg="white", command=self.sinavi_bitir).pack(pady=30)

        # Sol Taraf - Soru Alanı
        self.ders_etiketi = tk.Label(self.sol_frame, text="", font=("Arial", 14, "italic"), fg="blue")
        self.ders_etiketi.pack(anchor="w")
        
        self.soru_etiketi = tk.Label(self.sol_frame, text="", font=("Arial", 16), wraplength=600, justify="left")
        self.soru_etiketi.pack(anchor="w", pady=20)
        
        self.secim_degiskeni = tk.IntVar()
        self.secenek_butonlari = []
        for i in range(4):
            rb = tk.Radiobutton(self.sol_frame, text="", variable=self.secim_degiskeni, value=i, font=("Arial", 14), command=self.cevabi_kaydet)
            rb.pack(anchor="w", pady=5)
            self.secenek_butonlari.append(rb)
            
        # Alt Navigasyon
        nav_frame = tk.Frame(self.sol_frame)
        nav_frame.pack(fill=tk.X, pady=40)
        
        self.btn_onceki = tk.Button(nav_frame, text="<< Önceki Soru", font=("Arial", 12), command=self.onceki_soru)
        self.btn_onceki.pack(side=tk.LEFT)
        
        self.btn_sonraki = tk.Button(nav_frame, text="Sonraki Soru >>", font=("Arial", 12), command=self.sonraki_soru)
        self.btn_sonraki.pack(side=tk.RIGHT)

    def zamanlayiciyi_baslat(self):
        dakika = self.kalan_sure // 60
        saniye = self.kalan_sure % 60
        self.sure_etiketi.config(text=f"{dakika:02d}:{saniye:02d}")
        
        if self.kalan_sure > 0:
            self.kalan_sure -= 1
            self.zamanlayici_id = self.root.after(1000, self.zamanlayiciyi_baslat)
        else:
            self.sinavi_bitir(otomatik=True)

    def soruyu_goster(self):
        soru = self.sorular[self.su_anki_soru_index]
        self.ders_etiketi.config(text=f"{soru['ders']} - Soru {soru['no']}/70")
        self.soru_etiketi.config(text=soru['soru_metni'])
        
        self.secim_degiskeni.set(self.kullanici_cevaplari[self.su_anki_soru_index])
        
        for i in range(4):
            self.secenek_butonlari[i].config(text=soru['secenekler'][i])
            
        self.btn_onceki.config(state=tk.NORMAL if self.su_anki_soru_index > 0 else tk.DISABLED)
        self.btn_sonraki.config(state=tk.NORMAL if self.su_anki_soru_index < len(self.sorular) - 1 else tk.DISABLED)

    def cevabi_kaydet(self):
        self.kullanici_cevaplari[self.su_anki_soru_index] = self.secim_degiskeni.get()

    def onceki_soru(self):
        if self.su_anki_soru_index > 0:
            self.su_anki_soru_index -= 1
            self.soruyu_goster()

    def sonraki_soru(self):
        if self.su_anki_soru_index < len(self.sorular) - 1:
            self.su_anki_soru_index += 1
            self.soruyu_goster()

    def sinavi_bitir(self, otomatik=False):
        if not otomatik:
            cevap = messagebox.askyesno("Sınavı Bitir", "Sınavı bitirmek istediğinize emin misiniz?")
            if not cevap:
                return
                
        if self.zamanlayici_id:
            self.root.after_cancel(self.zamanlayici_id)
            
        self.sonuclari_hesapla()

    def sonuclari_hesapla(self):
        self.temizle()
        
        istatistikler = {ders: {"dogru": 0, "yanlis": 0, "bos": 0, "net": 0.0} for ders in DERS_DAGILIMI.keys()}
        eksik_konular = set()
        
        toplam_dogru = 0
        toplam_yanlis = 0
        toplam_bos = 0

        # Doğru, yanlış, boş ve konu analizi
        for i, soru in enumerate(self.sorular):
            ders = soru["ders"]
            verilen_cevap = self.kullanici_cevaplari[i]
            
            if verilen_cevap == -1:
                istatistikler[ders]["bos"] += 1
                toplam_bos += 1
                eksik_konular.add(f"{ders}: {soru['konu']}")
            elif verilen_cevap == soru["dogru_cevap"]:
                istatistikler[ders]["dogru"] += 1
                toplam_dogru += 1
            else:
                istatistikler[ders]["yanlis"] += 1
                toplam_yanlis += 1
                eksik_konular.add(f"{ders}: {soru['konu']}")

        # 3 Yanlış 1 Doğruyu Götürür Kuralı ve LGS Puanı (500 üzerinden)
        toplam_agirlikli_net = 0
        for ders, data in istatistikler.items():
            net = data["dogru"] - (data["yanlis"] / 3.0)
            data["net"] = max(0, net)
            toplam_agirlikli_net += data["net"] * DERS_DAGILIMI[ders]["katsayi"]
            
        # LGS Taban Puanı 194, Maksimum Ağırlıklı Net Puanı: 190 (Sınav max 500 Puan)
        # Formül: 194 + (Alınan Ağırlıklı Net / 190) * 306
        lgs_puani = 194 + (toplam_agirlikli_net / 190.0) * 306
        if toplam_dogru == 0 and toplam_yanlis == 0:
            lgs_puani = 0 # Hiçbir şey işaretlenmediyse 0

        self.sonuc_ekrani_goster(toplam_dogru, toplam_yanlis, toplam_bos, lgs_puani, eksik_konular)

    def sonuc_ekrani_goster(self, dogru, yanlis, bos, puan, konular):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(frame, text="Sınav Sonucu", font=("Arial", 22, "bold")).pack(pady=10)
        tk.Label(frame, text=f"LGS Tahmini Puanı: {puan:.2f} / 500", font=("Arial", 18, "bold"), fg="green").pack(pady=10)
        
        ozet = f"Toplam Doğru: {dogru}   |   Toplam Yanlış: {yanlis}   |   Boş Bırakılan: {bos}"
        tk.Label(frame, text=ozet, font=("Arial", 14)).pack(pady=10)
        
        if konular:
            tk.Label(frame, text="Tekrar Edilmesi Önerilen Konular:", font=("Arial", 14, "bold"), fg="red").pack(pady=10)
            listbox = tk.Listbox(frame, font=("Arial", 12), width=60, height=12)
            listbox.pack()
            for konu in sorted(listbox_items := list(konular)):
                listbox.insert(tk.END, f"• {konu}")
        else:
            tk.Label(frame, text="Tebrikler! Eksik konunuz bulunmamaktadır.", font=("Arial", 14, "bold"), fg="green").pack(pady=20)
            
        tk.Button(frame, text="Yeni Sınav Başlat", font=("Arial", 12), command=self.zorluk_ekrani_olustur).pack(pady=20)

    def temizle(self):
        for widget in self.root.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SinavUygulamasi(root)
    root.mainloop()
