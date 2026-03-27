import time
import requests
import random
import re
import sys

try:
    from seleniumwire import webdriver 
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
except ImportError:
    print("❌ Library belum lengkap! Jalankan: pip3 install selenium selenium-wire requests --break-system-packages")
    sys.exit(1)

# ==========================================
# KONFIGURASI API & DATA
# ==========================================
SERVER_BASE = "https://charms-men-webmaster-mortality.trycloudflare.com"
TOKEN_CLIENT = "CHANGE_ME_CLIENT_123"

MALE_FIRST = ["Budi", "Agus", "Rizky", "Fajar", "Ahmad", "Wahyu", "Hendra"]
FEMALE_FIRST = ["Ayu", "Putri", "Siti", "Nisa", "Sari", "Rini", "Dewi"]
LAST_NAMES = ["Saputra", "Pratama", "Wijaya", "Kusuma", "Santoso", "Hidayat"]
DEFAULT_PW = "SandiKuat123!@"

class FBBotSeleniumCLI:
    def __init__(self, target_range, proxy_str, use_proxy):
        self.target_range = target_range
        self.proxy_str = proxy_str
        self.use_proxy = use_proxy
        self.driver = None
        self.current_number = ""
        self.is_running = True

    def log(self, text):
        print(f"[BOT] {text}")

    def request_interceptor(self, request):
        blocked = ['.woff', '.ttf', '.svg', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4']
        if any(b in request.url for b in blocked):
            request.abort()

    def init_browser(self):
        if self.driver:
            try: self.driver.quit()
            except: pass
        
        options = Options()
        options.add_argument("--window-size=400,600")
        options.add_argument("--headless=new") # Wajib Headless untuk Termux CLI
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--lang=en-US")
        
        mobile_emulation = {
            "deviceMetrics": { "width": 360, "height": 640, "pixelRatio": 3.0 },
            "userAgent": "Mozilla/5.0 (Linux; Android 13; SM-A525F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Mobile Safari/537.36"
        }
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        prefs = {"intl.accept_languages": "en-US,en"}
        options.add_experimental_option("prefs", prefs)

        try:
            self.driver = webdriver.Chrome(options=options)
            self.driver.proxy = {} 
            
            # Anti-Detect Spoofing (Bypass WAF)
            spoof_js = """
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """
            self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": spoof_js})
            self.driver.request_interceptor = self.request_interceptor
            self.log("✅ Browser berjalan (Proxy OFF).")
        except Exception as e:
            self.log(f"❌ Error buka browser: {e}")
            sys.exit(1)

    def execute_js_with_wait(self, js_script, *args, timeout=20, step_name="Step"):
        for _ in range(timeout):
            if not self.is_running: return None
            try:
                res = self.driver.execute_script(js_script, *args)
                if res and "ERR:" not in str(res) and not str(res).startswith("NO_"):
                    return str(res)
            except Exception: pass
            time.sleep(1)
        self.log(f"❌ Timeout berhenti di {step_name}.")
        return None

    def click_next_general(self, extra_words=None):
        words = ['selanjutnya', 'next', 'lanjut', 'continue', 'lanjutkan', 'submit', 'kirim']
        if extra_words: words.extend(extra_words)
        js = """
        var words = arguments[0];
        var els=document.querySelectorAll('button, a, div[role=button], span, input[type="submit"], input[type="button"]');
        for(var i=0;i<els.length;i++){
            var r = els[i].getBoundingClientRect();
            if(r.width>0 && r.height>0){
                var t=(els[i].innerText || els[i].value || '').trim().toLowerCase();
                for(var w=0; w<words.length; w++){
                    if(t === words[w]){ els[i].click(); return 'NEXT_CLICKED'; }
                }
            }
        }
        return 'NO_NEXT';
        """
        return self.execute_js_with_wait(js, words, timeout=5, step_name="Tombol Next")

    def get_number(self):
        url = f"{SERVER_BASE}/mnit/getnum"
        payload = {"range": self.target_range, "is_national": False, "remove_plus": False}
        headers = {"Content-Type": "application/json", "token": TOKEN_CLIENT}
        try:
            resp = requests.post(url, json=payload, headers=headers).json()
            if resp.get("meta", {}).get("code") == 200:
                self.current_number = resp["data"].get("copy", resp["data"].get("number"))
                self.log(f"✅ Nomor API didapat: {self.current_number}")
                return True
        except: pass
        return False

    def auto_register_flow(self):
        self.init_browser()
        self.log("Membuka https://limited.facebook.com/reg ...")
        self.driver.get("https://limited.facebook.com/reg")

        is_female = random.choice([True, False]) 
        first_name = random.choice(FEMALE_FIRST) if is_female else random.choice(MALE_FIRST)
        last_name = random.choice(LAST_NAMES)

        # 1. FORM NAMA 
        js_name = """
            var first = arguments[0]; var last = arguments[1];
            function vis(el){if(!el) return false; var r=el.getBoundingClientRect(); return r.width>0&&r.height>0;}
            var inputs = document.querySelectorAll('input[type=text], input:not([type=hidden])');
            var visInputs = [];
            for(var i=0; i<inputs.length; i++) { if(vis(inputs[i])) visInputs.push(inputs[i]); }
            if (visInputs.length === 0) return 'NO_INPUT';
            if(visInputs.length >= 2){
                visInputs[0].value = first; visInputs[0].dispatchEvent(new Event('input', {bubbles:true})); 
                visInputs[1].value = last; visInputs[1].dispatchEvent(new Event('input', {bubbles:true})); 
                return 'FILLED_SPLIT';
            } else {
                visInputs[0].value = first + ' ' + last; visInputs[0].dispatchEvent(new Event('input', {bubbles:true})); 
                return 'FILLED_FULL';
            }
        """
        if not self.execute_js_with_wait(js_name, first_name, last_name, timeout=20, step_name="Form Nama"): return
        self.log(f"✅ Nama diisi: {first_name} {last_name}")
        time.sleep(1); self.click_next_general()

        # 2. HALAMAN DOB & USIA
        self.execute_js_with_wait("return 'FOUND_DOB';", timeout=10, step_name="Halaman DOB")
        self.click_next_general(); time.sleep(1); self.click_next_general()

        age_val = str(random.randint(20, 40))
        js_age = """
            var ageStr = arguments[0];
            var inp = document.querySelector('input[type=number]');
            if(!inp) return 'NO_AGE_INPUT';
            inp.value = ageStr;
            inp.dispatchEvent(new Event('input',{bubbles:true})); 
            return 'INJECTED';
        """
        self.execute_js_with_wait(js_age, age_val, timeout=10, step_name="Form Usia")
        time.sleep(1); self.click_next_general()

        # 3. OVERLAY OK
        self.click_next_general(['oke', 'ok'])

        # 4. SUNTIK NOMOR
        if not self.get_number(): 
            self.log("⚠️ Gagal ambil nomor."); return
            
        js_inject_phone = """
            var phoneStr = arguments[0];
            var inp = document.querySelector('input[type=tel]');
            if(!inp) return 'NO_PHONE_INPUT';
            inp.value = phoneStr;
            inp.dispatchEvent(new Event('input',{bubbles:true})); 
            return 'INJECTED';
        """
        if not self.execute_js_with_wait(js_inject_phone, self.current_number, timeout=15, step_name="Suntik Nomor"): return
        self.log(f"✅ Nomor disuntik: {self.current_number}")
        time.sleep(1); self.click_next_general()

        # 5. PILIH GENDER
        gender_id = "Perempuan" if is_female else "Laki-laki"
        gender_en = "Female" if is_female else "Male"
        js_gender = """
            var wantId = arguments[0].toLowerCase(); var wantEn = arguments[1].toLowerCase();
            var radios=document.querySelectorAll('input[type=radio]');
            for(var i=0;i<radios.length;i++){
                var r=radios[i];
                var wrap=r.closest('div, label'); if(!wrap) continue;
                var txt=(wrap.innerText||'').trim().toLowerCase();
                if(txt===wantId || txt===wantEn){
                    r.checked=true; r.dispatchEvent(new Event('change',{bubbles:true}));
                    wrap.click(); return 'GENDER_CLICKED';
                }
            }
            return 'NO_GENDER_OPTION';
        """
        if not self.execute_js_with_wait(js_gender, gender_id, gender_en, timeout=20, step_name="Pilih Gender"): return
        time.sleep(1); self.click_next_general()

        # 6. PASSWORD
        js_inject_pw = """
            var pwStr = arguments[0];
            var inp=document.querySelector('input[type=password]');
            if(!inp) return 'NO_PW_INPUT';
            inp.value = pwStr;
            inp.dispatchEvent(new Event('input',{bubbles:true}));
            return 'INJECTED';
        """
        if not self.execute_js_with_wait(js_inject_pw, DEFAULT_PW, timeout=20, step_name="Form Password"): return
        self.log("✅ Password disuntik!")
        time.sleep(1) 

        # ===============================================
        # AKTIFKAN PROXY SAAT KLIK DAFTAR
        # ===============================================
        if self.use_proxy and self.proxy_str:
            self.log(f"🌐 MENGAKTIFKAN PROXY untuk klik Daftar...")
            self.driver.proxy = {
                'http': f'http://{self.proxy_str}',
                'https': f'http://{self.proxy_str}',
                'no_proxy': 'localhost,127.0.0.1'
            }
            time.sleep(2) 

        # 7. KLIK DAFTAR
        js_click_daftar = """
            var cand=[];
            var els=document.querySelectorAll('button,input[type=submit],input[type=button],a,div[role=button]');
            for(var i=0;i<els.length;i++){
                var t=(els[i].innerText||els[i].value||'').trim().toLowerCase();
                if(t==='daftar' || t==='sign up' || t==='register' || t==='selanjutnya' || t==='next'){ cand.push(els[i]); }
            }
            if(cand.length>0) { cand[0].click(); return 'CLICKED_REGISTER'; }
            return 'NO_REGISTER_BTN';
        """
        if not self.execute_js_with_wait(js_click_daftar, timeout=10, step_name="Tombol Daftar"): return
        self.log("✅ Tombol DAFTAR diklik!")

        self.driver.proxy = {} 

        # 8. POST-REGISTRATION (NOT NOW -> SMS -> CONTINUE)
        self.log("⏳ Menunggu Not Now / SMS...")
        for _ in range(60):
            try:
                js_not_now = """
                    var els = document.querySelectorAll('button, a, div[role="button"], span');
                    for(var i=0; i<els.length; i++){
                        var t = (els[i].innerText||'').trim().toLowerCase();
                        if(t === 'not now' || t === 'lain kali'){ els[i].click(); return 'CLICKED_NOT_NOW'; }
                    } return 'WAIT';
                """
                if self.driver.execute_script(js_not_now) == 'CLICKED_NOT_NOW':
                    time.sleep(2); continue 
                
                js_sms = """
                    var labels = document.querySelectorAll('label, div, span');
                    for(var i=0; i<labels.length; i++){
                        var t = (labels[i].innerText||'').toLowerCase();
                        if((t.includes('via sms') || t.includes('melalui sms') || t.includes('sms')) && t.length < 40){
                            var radio = labels[i].querySelector('input[type="radio"]');
                            if(radio) { radio.checked = true; radio.dispatchEvent(new Event('change', {bubbles:true})); }
                            labels[i].click(); return 'CLICKED_SMS';
                        }
                    } return 'WAIT';
                """
                if self.driver.execute_script(js_sms) == 'CLICKED_SMS':
                    time.sleep(2)
                    self.click_next_general(['continue', 'lanjutkan', 'selanjutnya', 'kirim'])
                    break 
            except: pass
            time.sleep(1)

        # 9. TUNGGU OTP
        self.log(f"🔄 Menunggu OTP masuk untuk {self.current_number} di API...")
        otp_text = None
        for _ in range(36):
            try:
                resp = requests.get(f"{SERVER_BASE}/mnit/numsuccess?number={self.current_number}", headers={"x-client-secret": TOKEN_CLIENT}).json()
                if resp.get("ok") and resp.get("found"):
                    item = resp.get("otp_item", {})
                    otp_text = str(item.get("otp") or item.get("code") or "").strip()
                    if otp_text: break
            except: pass
            time.sleep(5)

        if otp_text:
            self.log(f"🎉 OTP DITEMUKAN DI API: {otp_text}")
        else:
            print("\n" + "="*40)
            otp_text = input(f"👉 MASUKKAN KODE OTP MANUAL (Atau Enter jika gagal): ").strip()
            print("="*40 + "\n")

        if not otp_text: return

        # 10. INPUT OTP (Sesuai kodemu)
        try:
            js_find_inp = "var inp = document.querySelector('input[name=\"c\"], input[name=\"code\"], input[id*=\"code\"], input[type=\"number\"]'); return inp;"
            otp_input = self.driver.execute_script(js_find_inp)
            if otp_input:
                otp_input.clear(); otp_input.send_keys(str(otp_text)); time.sleep(1)
                otp_input.send_keys(Keys.ENTER)
                time.sleep(2)
                self.click_next_general(['continue', 'lanjutkan', 'selanjutnya', 'submit', 'kirim'])
            else:
                self.log("⚠️ Kotak input OTP tidak ditemukan.")
        except Exception as e:
            self.log(f"⚠️ Gagal injeksi OTP: {e}")

        # 11. REFRESH & AMBIL COOKIES
        self.log("⏳ Menunggu 10 detik lalu refresh ke m.facebook.com ...")
        time.sleep(10)
        self.driver.get("https://m.facebook.com/")
        time.sleep(5)
        
        raw_cookies = self.driver.get_cookies()
        cookies_str = "; ".join([f"{c['name']}={c['value']}" for c in raw_cookies])
        user_id = next((c['value'] for c in raw_cookies if c['name'] == 'c_user'), "CHECKPOINT")
        
        print("\n" + "★"*40)
        print("🎉 HASIL EKSEKUSI AKUN 🎉")
        print(f"UID      : {user_id}")
        print(f"Password : {DEFAULT_PW}")
        print(f"Cookies  :\n{cookies_str}")
        print("★"*40 + "\n")

        self.driver.quit()
        self.driver = None

def main():
    print("====================================================")
    print(" 🤖 BOT FB DAFTAR (UBUNTU SELENIUM CLI - BYPASS WAF) ")
    print("====================================================")
    
    target_range = input("[?] Masukkan Range API: ").strip()
    tanya_proxy = input("[?] Pakai Proxy saat klik daftar? (y/n): ").strip().lower()
    use_proxy = (tanya_proxy == 'y')
    
    proxy_str = ""
    if use_proxy:
        proxy_str = input("[?] Masukkan Proxy (user:pass@ip:port): ").strip()

    while True:
        bot = FBBotSeleniumCLI(target_range, proxy_str, use_proxy)
        bot.auto_register_flow()
        
        print("\n[INFO] Siklus selesai.")
        lanjut = input("👉 Ketik 'q' lalu Enter untuk memulai loop baru (atau tombol lain untuk berhenti): ").strip().lower()
        if lanjut != 'q':
            print("🛑 Bot dihentikan.")
            break

if __name__ == "__main__":
    main()

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
