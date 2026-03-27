import requests
import time
from bs4 import BeautifulSoup
import random

# ==========================================
# KONFIGURASI API & DATA
# ==========================================
SERVER_BASE = "http://64.176.82.110:3000"
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
        
        # User-Agent Chrome Android Ringan (Paling Standar)
        self.ua = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        
        self.session.headers.update({
            "User-Agent": self.ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        })

    def log(self, text):
        print(f"[BOT] {text}")

    def get_number(self):
        self.log(f"⏳ Mengambil nomor API...")
        url = f"{SERVER_BASE}/mnit/getnum"
        payload = {"range": self.target_range, "is_national": False, "remove_plus": False}
        headers = {"Content-Type": "application/json", "token": TOKEN_CLIENT}
        try:
            resp = requests.post(url, json=payload, headers=headers).json()
            if resp.get("meta", {}).get("code") == 200:
                self.current_number = resp["data"].get("copy", resp["data"].get("number"))
                self.log(f"✅ Nomor: {self.current_number}")
                return True
        except: pass
        return False

    def run_flow(self):
        # STEP 1: Kunjungi Home dulu untuk dapat Cookies Dasar
        self.log("Membuka halaman utama limited.facebook.com...")
        try:
            r1 = self.session.get("https://limited.facebook.com/", timeout=15)
            # Kadang FB minta klik 'Create New Account' dulu
            if "/reg/" in r1.text:
                url_reg = "https://limited.facebook.com/reg/"
            else:
                url_reg = "https://limited.facebook.com/reg/"
            
            time.sleep(2)
            res = self.session.get(url_reg, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
        except Exception as e:
            self.log(f"❌ Koneksi Error: {e}")
            return

        # STEP 2: Cari Form & Payload
        form = soup.find("form")
        if not form:
            self.log("⚠️ Form masih tidak ketemu!")
            # DEBUG: Simpan halaman ke file untuk dicek manual
            with open("debug_fb.html", "w", encoding="utf-8") as f:
                f.write(res.text)
            self.log("💡 Cek file 'debug_fb.html' di folder kamu untuk lihat apa yang muncul.")
            return

        action = form.get("action")
        if not action.startswith("http"):
            action = "https://limited.facebook.com" + action

        payload = {}
        for inp in form.find_all("input"):
            n, v = inp.get("name"), inp.get("value", "")
            if n: payload[n] = v

        if not self.get_number(): return

        # STEP 3: Isi Data
        is_female = random.choice([True, False])
        fname = random.choice(FEMALE_FIRST if is_female else MALE_FIRST)
        lname = random.choice(LAST_NAMES)
        
        payload.update({
            'firstname': fname,
            'lastname': lname,
            'reg_email__': self.current_number,
            'sex': '1' if is_female else '2',
            'reg_passwd__': DEFAULT_PW,
            'birthday_day': str(random.randint(1, 28)),
            'birthday_month': str(random.randint(1, 12)),
            'birthday_year': str(random.randint(1992, 2004)),
            'submit': 'Sign Up'
        })

        # STEP 4: Submit dengan Proxy (jika ada)
        if self.use_proxy and self.proxy_str:
            self.session.proxies = {"http": f"http://{self.proxy_str}", "https": f"http://{self.proxy_str}"}
            self.log("🌐 Proxy Aktif...")

        self.log(f"🚀 Mendaftar sebagai {fname} {lname}...")
        try:
            p_res = self.session.post(action, data=payload, timeout=20)
            self.session.proxies.clear()
            
            # Cek hasil
            if "checkpoint" in p_res.url or "confirm" in p_res.url:
                self.log("✅ Berhasil masuk ke halaman Konfirmasi/OTP!")
            else:
                self.log(f"❓ Status Terakhir: {p_res.url}")
        except Exception as e:
            self.log(f"❌ Post Error: {e}")

def main():
    target_range = input("[?] Range API: ").strip()
    use_p = input("[?] Pakai Proxy? (y/n): ").lower() == 'y'
    p_str = input("[?] Proxy: ").strip() if use_p else ""

    while True:
        bot = FBAutoDaftarReq(target_range, p_str, use_p)
        bot.run_flow()
        if input("\nLanjut? (q=exit): ").lower() == 'q': break

if __name__ == "__main__":
    main()
