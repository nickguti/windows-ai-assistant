-----------------------------------------

Assistente Vocale Avanzato – nickguti  
=====================================

Versione: 1.0.0 – Release italiana  
Autore: nickguti  
Data: 30 giugno 2025

Un assistente vocale moderno, scritto in Python con interfaccia grafica, pensato per l’automazione personale su Windows. Consente comandi vocali, domande a ChatGPT, controllo Spotify, invio WhatsApp, gestione appunti, meteo, screenshot, ricerche online, giochi, gestione hardware e molto altro. Interamente in italiano, progettato per essere espandibile anche per la domotica.

-----------------------------------------

Introduzione  
------------

**nickguti** nasce per offrire un assistente virtuale semplice e potente, con GUI moderna, comando vocale o testuale, piena personalizzazione e sicurezza (dati solo in locale). Perfetto per chi vuole una soluzione personale, pronta all’uso, ma anche per chi vuole imparare o espandere il progetto con nuove integrazioni smart home.

-----------------------------------------

Funzionalità principali  
-----------------------

- Wake word personalizzabile (es: “francesco”)
- Riconoscimento vocale e sintesi vocale in italiano
- Interfaccia grafica intuitiva (Tkinter) con tray icon
- Comandi vocali e testuali per:
    - Spotify: riproduzione, ricerca, playlist, controllo tracce
    - Meteo: aggiornato per città scelta
    - WhatsApp: invio messaggi, rubrica integrata
    - ChatGPT: domande in tempo reale (richiede API OpenAI)
    - Google, YouTube, Wikipedia: ricerca automatica o vocale
    - Calcolatrice, timer, promemoria
    - Giochi: barzellette, indovina il numero, numeri random
    - Screenshot rapido del desktop
    - Info hardware: spazio disco, temperatura CPU, speedtest internet
    - Gestione appunti e memoria personale
    - Personalizzazione impostazioni tramite GUI
- Dati e rubrica sempre solo in locale (no cloud)
- Facilmente espandibile (es. domotica: vedi sotto)

-----------------------------------------

Installazione  
-------------

1. Clona il repository  
   git clone https://github.com/nickguti/nickguti.git  
   cd nickguti

2. Installa le dipendenze  
   pip install -r requirements.txt

3. Esegui l’assistente  
   python assistant.py

4. (Facoltativo) Personalizza le impostazioni di OpenAI, Spotify, ecc. direttamente dalla finestra delle impostazioni dell’app.

5. (Opzionale) Crea il file eseguibile .exe:  
   pip install pyinstaller  
   pyinstaller --onefile --noconsole assistant.py  
   L’eseguibile si trova nella cartella dist/.

-----------------------------------------

Espansione domotica  
-------------------

Il codice è pronto per essere integrato con dispositivi smart home: puoi aggiungere moduli Python per MQTT, REST API, controlli custom ecc. Vedi gli esempi e i commenti nel codice sorgente per integrare la domotica secondo le tue esigenze.

-----------------------------------------

Dipendenze principali  
---------------------

- Python 3.8+
- tkinter
- speech_recognition
- gtts
- pydub
- pystray
- spotipy
- simpleaudio
- psutil
- pyautogui
- pywhatkit
- openai
- speedtest-cli
- wikipedia
- Pillow

(Tutte le dipendenze sono elencate in requirements.txt).

-----------------------------------------

Licenza  
-------

Questo progetto è distribuito sotto licenza MIT.

-----------------------------------------

Autore: nickguti  
Versione: 1.0.0  
Data: 30/06/2025  

-----------------------------------------
