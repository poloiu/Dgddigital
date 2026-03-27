import requests
import time
from bs4 import BeautifulSoup
import random
import os

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
        
        # User-Agent Browser HP Jadul yang paling bandel
        self.session.headers.update({
            "User-Agent": "NokiaX2-01/5.0 (08.71) Profile/MIDP-2.1 Configuration/CLDC-1.1 Mozilla/5.0 AppleWebKit/420+ (KHTML, like Gecko) Safari/420+",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1"
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
        # Gunakan jalur /n/ (jalur alternatif pendaftaran)
        target_url = "https://limited.facebook.com/n/?_rdr"
        self.log(f"Membuka jalur pendaftaran: {target_url}")
        
        try:
            res = self.session.get(target_url, timeout=15)
            soup = BeautifulSoup(res.text, 'html.parser')
            
            # Jika tidak ada form, coba paksa ke /reg/
            if not soup.find("form"):
                self.log("Mencoba alternatif ke /reg/...")
                res = self.session.get("https://limited.facebook.com/reg/", timeout=15)
                soup = BeautifulSoup(res.text, 'html.parser')

            # Debugging: Simpan apa yang dilihat bot
            with open("debug_fb.html", "w", encoding="utf-8") as f:
                f.write(res.text)

            form = soup.find("form")
            if not form:
                self.log("⚠️ Tetap gagal menemukan form. Silakan cek 'debug_fb.html'.")
                return

            action = form.get("action")
            if action and not action.startswith("http"):
                action = "https://limited.facebook.com" + action

            # Scrape semua input yang ada
            payload = {}
            for inp in form.find_all("input"):
                n, v = inp.get("name"), inp.get("value", "")
                if n: payload[n] = v

            if not self.get_number(): return

            # Isi Data
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
                'birthday_year': str(random.randint(1995, 2005)),
            })
            
            # Hapus submit lama dan pasang yang baru jika diperlukan
            if 'submit' in payload: del payload['submit']
            payload['submit'] = 'Sign Up'

            # Kirim Data
            if self.use_proxy and self.proxy_str:
                self.session.proxies = {"http": f"http://{self.proxy_str}", "https": f"http://{self.proxy_str}"}

            self.log(f"🚀 Mendaftar sebagai: {fname} {lname} ({self.current_number})")
            p_res = self.session.post(action, data=payload, timeout=20)
            self.session.proxies.clear()

            self.log(f"Selesai! Cek respon: {p_res.url}")

        except Exception as e:
            self.log(f"❌ Error: {e}")

def main():
    print("=== BOT FB REGISTER (LIMITED BYPASS) ===")
    target_range = input("[?] Range API: ").strip()
    use_p = input("[?] Pakai Proxy? (y/n): ").lower() == 'y'
    p_str = input("[?] Proxy: ").strip() if use_p else ""

    while True:
        bot = FBAutoDaftarReq(target_range, p_str, use_p)
        bot.run_flow()
        if input("\nKetik 'q' untuk keluar: ").lower() == 'q': break

if __name__ == "__main__":
    main()
