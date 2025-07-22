import os
import sys
import requests
import zipfile
import threading
import customtkinter
import queue
import webbrowser
import subprocess
import json
from tkinter import messagebox, filedialog
from PIL import Image

# ==============================================================================
# 1. PUSAT BAHASA (Tidak Berubah)
# ==============================================================================
LANGS = {
    'id': { "app_title": "Downloader oleh Lexiiz3417", "main_title": "Ultimate Video Downloader", "placeholder": "Tempel link videonya di sini, sayang...", "download_button": "🚀 Download Sekarang", "processing_button": "Lagi Proses...", "ready_status": "Tinggal tempel link & gas download!", "format_label": "Format:", "quality_label": "Kualitas:", "format_video": "Video", "format_audio": "Audio (MP3)", "quality_best": "Terbaik", "speed_label": "Kecepatan:", "finished_status": "Yeay! Berhasil diunduh, sayang! 🎉💖", "warn_no_link_title": "Eh, tunggu dulu!", "warn_no_link_msg": "Link videonya belum dimasukin, ayang.", "err_download_title": "Oops, Error!", "err_download_msg": "Aduh, maaf ada error saat download video:\n{}", "ffmpeg_needed_title": "Butuh Komponen Tambahan", "ffmpeg_needed_msg": "Aplikasi ini butuh FFmpeg untuk beberapa fitur.\n\nIzinkan aplikasi mengunduh komponen ini sekarang?", "ffmpeg_warn_msg": "Tanpa FFmpeg, fitur ini mungkin gagal.","audio_quality_best": "Terbaik (VBR)","audio_quality_good": "Bagus (192k)","audio_quality_std": "Standar (128k)", },
    'en': { "app_title": "Downloader by Lexiiz3417", "main_title": "Ultimate Video Downloader", "placeholder": "Paste the video link here, dear...", "download_button": "🚀 Download Now", "processing_button": "Processing...", "ready_status": "Paste a link & let's download!", "format_label": "Format:", "quality_label": "Quality:", "format_video": "Video", "format_audio": "Audio (MP3)", "quality_best": "Best", "speed_label": "Speed:", "finished_status": "Yay! Download finished, dear! 🎉💖", "warn_no_link_title": "Hey, wait!", "warn_no_link_msg": "You haven't entered the link yet, dear.", "err_download_title": "Oops, Error!", "err_download_msg": "Sorry, an error occurred while downloading the video:\n{}", "ffmpeg_needed_title": "Additional Component Required", "ffmpeg_needed_msg": "This application needs FFmpeg for this feature.\n\nAllow the application to download this component now?", "ffmpeg_warn_msg": "Without FFmpeg, this feature might fail.","audio_quality_best": "Best (VBR)","audio_quality_good": "Good (192k)","audio_quality_std": "Standard (128k)", }
}

# ==============================================================================
# 2. KELAS JENDELA LOADING GENERIK (VERSI FINAL TANPA GIF)
# ==============================================================================
class DownloaderWindow(customtkinter.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Memuat Komponen..."); self.geometry("400x200"); self.resizable(False, False); self.protocol("WM_DELETE_WINDOW", self.on_closing); self.grab_set()
        
        self.info_label = customtkinter.CTkLabel(self, text="Mohon tunggu...", wraplength=380); self.info_label.pack(pady=(20, 10))
        self.status_label = customtkinter.CTkLabel(self, text="", wraplength=380, font=("", 10)); self.status_label.pack()
        self.progress_bar = customtkinter.CTkProgressBar(self, width=350); self.progress_bar.set(0); self.progress_bar.pack(pady=10)
        self.percent_label = customtkinter.CTkLabel(self, text="0%"); self.percent_label.pack()
        
        self.update_queue = queue.Queue(); self.download_thread = None

    def on_closing(self): messagebox.showwarning("Tunggu", "Proses sedang berjalan...", parent=self)
    def start_ffmpeg_download(self): self.title("Mengunduh FFmpeg..."); self.download_thread = threading.Thread(target=self.ffmpeg_worker); self.download_thread.start(); self.after(100, self.process_queue)
    def start_ytdlp_update(self): self.title("Memperbarui Mesin..."); self.download_thread = threading.Thread(target=self.ytdlp_worker); self.download_thread.start(); self.after(100, self.process_queue)

    def process_queue(self):
        try:
            while True:
                msg_type, value = self.update_queue.get_nowait()
                if msg_type == 'info_label': self.info_label.configure(text=value)
                elif msg_type == 'status_label': self.status_label.configure(text=value)
                elif msg_type == 'progress': self.progress_bar.set(value)
                elif msg_type == 'percent': self.percent_label.configure(text=value)
                elif msg_type == 'messagebox':
                    msg_kind, title, message = value
                    if msg_kind == 'info': messagebox.showinfo(title, message, parent=self)
                    if msg_kind == 'error': messagebox.showerror(title, message, parent=self)
                elif msg_type == 'destroy': self.destroy(); return
        except queue.Empty: pass
        self.after(100, self.process_queue)

    def ytdlp_worker(self):
        self.update_queue.put(('info_label', "Mencari yt-dlp versi terbaru...")); self.update_queue.put(('status_label', ''))
        try:
            api_url = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"; response = requests.get(api_url, timeout=15); response.raise_for_status(); release_info = response.json(); asset_url = ""
            for asset in release_info.get("assets", []):
                if asset.get("name") == "yt-dlp.exe": asset_url = asset.get("browser_download_url"); break
            if not asset_url: raise Exception("yt-dlp.exe tidak ditemukan di rilis terbaru.")
            bin_folder = os.path.join(get_base_path(), "bin"); ytdlp_path = os.path.join(bin_folder, "yt-dlp.exe")
            with requests.get(asset_url, stream=True, headers={'User-Agent': 'Mozilla/5.0'}, timeout=30) as r:
                r.raise_for_status(); total_size = int(r.headers.get('content-length', 0)); self.update_queue.put(('info_label', f"Mengunduh {os.path.basename(ytdlp_path)}..."))
                with open(ytdlp_path, 'wb') as f:
                    dl_size = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk); dl_size += len(chunk)
                            if total_size > 0:
                                progress = dl_size / total_size; self.update_queue.put(('progress', progress)); self.update_queue.put(('percent', f"{progress*100:.1f}%")); self.update_queue.put(('status_label', f"{dl_size/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB"))
            self.update_queue.put(('messagebox', ('info', 'Sukses!', 'Mesin unduhan (yt-dlp) berhasil diperbarui!'))); self.update_queue.put(('destroy', None))
        except Exception as e: self.update_queue.put(('messagebox', ('error', 'Error', f'Gagal memperbarui yt-dlp:\n{e}'))); self.update_queue.put(('destroy', None))

    def ffmpeg_worker(self):
        application_path = get_base_path(); bin_folder = os.path.join(application_path, "bin"); zip_path = os.path.join(bin_folder, "ffmpeg.zip"); os.makedirs(bin_folder, exist_ok=True)
        try:
            if os.path.exists(zip_path):
                self.update_queue.put(('info_label', "File sementara ditemukan..."));
                try:
                    with zipfile.ZipFile(zip_path, 'r') as zr:
                        if not any(f.filename.endswith("ffmpeg.exe") for f in zr.infolist()): raise zipfile.BadZipFile("ffmpeg.exe tidak ditemukan.")
                        for f in zr.infolist():
                            if f.filename.endswith("ffmpeg.exe"): f.filename=os.path.basename(f.filename); zr.extract(f, bin_folder); break
                    os.remove(zip_path); self.update_queue.put(('messagebox', ('info', "Sukses!", "FFmpeg berhasil disiapkan!"))); self.update_queue.put(('destroy', None)); return
                except zipfile.BadZipFile: self.update_queue.put(('info_label', "File sementara rusak...")); os.remove(zip_path)
            self.update_queue.put(('info_label', "Menghubungi server...")); ffmpeg_zip_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"; headers = {'User-Agent': 'Mozilla/5.0'}
            with requests.get(ffmpeg_zip_url, stream=True, headers=headers, timeout=30) as r:
                r.raise_for_status(); total_size = int(r.headers.get('content-length', 0)); self.update_queue.put(('info_label', "Mengunduh FFmpeg..."))
                with open(zip_path, 'wb') as f:
                    dl_size = 0
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk); dl_size += len(chunk)
                            if total_size > 0:
                                progress = dl_size / total_size; self.update_queue.put(('progress', progress)); self.update_queue.put(('percent', f"{progress*100:.1f}%")); self.update_queue.put(('status_label', f"{dl_size/1024/1024:.2f} MB / {total_size/1024/1024:.2f} MB"))
            self.update_queue.put(('info_label', "Download selesai, ekstrak file...")); self.update_queue.put(('status_label', ''))
            with zipfile.ZipFile(zip_path, 'r') as zr:
                for f in zr.infolist():
                    if f.filename.endswith("ffmpeg.exe"): f.filename=os.path.basename(f.filename); zr.extract(f, bin_folder); break
            os.remove(zip_path); self.update_queue.put(('messagebox', ('info', "Sukses!", "FFmpeg berhasil diinstal!"))); self.update_queue.put(('destroy', None))
        except Exception as e:
            print(f"ERROR FFMPEG: {e}"); self.update_queue.put(('messagebox', ('error', "Error", f"Gagal mengunduh FFmpeg.\nError: {e}")));
            if os.path.exists(zip_path): os.remove(zip_path); self.update_queue.put(('destroy', None))

# ==============================================================================
# 3. FUNGSI BANTUAN
# ==============================================================================
def get_base_path():
    if getattr(sys, 'frozen', False): return os.path.dirname(sys.executable)
    else: return os.path.dirname(os.path.abspath(__file__))
def get_ytdlp_path(): return os.path.join(get_base_path(), "bin", "yt-dlp.exe")
def get_ffmpeg_path(): return os.path.join(get_base_path(), "bin", "ffmpeg.exe")

# ==============================================================================
# 4. KELAS APLIKASI UTAMA 
# ==============================================================================
class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.current_lang = "id"
        self.texts = LANGS[self.current_lang]
        
        self.title(self.texts["app_title"])
        self.geometry("600x520")
        self.resizable(False, False)

        self.update_queue = queue.Queue()

        # --- Main Frame (sebagai 'kotak dalam') ---
        # Sekarang kita buat dia mengisi ruang yang tersedia
        self.main_frame = customtkinter.CTkFrame(self, corner_radius=15)
        self.main_frame.pack(pady=(20, 10), padx=20, fill="both", expand=True)

        self.title_label = customtkinter.CTkLabel(self.main_frame, font=customtkinter.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(10, 10))

        self.url_entry = customtkinter.CTkEntry(self.main_frame, width=400)
        self.url_entry.pack(pady=10, padx=20)
        
        self.options_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.options_frame.pack(pady=10, padx=20, fill="x")
        self.options_frame.columnconfigure((0, 1), weight=1)

        self.format_label = customtkinter.CTkLabel(self.options_frame)
        self.format_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.format_var = customtkinter.StringVar()
        self.format_segmented_button = customtkinter.CTkSegmentedButton(self.options_frame, variable=self.format_var, command=self.on_format_change)
        self.format_segmented_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.quality_label = customtkinter.CTkLabel(self.options_frame)
        self.quality_label.grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.quality_options = ["", "1080p", "720p", "480p"]
        self.quality_menu = customtkinter.CTkOptionMenu(self.options_frame, values=self.quality_options)
        self.quality_menu.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        self.download_button = customtkinter.CTkButton(self.main_frame, command=self.start_download)
        self.download_button.pack(pady=20, padx=20, ipady=5)

        # --- Area Status ---
        self.status_frame = customtkinter.CTkFrame(self.main_frame, fg_color="transparent")
        self.progress_bar = customtkinter.CTkProgressBar(self.status_frame, width=300)
        self.progress_bar.set(0)
        self.status_percent_label = customtkinter.CTkLabel(self.status_frame, text="0%")
        self.status_process_label = customtkinter.CTkLabel(self.status_frame, text="", wraplength=500)
        
        self.main_status_label = customtkinter.CTkLabel(self.main_frame, text="", wraplength=500, justify="center")
        self.main_status_label.pack(pady=(0, 10), fill="x", expand=True)
        
        # --- Footer Frame ---
        self.footer_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=10, pady=(5, 10))
        
        self.about_button = customtkinter.CTkButton(self.footer_frame, text="i", font=customtkinter.CTkFont(size=15, weight="bold"), width=28, height=28, command=self.show_about_window)
        self.about_button.pack(side="left", padx=10)
        
        self.lang_menu = customtkinter.CTkOptionMenu(self.footer_frame, values=["Indonesia", "English"], command=lambda c: self.change_language(c), width=120)
        self.lang_menu.pack(side="right", padx=10)
        
        # Inisialisasi awal
        self.update_ui_texts()
        self.on_format_change(self.format_var.get())
        self.process_queue()

    def process_queue(self):
        try:
            while True:
                msg_type, value = self.update_queue.get_nowait()
                if msg_type == 'progress': self.progress_bar.set(value)
                elif msg_type == 'percent': self.status_percent_label.configure(text=value)
                elif msg_type == 'status': self.status_process_label.configure(text=value)
                elif msg_type == 'finished':
                    self.status_frame.pack_forget() # Sembunyikan frame progress
                    status_text, final_path = value
                    # Tampilkan pesan sukses di label status utama
                    self.main_status_label.configure(text=f"{status_text}\nDisimpan di: {final_path}")
                    self.download_button.configure(state="normal", text=self.texts["download_button"])
                elif msg_type == 'error':
                    self.status_frame.pack_forget()
                    # Tampilkan status siap di label status utama
                    self.main_status_label.configure(text=self.texts["ready_status"])
                    self.download_button.configure(state="normal", text=self.texts["download_button"])
                    messagebox.showerror(self.texts["err_download_title"], self.texts["err_download_msg"].format(value))
                elif msg_type == 'run_updater':
                    self.run_ytdlp_update()
        except queue.Empty: pass
        self.after(100, self.process_queue)
    
    def start_download(self):
        if not self.url_entry.get(): messagebox.showwarning(self.texts["warn_no_link_title"], self.texts["warn_no_link_msg"]); return
        save_path = filedialog.askdirectory()
        if not save_path: return

        self.download_button.configure(state="disabled", text=self.texts["processing_button"])
        
        # Bersihkan status lama, tampilkan frame progress
        self.main_status_label.configure(text="")
        self.status_frame.pack(pady=10)
        self.progress_bar.pack(pady=(5,0))
        self.status_percent_label.pack()
        self.status_process_label.pack()
        
        chosen_format = self.format_var.get(); chosen_quality = self.quality_menu.get()
        threading.Thread(target=self.download_video_thread, args=(self.url_entry.get(), save_path, chosen_format, chosen_quality)).start()

    def download_video_thread(self, video_url, save_path, chosen_format, chosen_quality):
        ytdlp_path = get_ytdlp_path()
        if not os.path.exists(ytdlp_path):
            self.update_queue.put(('run_updater', None))
            # Tunggu sebentar untuk memberi waktu updater berjalan, lalu cek lagi
            threading.Event().wait(1) 
            if not os.path.exists(ytdlp_path):
                self.update_queue.put(('error', "yt-dlp.exe tidak ada. Coba perbarui lagi."))
                return
        
        ffmpeg_path = get_ffmpeg_path()

        # 1. Tentukan subfolder berdasarkan format
        subfolder = "videos" if chosen_format == self.texts["format_video"] else "audios"
        
        # 2. Buat template path output yang baru dan dinamis
        # %(extractor)s akan otomatis diisi dengan nama situs (misal: facebook, youtube)
        # %(id)s akan diisi ID video
        output_template = os.path.join(save_path, '%(extractor)s', subfolder, '%(id)s.%(ext)s')

        # 3. Buat perintah untuk subprocess
        command = [ytdlp_path]
        
        # Menambahkan argumen format
        if chosen_format == self.texts["format_audio"]:
            if not os.path.exists(ffmpeg_path):
                self.update_queue.put(('error', self.texts["ffmpeg_warn_msg"]))
                return
            command.extend(['-x', '--audio-format', 'mp3', '--audio-quality', '192K'])
        else:
            quality_map = { 
                self.texts["quality_best"]: 'bestvideo*+bestaudio/best', 
                "1080p": 'bestvideo[height<=1080]+bestaudio', 
                "720p": 'bestvideo[height<=720]+bestaudio', 
                "480p": 'bestvideo[height<=480]+bestaudio' 
            }
            command.extend(['-f', quality_map.get(chosen_quality, quality_map[self.texts["quality_best"]])])
        
        # 4. Gunakan template output yang baru di dalam perintah
        command.extend([
            '--ffmpeg-location', os.path.dirname(ffmpeg_path),
            '-o', output_template, # <-- Menggunakan template baru
            '--no-playlist',
            '--progress',
            '--progress-template', '{"status":"%(progress.status)s", "downloaded_bytes":%(progress.downloaded_bytes)d, "total_bytes":%(progress.total_bytes)d, "speed":"%(progress.speed)s"}',
            video_url
        ])

        try:
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)
            for line in iter(process.stdout.readline, ''):
                try:
                    data = json.loads(line)
                    if data['status'] == 'downloading':
                        total = data.get('total_bytes'); downloaded = data.get('downloaded_bytes'); speed = data.get('speed', 'N/A')
                        if total and downloaded: progress = downloaded / total; self.update_queue.put(('progress', progress)); self.update_queue.put(('percent', f"{progress*100:.1f}%"))
                        self.update_queue.put(('status', f"{self.texts['speed_label']} {speed}"))
                except (json.JSONDecodeError, KeyError): continue
            process.wait()
            if process.returncode == 0:
                self.update_queue.put(('finished', (self.texts["finished_status"], save_path)))
            else: self.update_queue.put(('error', process.stderr.read()))
        except Exception as e: self.update_queue.put(('error', e))

    def run_ytdlp_update(self):
        root = customtkinter.CTk(); root.withdraw()
        updater_window = DownloaderWindow(root); updater_window.start_ytdlp_update(); root.wait_window(updater_window)
    def show_about_window(self):
        if hasattr(self,'about_win') and self.about_win.winfo_exists(): self.about_win.focus(); return
        self.about_win = customtkinter.CTkToplevel(self); self.about_win.title("Tentang Aplikasi"); self.about_win.geometry("350x300"); self.about_win.resizable(False, False); self.about_win.transient(self); self.about_win.grab_set()
        customtkinter.CTkLabel(self.about_win, text="Downloader", font=customtkinter.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))
        customtkinter.CTkLabel(self.about_win, text="Versi 1.4.0", font=customtkinter.CTkFont(size=12)).pack(pady=0)
        customtkinter.CTkLabel(self.about_win, text="Dibuat oleh: Lexiiz3417", font=customtkinter.CTkFont(size=12)).pack(pady=(15, 5))
        customtkinter.CTkLabel(self.about_win, text="Tools tempur: yt-dlp, CustomTkinter, Python", font=customtkinter.CTkFont(size=10)).pack(pady=0)
        customtkinter.CTkButton(self.about_win, text="Perbarui Mesin Unduhan", command=self.run_ytdlp_update).pack(pady=(20,5))
        github_link_label=customtkinter.CTkLabel(self.about_win,text="Lihat di GitHub",text_color="#6495ED",font=customtkinter.CTkFont(size=12,underline=True),cursor="hand2"); github_link_label.pack(pady=(10, 5)); github_link_label.bind("<Button-1>", lambda e: webbrowser.open_new_tab("https://github.com/Lexiiz3417/"))
    def update_ui_texts(self):
        self.texts = LANGS[self.current_lang]; self.title(self.texts["app_title"]); self.title_label.configure(text=self.texts["main_title"]); self.url_entry.configure(placeholder_text=self.texts["placeholder"]); self.download_button.configure(text=self.texts["download_button"]); self.main_status_label.configure(text=self.texts["ready_status"]); self.format_label.configure(text=self.texts["format_label"]); self.quality_label.configure(text=self.texts["quality_label"]);
        video_text=self.texts["format_video"]; audio_text=self.texts["format_audio"]; self.format_segmented_button.configure(values=[video_text, audio_text]);
        if self.format_var.get() in [LANGS['id']['format_video'], LANGS['en']['format_video'], ""]: self.format_var.set(video_text)
        else: self.format_var.set(audio_text)
        self.quality_options[0]=self.texts["quality_best"]; self.quality_menu.configure(values=self.quality_options)
    def on_format_change(self, value):
        """Menampilkan/menyembunyikan dan mengubah isi menu kualitas."""
        if value == self.texts["format_video"]:
            self.quality_label.grid()
            self.quality_menu.grid()
            # Atur pilihan untuk video
            self.quality_menu.configure(values=self.quality_options)
            self.quality_menu.set(self.texts["quality_best"])
        else:
            self.quality_label.grid()
            self.quality_menu.grid()
            # Atur pilihan untuk audio
            audio_options = [
                self.texts["audio_quality_best"],
                self.texts["audio_quality_good"],
                self.texts["audio_quality_std"]
            ]
            self.quality_menu.configure(values=audio_options)
            self.quality_menu.set(self.texts["audio_quality_best"])

# ==============================================================================
# 5. ALUR UTAMA APLIKASI
# ==============================================================================
if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")
    customtkinter.set_default_color_theme("blue")
    
    if not os.path.exists(get_ffmpeg_path()):
        root = customtkinter.CTk(); root.withdraw()
        user_choice = messagebox.askyesno(LANGS['id']['ffmpeg_needed_title'], LANGS['id']['ffmpeg_needed_msg'])
        if user_choice:
            downloader_window = DownloaderWindow(root); downloader_window.start_ffmpeg_download(); root.wait_window(downloader_window)
        else: messagebox.showwarning(LANGS['id']['ffmpeg_warn_title'], LANGS['id']['ffmpeg_warn_msg'])
        try:
            if root.winfo_exists(): root.destroy()
        except Exception: pass

    app = App()
    app.mainloop()