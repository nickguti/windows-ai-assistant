from gtts import gTTS
from pydub import AudioSegment
import io
import os
import speech_recognition as sr
import datetime
import webbrowser
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import simpleaudio as sa
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext, ttk, simpledialog
import threading
import pyautogui
import time
import json
import wikipedia
import pywhatkit
import random
import psutil
import speedtest
import openai
import pystray
from PIL import Image

# ---------------------- IMPOSTAZIONI DI DEFAULT --------------------------
DEFAULT_SETTINGS = {
    DEFAULT_SETTINGS = {
    "WAKE_WORD": "francesco",
    "CITY": "Bologna",
    "VOICE_SPEED": "1.0",
    "VOICE_PITCH": "0",
    "SPOTIFY_CLIENT_ID": "",
    "SPOTIFY_CLIENT_SECRET": "",
    "SPOTIFY_REDIRECT_URI": "http://127.0.0.1:8888/callback",
    "SPOTIFY_SCOPE": "user-modify-playback-state,user-read-playback-state",
    "OPENAI_API_KEY": "",
    "OPENAI_MODEL": "gpt-3.5-turbo"
}

SETTINGS_FILE = "assistant_settings.json"
CONTACTS_FILE = "assistant_contacts.json"

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=4)

def load_contacts():
    if os.path.exists(CONTACTS_FILE):
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_contacts(contacts):
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=2)

settings = load_settings()
contacts = load_contacts()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AudioSegment.converter = os.path.join(BASE_DIR, "ffmpeg.exe")
AudioSegment.ffprobe = os.path.join(BASE_DIR, "ffprobe.exe")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=settings["SPOTIFY_CLIENT_ID"],
    client_secret=settings["SPOTIFY_CLIENT_SECRET"],
    redirect_uri=settings["SPOTIFY_REDIRECT_URI"],
    scope=settings["SPOTIFY_SCOPE"]))

MEMORY_FILE = "assistant_memory.json"
def save_memory(note):
    mem = []
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            mem = json.load(f)
    mem.append(note)
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(mem, f, indent=2)

def get_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            mem = json.load(f)
        return mem
    else:
        return []

# ---------------------- FUNZIONI BASE --------------------------
def speak(text):
    print("Assistente:", text)
    app.log(text)
    tts = gTTS(text=text, lang='it', slow=float(settings.get("VOICE_SPEED", "1.0"))<1)
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    audio = AudioSegment.from_file(mp3_fp, format="mp3")
    try:
        speed = float(settings.get("VOICE_SPEED", "1.0"))
        if speed != 1.0:
            audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * speed)}).set_frame_rate(audio.frame_rate)
    except:
        pass
    temp_wav_path = "temp.wav"
    try:
        audio.export(temp_wav_path, format="wav")
        wave_obj = sa.WaveObject.from_wave_file(temp_wav_path)
        play_obj = wave_obj.play()
        play_obj.wait_done()
        time.sleep(0.1)
    finally:
        if os.path.exists(temp_wav_path):
            os.remove(temp_wav_path)

def listen(timeout=5, phrase_time_limit=5):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        app.log("In ascolto...")
        try:
            audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            query = r.recognize_google(audio, language='it-IT')
            app.log("Tu: " + query)
            return query.lower()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except sr.RequestError:
            speak("Errore di connessione.")
            return ""

def log_command(cmd):
    with open(os.path.join(BASE_DIR, "log_comandi.txt"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now()}: {cmd}\n")

def get_weather(city=None):
    if not city:
        city = settings["CITY"]
    url = f"https://wttr.in/{city}?format=3"
    try:
        response = requests.get(url)
        speak(f"Il tempo a {city} è:")
        speak(response.text)
    except:
        speak("Non riesco a ottenere il meteo.")

def play_spotify():
    try:
        devices = sp.devices()
        if devices['devices']:
            device_id = devices['devices'][0]['id']
            sp.start_playback(device_id=device_id)
            speak("Sto riproducendo Spotify.")
        else:
            speak("Nessun dispositivo Spotify attivo trovato.")
    except Exception as e:
        app.log("Errore Spotify: " + str(e))
        speak("Non sono riuscito a connettermi a Spotify.")

def spotify_control(action):
    try:
        devices = sp.devices()
        if not devices['devices']:
            speak("Nessun dispositivo Spotify attivo trovato.")
            return
        device_id = devices['devices'][0]['id']
        if action == "next":
            sp.next_track(device_id=device_id)
            speak("Traccia successiva.")
        elif action == "previous":
            sp.previous_track(device_id=device_id)
            speak("Traccia precedente.")
        elif action == "pause":
            sp.pause_playback(device_id=device_id)
            speak("Musica in pausa.")
        elif action == "play":
            sp.start_playback(device_id=device_id)
            speak("Riprendo la musica.")
    except Exception as e:
        speak("Comando Spotify non riuscito.")

def spotify_search_and_play(query):
    try:
        results = sp.search(q=query, limit=1, type='track')
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            track = tracks[0]
            uri = track['uri']
            sp.start_playback(uris=[uri])
            speak(f"Riproduco: {track['name']} di {track['artists'][0]['name']}")
        else:
            speak("Nessun brano trovato.")
    except Exception as e:
        speak("Errore nella ricerca su Spotify.")

def spotify_play_playlist(playlist_name):
    try:
        playlists = sp.current_user_playlists()['items']
        for pl in playlists:
            if playlist_name.lower() in pl['name'].lower():
                sp.start_playback(context_uri=pl['uri'])
                speak(f"Riproduco la playlist {pl['name']}.")
                return
        speak("Playlist non trovata.")
    except Exception as e:
        speak("Errore nel cercare la playlist.")

def open_discord():
    discord_path = os.path.join(BASE_DIR, "Update.exe")
    if os.path.exists(discord_path):
        os.startfile(discord_path)
        speak("Apro Discord")
    else:
        speak("Non trovo Discord sul percorso specificato.")

def open_streaming(service):
    urls = {
        "netflix": "https://www.netflix.com/",
        "prime video": "https://www.primevideo.com/",
        "disney plus": "https://www.disneyplus.com/"
    }
    found = None
    for key in urls:
        if key in service:
            found = urls[key]
            break
    if found:
        webbrowser.open(found)
        speak(f"Apro {service.capitalize()}")
    else:
        speak("Servizio di streaming non riconosciuto.")

def take_screenshot():
    img = pyautogui.screenshot()
    filename = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
    if filename:
        img.save(filename)
        speak("Screenshot salvato.")

def set_timer(minutes):
    speak(f"Timer impostato per {minutes} minuti.")
    threading.Thread(target=lambda: (time.sleep(minutes*60), speak("Tempo scaduto!"))).start()

def set_reminder(text, seconds):
    speak(f"Promemoria impostato.")
    threading.Thread(target=lambda: (time.sleep(seconds), speak(f"Promemoria: {text}"))).start()

def simple_calc(expression):
    try:
        result = eval(expression, {"__builtins__": {}})
        speak(f"Il risultato è {result}")
    except Exception:
        speak("Espressione non valida.")

def search_google(query):
    url = f"https://www.google.com/search?q={query}"
    webbrowser.open(url)
    speak(f"Cerco {query} su Google")

def search_youtube(query):
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)
    speak(f"Cerco {query} su YouTube")

def adjust_volume(level):
    try:
        import ctypes
        for _ in range(5):
            ctypes.windll.user32.keybd_event(0xAF if level > 0 else 0xAE, 0, 0, 0)
            time.sleep(0.05)
        speak(f"Volume {'su' if level > 0 else 'giù'}")
    except:
        speak("Funzione non disponibile su questo sistema.")

def save_note(note):
    with open("appunti.txt", "a", encoding="utf-8") as f:
        f.write(note + "\n")
    speak("Ho preso nota.")

def send_whatsapp(contact, message):
    number = contact
    if not number.startswith("+"):
        if contact in contacts:
            number = contacts[contact]
        else:
            speak("Contatto non trovato nella rubrica.")
            return
    try:
        pywhatkit.sendwhatmsg_instantly(number, message, wait_time=10, tab_close=True)
        speak("Messaggio WhatsApp pronto per l'invio. Conferma nel browser.")
    except Exception as e:
        speak("Errore nell'invio del messaggio WhatsApp.")

def wiki_search(query):
    try:
        wikipedia.set_lang("it")
        summary = wikipedia.summary(query, sentences=2)
        speak(summary)
    except Exception:
        speak("Non ho trovato risultati su Wikipedia.")

def random_joke():
    jokes = [
        "Perché il computer è andato dal dottore? Perché aveva un virus!",
        "Sai qual è il colmo per un elettricista? Non trovare la corrente!",
        "Che fa un matematico al mare? Integra.",
        "Perché il pomodoro non riesce a dormire? Perché l'insalata russa.",
        "Perché la maestra va a scuola con il costume? Perché insegna le immersioni!"
    ]
    joke = random.choice(jokes)
    speak(joke)

def random_number(min_val, max_val):
    num = random.randint(min_val, max_val)
    speak(f"Numero casuale tra {min_val} e {max_val}: {num}")

def guess_the_number():
    numero = random.randint(1, 100)
    speak("Ho pensato a un numero tra 1 e 100. Prova a indovinare!")
    tentativi = 0
    while True:
        risposta = listen(5, 5)
        tentativi += 1
        try:
            guess = int(''.join(filter(str.isdigit, risposta)))
        except:
            speak("Per favore, dimmi solo il numero.")
            continue
        if guess < numero:
            speak("Troppo basso!")
        elif guess > numero:
            speak("Troppo alto!")
        else:
            speak(f"Bravo! Hai indovinato in {tentativi} tentativi.")
            break

def play_sound(effect):
    sounds = {
        "buzzer": "buzzer.wav",
        "applausi": "applause.wav"
    }
    if effect in sounds and os.path.exists(sounds[effect]):
        wave_obj = sa.WaveObject.from_wave_file(sounds[effect])
        play_obj = wave_obj.play()
        play_obj.wait_done()
        speak(f"Riproduco il suono {effect}.")
    else:
        speak("Suono non trovato. Assicurati che il file sia nella cartella.")

def cpu_temp():
    try:
        temps = psutil.sensors_temperatures()
        found = False
        for name in temps:
            for entry in temps[name]:
                speak(f"La temperatura di {entry.label or name} è {entry.current} gradi.")
                found = True
        if not found:
            speak("Non riesco a leggere la temperatura della CPU su questo computer.")
    except:
        speak("Funzione non supportata su questo sistema.")

def disk_space():
    usage = psutil.disk_usage("C:\\" if os.name == "nt" else "/")
    free_gb = round(usage.free / (1024**3), 2)
    total_gb = round(usage.total / (1024**3), 2)
    speak(f"Spazio libero su disco: {free_gb} giga su {total_gb} totali.")

def internet_speed():
    speak("Misuro la velocità di internet, attendi qualche secondo.")
    st = speedtest.Speedtest()
    download = round(st.download() / 1_000_000, 2)
    upload = round(st.upload() / 1_000_000, 2)
    ping = round(st.results.ping, 2)
    speak(f"Download: {download} megabit al secondo. Upload: {upload}. Ping: {ping} millisecondi.")

def download_file(url):
    filename = url.split("/")[-1]
    try:
        response = requests.get(url)
        with open(filename, "wb") as f:
            f.write(response.content)
        speak(f"File scaricato: {filename}")
    except:
        speak("Errore nel download del file.")

def ask_confirmation(azione="procedere"):
    speak(f"Sei sicuro di voler {azione}? Di' Sì per confermare, oppure No per annullare.")
    risposta = listen(4, 5)
    if "sì" in risposta or "si" in risposta:
        return True
    else:
        speak("Operazione annullata.")
        return False

# ---------------------- FUNZIONE CHATGPT --------------------------
def chatgpt_ask(question):
    api_key = settings.get("OPENAI_API_KEY", "")
    model = settings.get("OPENAI_MODEL", "gpt-3.5-turbo")
    if not api_key:
        speak("Non hai impostato la chiave OpenAI nelle impostazioni.")
        return
    openai.api_key = api_key
    try:
        app.log("Chiedo a ChatGPT...")
        completion = openai.ChatCompletion.create(
            model=model,
            messages=[
                {"role": "system", "content": "Rispondi come un assistente vocale italiano, con risposte chiare e concise."},
                {"role": "user", "content": question}
            ],
            max_tokens=700,
            temperature=0.6
        )
        risposta = completion['choices'][0]['message']['content']
        speak(risposta)
    except Exception as e:
        app.log("Errore richiesta OpenAI: " + str(e))
        speak("C'è stato un errore con la richiesta a ChatGPT.")

# ---------------------- COMANDO PRINCIPALE --------------------------
def handle_command(cmd):
    log_command(cmd)
    cmd = cmd.lower()
    if cmd.strip().startswith("cerca chatgpt"):
        domanda = cmd.replace("cerca chatgpt", "").strip()
        if not domanda:
            speak("Dimmi cosa vuoi chiedere a ChatGPT.")
            domanda = listen(5, 10)
        if domanda:
            chatgpt_ask(domanda)
    elif "ciao" in cmd:
        speak("Ciao! Sono il tuo assistente.")
    elif "che ore sono" in cmd:
        ora = datetime.datetime.now().strftime("%H:%M")
        speak(f"Sono le {ora}")
    elif "apri youtube" in cmd:
        webbrowser.open("https://youtube.com")
        speak("Apro YouTube")
    elif "apri discord" in cmd:
        open_discord()
    elif "meteo" in cmd:
        if "a " in cmd:
            city = cmd.split("a ")[-1]
            get_weather(city)
        else:
            get_weather()
    elif "spegni il pc" in cmd:
        if ask_confirmation("spegnere il computer"):
            speak("Spengo il computer.")
            os.system("shutdown /s /t 5")
        else:
            speak("Operazione annullata.")
    elif "riavvia il pc" in cmd or "riavvia il computer" in cmd:
        if ask_confirmation("riavviare il computer"):
            speak("Riavvio il computer.")
            os.system("shutdown /r /t 5")
        else:
            speak("Operazione annullata.")
    elif "riproduci spotify" in cmd:
        play_spotify()
    elif ("cerca spotify" in cmd) or ("riproduci canzone" in cmd) or ("riproduci artista" in cmd):
        if "cerca spotify" in cmd:
            query = cmd.replace("cerca spotify", "").strip()
        elif "riproduci canzone" in cmd:
            query = cmd.replace("riproduci canzone", "").strip()
        elif "riproduci artista" in cmd:
            query = cmd.replace("riproduci artista", "").strip()
        else:
            query = cmd
        if not query:
            speak("Cosa vuoi cercare su Spotify?")
            query = listen(4, 7)
        spotify_search_and_play(query)
    elif "prossima canzone" in cmd or "traccia successiva" in cmd:
        spotify_control("next")
    elif "canzone precedente" in cmd or "traccia precedente" in cmd:
        spotify_control("previous")
    elif "pausa spotify" in cmd or "metti in pausa spotify" in cmd:
        spotify_control("pause")
    elif "riprendi spotify" in cmd or "continua spotify" in cmd:
        spotify_control("play")
    elif "playlist" in cmd and "spotify" in cmd:
        nome_playlist = cmd.split("playlist")[-1].strip()
        spotify_play_playlist(nome_playlist)
    elif "apri netflix" in cmd or "apri prime video" in cmd or "apri disney" in cmd:
        if "netflix" in cmd:
            open_streaming("netflix")
        elif "prime" in cmd:
            open_streaming("prime video")
        elif "disney" in cmd:
            open_streaming("disney plus")
    elif "screenshot" in cmd:
        take_screenshot()
    elif "timer" in cmd:
        minuti = [int(s) for s in cmd.split() if s.isdigit()]
        if minuti:
            set_timer(minuti[0])
        else:
            speak("Non ho capito i minuti del timer.")
    elif "promemoria" in cmd:
        speak("Dimmi cosa devo ricordarti.")
        testo = listen(5, 7)
        if testo:
            set_reminder(testo, 10)
    elif "calcola" in cmd:
        expr = cmd.replace("calcola", "").strip()
        simple_calc(expr)
    elif "cerca su google" in cmd:
        q = cmd.replace("cerca su google", "").strip()
        search_google(q)
    elif "cerca su youtube" in cmd:
        q = cmd.replace("cerca su youtube", "").strip()
        search_youtube(q)
    elif "volume su" in cmd:
        adjust_volume(1)
    elif "volume giù" in cmd:
        adjust_volume(-1)
    elif "prendi nota" in cmd:
        nota = cmd.replace("prendi nota", "").strip()
        if not nota:
            speak("Cosa vuoi che annoti?")
            nota = listen(5, 7)
        if nota:
            save_note(nota)
    elif "invia whatsapp" in cmd:
        try:
            speak("Vuoi inviare a un contatto salvato o inserire un numero? Di' 'contatto' o 'numero'.")
            tipo = listen(5, 5)
            if "contatto" in tipo:
                nomi = list(contacts.keys())
                if not nomi:
                    speak("Nessun contatto salvato. Dimmelo come numero.")
                    tipo = "numero"
                else:
                    speak("Dimmi il nome del contatto.")
                    nome = listen(4, 8)
                    if nome in contacts:
                        speak("Cosa devo scrivere?")
                        message = listen(7, 10)
                        if message:
                            send_whatsapp(nome, message)
                    else:
                        speak("Contatto non trovato.")
            if "numero" in tipo:
                speak("Dimmi il numero con prefisso internazionale, per esempio più 39 e poi il numero")
                number = listen(7, 10)
                speak("Cosa devo scrivere?")
                message = listen(7, 10)
                if number and message:
                    send_whatsapp(number.replace(" ", ""), message)
        except:
            speak("Errore WhatsApp.")
    elif "aggiungi contatto" in cmd:
        speak("Dimmi il nome del contatto da salvare.")
        nome = listen(4, 7)
        speak("Dimmi il numero con prefisso internazionale.")
        numero = listen(7, 10)
        if nome and numero:
            contacts[nome] = numero
            save_contacts(contacts)
            speak("Contatto salvato.")
    elif "rubrica" in cmd or "mostra rubrica" in cmd:
        if contacts:
            lista = ", ".join([f"{n}: {v}" for n, v in contacts.items()])
            speak("I tuoi contatti sono: " + lista)
        else:
            speak("La rubrica è vuota.")
    elif "wikipedia" in cmd or "cerca su wikipedia" in cmd:
        q = cmd.replace("cerca su wikipedia", "").replace("wikipedia", "").strip()
        if not q:
            speak("Cosa vuoi cercare su Wikipedia?")
            q = listen(5, 8)
        if q:
            wiki_search(q)
    elif "racconta una barzelletta" in cmd or "barzelletta" in cmd:
        random_joke()
    elif "numero casuale" in cmd:
        numeri = [int(s) for s in cmd.split() if s.isdigit()]
        if len(numeri) == 2:
            random_number(numeri[0], numeri[1])
        else:
            random_number(1, 100)
    elif "indovina il numero" in cmd:
        guess_the_number()
    elif "applausi" in cmd or "buzzer" in cmd:
        if "applausi" in cmd:
            play_sound("applausi")
        else:
            play_sound("buzzer")
    elif "temperatura cpu" in cmd or "temperatura della cpu" in cmd:
        cpu_temp()
    elif "spazio su disco" in cmd or "spazio libero" in cmd:
        disk_space()
    elif "velocità internet" in cmd or "speedtest" in cmd:
        internet_speed()
    elif "scarica da" in cmd:
        url = cmd.split("scarica da")[-1].strip()
        if not url.startswith("http"):
            speak("Dimmi l'indirizzo completo, a partire da http o https.")
            url = listen(6, 8)
        if url:
            download_file(url)
    elif "ricorda che" in cmd:
        ricordo = cmd.replace("ricorda che", "").strip()
        if not ricordo:
            speak("Cosa devo ricordare?")
            ricordo = listen(5, 7)
        if ricordo:
            save_memory(ricordo)
            speak("Ricorderò questa cosa.")
    elif "cosa devo ricordare" in cmd or "cosa ti ho detto di ricordare" in cmd:
        mem = get_memory()
        if mem:
            speak("Mi hai detto di ricordare queste cose: " + "; ".join(mem))
        else:
            speak("Non mi hai detto di ricordare nulla.")
    elif "esci" in cmd or "fermati" in cmd:
        speak("Va bene, mi fermo. A presto!")
        app.quit_app()
    else:
        speak("Comando non riconosciuto.")

# ---------------------- FUNZIONI TRAY --------------------------
def create_tray_icon(app_instance):
    icon_path = os.path.join(BASE_DIR, 'assistant_virtuale.ico')
    image = Image.open(icon_path)

    def show_window(icon, item):
        app_instance.show_window_from_tray()

    def quit_app(icon, item):
        icon.stop()
        app_instance.quit_app()

    menu = pystray.Menu(
        pystray.MenuItem("Apri Assistente", show_window),
        pystray.MenuItem("Esci", quit_app)
    )
    tray_icon = pystray.Icon("AssistenteVirtuale", image, "Assistente Virtuale", menu)
    return tray_icon

# ---------------------- CLASSE PRINCIPALE --------------------------
class AssistantApp:
    def __init__(self, master):
        self.master = master
        master.title("Assistente Vocale Avanzato")
        master.geometry("680x490")
        master.configure(bg="#23272e")
        style = ttk.Style(master)
        style.theme_use('clam')
        style.configure('TButton', background='#2f3136', foreground='#fff', font=("Segoe UI", 10, "bold"))
        style.configure('TLabel', background='#23272e', foreground='#fff')
        style.configure('TEntry', font=("Segoe UI", 10), fieldbackground="#2f3136", foreground="#fff")
        self.settings = settings

        # Menu impostazioni
        menubar = tk.Menu(master, bg="#23272e", fg="#fff")
        settings_menu = tk.Menu(menubar, tearoff=0, bg="#23272e", fg="#fff")
        settings_menu.add_command(label="Impostazioni", command=self.edit_settings)
        settings_menu.add_command(label="Rubrica", command=self.manage_contacts)
        menubar.add_cascade(label="Menu", menu=settings_menu)
        master.config(menu=menubar)

        # Log
        self.log_panel = scrolledtext.ScrolledText(master, width=78, height=18, state='disabled', bg="#18191c", fg="#c7ccd1", font=("Segoe UI", 9))
        self.log_panel.pack(padx=12, pady=10)

        frame = tk.Frame(master, bg="#23272e")
        frame.pack(pady=2)
        tk.Button(frame, text="Screenshot", command=take_screenshot, bg="#2f3136", fg="#fff").pack(side=tk.LEFT, padx=7)
        tk.Button(frame, text="Spegni PC", command=lambda: handle_command("spegni il pc"), bg="#2f3136", fg="#fff").pack(side=tk.LEFT, padx=7)
        tk.Button(frame, text="Rubrica", command=self.manage_contacts, bg="#2f3136", fg="#fff").pack(side=tk.LEFT, padx=7)

        input_frame = tk.Frame(master, bg="#23272e")
        input_frame.pack(pady=5)
        self.cmd_entry = tk.Entry(input_frame, width=48, font=("Segoe UI", 12), bg="#18191c", fg="#fff", insertbackground="white")
        self.cmd_entry.pack(side=tk.LEFT, padx=3)
        self.cmd_entry.bind('<Return>', self.on_manual_command)
        tk.Button(input_frame, text="Invia", command=self.on_manual_command, bg="#7289da", fg="#fff", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT, padx=4)
        tk.Button(input_frame, text="🎤", command=self.trigger_voice, bg="#43b581", fg="#fff", font=("Segoe UI", 13, "bold")).pack(side=tk.LEFT, padx=2)

        tk.Button(master, text="Nascondi", command=self.hide_window, bg="#7289da", fg="#fff", font=("Segoe UI", 10, "bold")).pack(pady=3)
        tk.Button(master, text="Esci", command=self.quit_app, bg="#ed4245", fg="#fff", font=("Segoe UI", 10, "bold")).pack(pady=5)

        self.stop_listen = False
        self.last_log = ""
        self.tray_icon = None
        self.tray_thread = None
        threading.Thread(target=self.background_listen, daemon=True).start()

    def log(self, text):
        def update_log():
            self.log_panel.configure(state='normal')
            self.log_panel.insert(tk.END, text + "\n")
            self.log_panel.configure(state='disabled')
            self.log_panel.see(tk.END)
        self.master.after(0, update_log)

    def edit_settings(self):
        edit = tk.Toplevel(self.master)
        edit.title("Impostazioni")
        edit.configure(bg="#23272e")
        labels = {}
        entries = {}
        options = {}

        imp_fields = [
            ("WAKE_WORD", "Wake Word"),
            ("CITY", "Città per il meteo"),
            ("VOICE_SPEED", "Velocità voce (es. 0.9, 1.0, 1.2)"),
            ("SPOTIFY_CLIENT_ID", "Spotify Client ID"),
            ("SPOTIFY_CLIENT_SECRET", "Spotify Secret"),
            ("SPOTIFY_REDIRECT_URI", "Spotify Redirect URL"),
            ("OPENAI_API_KEY", "OpenAI API Key")
        ]
        for i, (key, label) in enumerate(imp_fields):
            ttk.Label(edit, text=label + ":", background="#23272e", foreground="#fff").grid(row=i, column=0, padx=12, pady=6, sticky="e")
            entries[key] = ttk.Entry(edit, width=35)
            entries[key].insert(0, self.settings.get(key, ""))
            entries[key].grid(row=i, column=1, padx=10, pady=6, sticky="w")

        # Modello GPT
        ttk.Label(edit, text="Modello ChatGPT:", background="#23272e", foreground="#fff").grid(row=len(imp_fields), column=0, padx=12, pady=6, sticky="e")
        model_var = tk.StringVar(edit)
        model_var.set(self.settings.get("OPENAI_MODEL", "gpt-3.5-turbo"))
        models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
        model_box = ttk.Combobox(edit, textvariable=model_var, values=models, width=33, state="readonly")
        model_box.grid(row=len(imp_fields), column=1, padx=10, pady=6, sticky="w")

        def save_and_close():
            for key in entries:
                self.settings[key] = entries[key].get()
            self.settings["OPENAI_MODEL"] = model_var.get()
            save_settings(self.settings)
            messagebox.showinfo("Impostazioni", "Impostazioni salvate.")
            edit.destroy()

        tk.Button(edit, text="Salva", command=save_and_close, bg="#43b581", fg="#fff").grid(row=len(imp_fields)+1, column=0, columnspan=2, pady=13)

    def manage_contacts(self):
        win = tk.Toplevel(self.master)
        win.title("Rubrica")
        win.configure(bg="#23272e")
        tk.Label(win, text="Contatti WhatsApp salvati:", bg="#23272e", fg="#fff", font=("Segoe UI", 10, "bold")).pack(pady=6)
        contacts_list = tk.Listbox(win, width=44, height=10, font=("Segoe UI", 10), bg="#18191c", fg="#fff")
        contacts_list.pack(padx=8, pady=4)
        for nome, num in contacts.items():
            contacts_list.insert(tk.END, f"{nome} → {num}")

        def add_contact():
            nome = simpledialog.askstring("Nome", "Nome contatto:", parent=win)
            numero = simpledialog.askstring("Numero", "Numero (con +39...):", parent=win)
            if nome and numero:
                contacts[nome] = numero
                save_contacts(contacts)
                contacts_list.insert(tk.END, f"{nome} → {numero}")

        def delete_selected():
            sel = contacts_list.curselection()
            if sel:
                nome_num = contacts_list.get(sel[0])
                nome = nome_num.split("→")[0].strip()
                if nome in contacts:
                    del contacts[nome]
                    save_contacts(contacts)
                    contacts_list.delete(sel[0])

        btn_frame = tk.Frame(win, bg="#23272e")
        btn_frame.pack(pady=7)
        tk.Button(btn_frame, text="Aggiungi", command=add_contact, bg="#43b581", fg="#fff").pack(side=tk.LEFT, padx=6)
        tk.Button(btn_frame, text="Elimina", command=delete_selected, bg="#ed4245", fg="#fff").pack(side=tk.LEFT, padx=6)
        tk.Button(win, text="Chiudi", command=win.destroy, bg="#23272e", fg="#fff").pack(pady=7)

    def on_manual_command(self, event=None):
        cmd = self.cmd_entry.get()
        if cmd:
            self.cmd_entry.delete(0, tk.END)
            handle_command(cmd)

    def trigger_voice(self):
        speak("In ascolto. Di' pure il comando.")
        comando = listen(6, 9)
        if comando:
            handle_command(comando)

    def background_listen(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            while not self.stop_listen:
                if self.last_log != "Attesa wake word...":
                    self.log("Attesa wake word...")
                    self.last_log = "Attesa wake word..."
                try:
                    audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    try:
                        query = recognizer.recognize_google(audio, language='it-IT')
                        self.log("Tu: " + query)
                        self.last_log = "Tu"
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError:
                        speak("Errore di connessione.")
                        continue

                    if self.settings["WAKE_WORD"] in query.lower():
                        speak("Eccomi, dimmi pure.")
                        try:
                            audio2 = recognizer.listen(source, timeout=7, phrase_time_limit=7)
                            comando = recognizer.recognize_google(audio2, language='it-IT')
                            self.log("Tu: " + comando)
                            self.last_log = "Tu"
                            if comando:
                                handle_command(comando)
                        except sr.UnknownValueError:
                            speak("Non ho capito, ripeti pure.")
                        except sr.WaitTimeoutError:
                            speak("Nessun comando rilevato.")
                        except sr.RequestError:
                            speak("Errore di connessione.")
                except sr.WaitTimeoutError:
                    continue
                time.sleep(0.18)

    def hide_window(self):
        self.master.withdraw()
        if not self.tray_icon:
            self.tray_icon = create_tray_icon(self)
            self.tray_thread = threading.Thread(target=self.tray_icon.run, daemon=True)
            self.tray_thread.start()

    def show_window_from_tray(self):
        self.master.after(0, self.master.deiconify)
        if self.tray_icon:
            self.tray_icon.stop()
            self.tray_icon = None

    def quit_app(self):
        self.stop_listen = True
        speak("Chiusura assistente. Arrivederci!")
        if self.tray_icon:
            self.tray_icon.stop()
        self.master.quit()

# ---------------------- AVVIO APP --------------------------
root = tk.Tk()
app = AssistantApp(root)
root.after(900, lambda: speak("Assistente pronto. Di' la wake word o scrivi un comando!"))
root.mainloop()
