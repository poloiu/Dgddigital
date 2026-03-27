import requests
import time
from bs4 import BeautifulSoup
import random
import sys

# ==========================================
# KONFIGURASI API & DATA
# ==========================================
SERVER_BASE = "https://charms-men-webmaster-mortality.trycloudflare.com"
TOKEN_CLIENT = "CHANGE_ME_CLIENT_123"

MALE_FIRST = ["Budi", "Agus", "Rizky", "Fajar", "Ahmad", "Wahyu", "Hendra"]
FEMALE_FIRST = ["Ayu", "Putri", "Siti", "Nisa", "Sari", "Rini", "Dewi"]
LAST_NAMES = ["Saputra", "Pratama", "Wijaya", "Kusuma", "Santoso", "Hidayat"]
DEFAULT_PW = "SandiKuat123!@"

class FBAutoDaftarReq:
    def __init__(self, target_range, proxy_str, use_proxy):
        self.target_range = target_range
        self.proxy_str = proxy_str
        self.use_proxy = use_proxy
        self.current_number = ""
        self.session = requests.Session()
        
        # User Agent Mobile & Setelan Bahasa Inggris (en-US)
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": "https://limited.facebook.com",
            "Referer": "https://limited.facebook.com/"
        })

    def log(self, text):
        print(f"[BOT] {text}")

    def get_number(self):
        self.log(f"⏳ Mengambil nomor dari API (Range: {self.target_range})...")
        url = f"{SERVER_BASE}/mnit/getnum"
        payload = {"range": self.target_range, "is_national": False, "remove_plus": False}
        headers = {"Content-Type": "application/json", "token": TOKEN_CLIENT}
        try:
            resp = requests.post(url, json=payload, headers=headers).json()
            if resp.get("meta", {}).get("code") == 200:
                self.current_number = resp["data"].get("copy", resp["data"].get("number"))
                self.log(f"✅ Nomor didapat: {self.current_number}")
                return True
            else:
                self.log(f"❌ Gagal Get Number: {resp.get('message')}")
        except Exception as e:
            self.log(f"❌ Error API Get Number: {e}")
        return False

    def wait_for_otp(self):
        self.log(f"🔄 Menunggu OTP masuk untuk {self.current_number} (Maks 3 menit)...")
        url = f"{SERVER_BASE}/mnit/numsuccess?number={self.current_number}"
        headers = {"x-client-secret": TOKEN_CLIENT}
        
        for _ in range(36):
            try:
                resp = requests.get(url, headers=headers).json()
                if resp.get("ok") and resp.get("found"):
                    item = resp.get("otp_item", {})
                    otp_text = str(item.get("otp") or item.get("otp_code") or item.get("code") or "").strip()
                    if otp_text:
                        self.log(f"🎉 OTP DITEMUKAN DI API: {otp_text}")
                        return otp_text
            except: pass
            time.sleep(5)
        self.log("⌛ Waktu habis. OTP tidak masuk.")
        return None

    def run_flow(self):
        # 1. BUKA HALAMAN TANPA PROXY (Untuk ambil token aman)
        self.session.proxies.clear()
        self.log("Membuka limited.facebook.com/reg (Proxy OFF) ...")
        try:
            res = self.session.get("https://limited.facebook.com/reg", timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            self.log(f"❌ Gagal membuka web FB: {e}")
            return

        # Ambil form action URL
        form = soup.find('form')
        if not form:
            self.log("⚠️ Form pendaftaran tidak ditemukan di limited.facebook.com")
            return
            
        action_url = form.get('action')
        if not action_url:
            self.log("⚠️ URL Action form tidak ditemukan!")
            return
            
        if not action_url.startswith("http"):
            action_url = "https://limited.facebook.com" + action_url

        # Ambil semua input hidden (lsd, jazoest, m_ts, dll) wajib dari FB
        payload = {}
        for inp in form.find_all("input"):
            name = inp.get("name")
            value = inp.get("value", "")
            if name: payload[name] = value

        if "lsd" not in payload:
            self.log("⚠️ Token keamanan (lsd) tidak ditemukan!")
            return

        # 2. AMBIL NOMOR API
        if not self.get_number(): return

        # 3. ISI DATA FORMULIR
        is_female = random.choice([True, False]) 
        first_name = random.choice(FEMALE_FIRST) if is_female else random.choice(MALE_FIRST)
        last_name = random.choice(LAST_NAMES)
        
        payload['firstname'] = first_name
        payload['lastname'] = last_name
        payload['reg_email__'] = self.current_number
        payload['sex'] = '1' if is_female else '2' # 1: Female, 2: Male
        payload['reg_passwd__'] = DEFAULT_PW
        payload['birthday_day'] = str(random.randint(1, 28))
        payload['birthday_month'] = str(random.randint(1, 12))
        payload['birthday_year'] = str(random.randint(1990, 2003))
        
        if 'submit' in payload: del payload['submit']
        payload['submit'] = 'Sign Up' # Menggunakan tombol versi bahasa Inggris

        self.log(f"✅ Data disiapkan: {first_name} {last_name} | {self.current_number}")
        time.sleep(2)

        # ===============================================
        # 4. NYALAKAN PROXY HANYA SAAT KLIK DAFTAR
        # ===============================================
        if self.use_proxy and self.proxy_str:
            self.log(f"🌐 MENGAKTIFKAN PROXY untuk pendaftaran...")
            self.session.proxies = {
                "http": f"http://{self.proxy_str}",
                "https": f"http://{self.proxy_str}"
            }

        self.log("🚀 MENGIRIM DATA PENDAFTARAN (Klik Sign Up)...")
        try:
            # Kirim data form (Ini ibarat klik tombol daftar)
            self.session.post(action_url, data=payload, timeout=20)
            
            # Matikan proxy lagi setelah klik daftar berhasil
            self.session.proxies.clear()
            self.log("✅ Data terkirim. (Proxy dimatikan kembali)")
            
        except Exception as e:
            self.log(f"❌ Error saat mengirim data: {e}")
            return

        # 5. TUNGGU OTP DARI API
        otp_api = self.wait_for_otp()
        if not otp_api: return

        print("\n" + "="*40)
        manual_otp = input(f"👉 MASUKKAN KODE OTP SECARA MANUAL: ").strip()
        print("="*40 + "\n")

        # 6. REFRESH & AMBIL COOKIES
        self.log("🔄 Merefresh ke halaman utama (limited.facebook.com)...")
        try:
            self.session.get("https://limited.facebook.com/")
        except: pass
        
        raw_cookies = self.session.cookies.get_dict()
        cookies_str = "; ".join([f"{k}={v}" for k, v in raw_cookies.items()])
        user_id = raw_cookies.get("c_user", "GAGAL / TERKENA CHECKPOINT SEBELUM OTP")

        print("\n" + "★"*40)
        print("🎉 HASIL EKSEKUSI AKUN 🎉")
        print(f"UID      : {user_id}")
        print(f"Password : {DEFAULT_PW}")
        print(f"Cookies  :\n{cookies_str}")
        print("★"*40 + "\n")

def main():
    print("========================================")
    print(" 🤖 BOT FB DAFTAR (LIMITED.FB - REQUESTS) ")
    print("========================================")
    
    target_range = input("[?] Masukkan Range API: ").strip()
    tanya_proxy = input("[?] Pakai Proxy saat klik daftar? (y/n): ").strip().lower()
    use_proxy = (tanya_proxy == 'y')
    
    proxy_str = ""
    if use_proxy:
        proxy_str = input("[?] Masukkan Proxy (user:pass@ip:port): ").strip()

    while True:
        bot = FBAutoDaftarReq(target_range, proxy_str, use_proxy)
        bot.run_flow()
        
        print("\n[INFO] Siklus selesai.")
        lanjut = input("👉 Ketik 'q' lalu Enter untuk memulai loop baru (atau tombol lain untuk berhenti): ").strip().lower()
        if lanjut != 'q':
            print("🛑 Bot dihentikan.")
            break

if __name__ == "__main__":
    main()
