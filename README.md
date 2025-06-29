Assistente Vocale Avanzato
==========================

Versione: 1.3 - Release italiana  
Autore: nickguti  
Data: 29 giugno 2025

Un assistente vocale moderno scritto in Python con interfaccia grafica. Permette di eseguire comandi vocali, interrogare ChatGPT, gestire Spotify, inviare messaggi WhatsApp, salvare note e appunti, controllare il meteo, eseguire screenshot, fare ricerche su Google, YouTube, Wikipedia e molto altro. Progettato per essere espandibile anche con funzionalità di domotica.

-----------------------------------------

Introduzione
------------

Questo progetto nasce per offrire un assistente virtuale facile da usare, personalizzabile, scritto in Python e adatto a ogni esigenza quotidiana. Si integra facilmente con servizi online e permette di aggiungere nuove funzioni, inclusa la domotica.

-----------------------------------------

Funzionalità principali
-----------------------

- Comandi vocali: riconoscimento vocale e risposta tramite sintesi vocale  
- Integrazione con ChatGPT/OpenAI: domande e risposte in tempo reale  
- Gestione Spotify: ricerca, riproduzione brani, controllo playlist e device  
- Invio WhatsApp: invia messaggi a numeri o contatti salvati  
- Rubrica integrata: salva e gestisci i contatti per WhatsApp  
- Appunti e note: prendi nota rapidamente  
- Meteo: informazioni sul tempo per la tua città  
- Screenshot: cattura lo schermo facilmente  
- Ricerche online: Google, YouTube, Wikipedia  
- Barzellette, numeri casuali, giochi  
- Timer, promemoria, calcolatrice  
- Controllo hardware: temperatura CPU, spazio disco, speedtest internet  
- Tray icon: l'app si minimizza nella barra delle applicazioni di sistema  

-----------------------------------------

Installazione
-------------

1. Clona il repository  
   git clone https://github.com/nickguti/assistente-vocale.git  
   cd assistente-vocale

2. Installa le dipendenze  
   pip install -r requirements.txt

3. Esegui l’assistente  
   python assistant.py

4. (Facoltativo) Configura le impostazioni per OpenAI, Spotify ecc. dalla finestra delle impostazioni.

-----------------------------------------

Espansione domotica
-------------------

Il codice è pensato per essere facilmente integrato con dispositivi smart home tramite moduli aggiuntivi Python (ad esempio requests per chiamate REST, paho-mqtt per MQTT, ecc). Consulta la documentazione interna del codice per esempi di estensione.

-----------------------------------------

Dipendenze principali
---------------------

- Python 3.8+
- tkinter, speech_recognition, gtts, pydub, pystray, spotipy, simpleaudio, psutil, pyautogui, pywhatkit, openai, speedtest, wikipedia, Pillow, ecc.

Vedi requirements.txt per l’elenco completo.

-----------------------------------------

Licenza
-------

Questo progetto è distribuito sotto licenza MIT.

-----------------------------------------

Autore: nickguti  
Versione: 1.3  
Data: 29/06/2025
