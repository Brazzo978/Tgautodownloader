# Tgautodownloader

Bot Telegram Docker-friendly per scaricare video da link (YouTube, Instagram, TikTok, X/Twitter, Facebook, ecc.) usando `yt-dlp`, salvarli in una cartella e rimandarli all'utente. Include una web GUI locale per vedere stato download e log.

## 1. Preparazione rapidissima (versione breve)
1. Installa Python 3.11+ e Docker (opzionale ma consigliato).
2. Clona o scarica questa cartella.
3. Apri `app/config.py` e:
   - Incolla il tuo `BOT_TOKEN` di Telegram.
   - Metti il tuo ID Telegram in `ALLOWED_USER_IDS` (es. `[123456789]`). Solo questi ID potranno usare il bot.
   - (Opzionale) regola `DOWNLOAD_DIR`, `MAX_FILE_SIZE_MB` e la porta web `WEB_APP_PORT`.
   - (Opzionale) imposta `DELETE_AFTER_SEND` a `True` se vuoi cancellare automaticamente i file locali dopo l'invio.
4. Scegli come avviarlo:
   - **Locale:** `pip install -r requirements.txt` poi `python -m app.main`.
   - **Docker:** `docker build -t telegram-video-bot .` poi `docker run --rm -p 8000:8000 -v /percorso/locale/downloads:/downloads telegram-video-bot`.
5. Apri la web GUI su `http://localhost:8000` per vedere download e log.

## 2. Guida passo-passo per chi parte da zero
### Ottieni token e tuo ID
- Crea un bot con [@BotFather](https://t.me/BotFather) e copia il token.
- Recupera il tuo ID Telegram inviando un messaggio a [@userinfobot](https://t.me/userinfobot) o simili.

### Configura il progetto
1. Apri `app/config.py` e sostituisci:
   - `BOT_TOKEN = "INSERISCI_QUI_IL_TUO_TOKEN_TELEGRAM"`
   - `ALLOWED_USER_IDS = [123456789]` → metti il tuo ID (puoi aggiungere altri separati da virgola).
2. Se vuoi cambiare cartella download o porta web, modifica `DOWNLOAD_DIR` e `WEB_APP_PORT` (di default la cartella è `/downloads`).
3. Per controllare se i file scaricati vanno cancellati dopo l'invio, regola `DELETE_AFTER_SEND` (di default è `False`).
4. Salva il file. Non servono `.env` o variabili ambiente: tutto è in `config.py`.

### Avvio in locale (senza Docker)
```bash
# Dentro la cartella del progetto
a) pip install -r requirements.txt
b) python -m app.main
```
- Il bot parte e contemporaneamente lancia la web GUI su `http://localhost:8000`.
- La cartella di download viene creata automaticamente se non esiste.

### Avvio con Docker
```bash
docker build -t telegram-video-bot .
# Monta una cartella locale per conservare i download e pubblica la porta web
docker run --rm -p 8000:8000 -v /percorso/locale/downloads:/downloads telegram-video-bot
```
Note:
- Prima di buildare, assicurati di aver già modificato `app/config.py`.
- Sostituisci `/percorso/locale/downloads` con una cartella reale del tuo PC.

### Avvio con Docker Compose (opzionale)
```bash
docker compose up --build
```
Il file `docker-compose.yml` monta `./downloads` sulla cartella del container `/downloads` e pubblica la porta `8000`.

## 3. Come si usa il bot (lato Telegram)
1. Apri il tuo bot su Telegram e manda `/start` (solo gli ID in whitelist ricevono risposta).
2. Invia un link a un video (YouTube/Instagram/TikTok/X/Facebook ecc.).
3. Il bot risponde "Sto scaricando il video" e poi:
   - Se il file è entro `MAX_FILE_SIZE_MB`, ricevi il video (o un documento se l'invio video fallisce).
   - Se supera il limite, ricevi un messaggio di file troppo grande.
4. Se `DELETE_AFTER_SEND` è `True`, i file scaricati vengono eliminati dopo l'invio; con `False` rimangono nella cartella download.

## 4. Web GUI locale
- Indirizzo: `http://localhost:8000`
- Cosa mostra:
  - Tabella con download recenti (URL, utente, stato, dettagli).
  - Log recenti dell'applicazione.
- Puoi consumare i dati anche via API:
  - `GET /api/status` → JSON con i download.
  - `GET /api/logs` → JSON con i log recenti.

## 5. Sicurezza: whitelist forte
- Solo gli ID inseriti in `ALLOWED_USER_IDS` possono interagire con il bot. Tutti gli altri ricevono `Accesso non autorizzato`.
- Mantieni privato il tuo `BOT_TOKEN`.

## 6. Note tecniche
- Dipendenze principali: `python-telegram-bot`, `yt-dlp`, `fastapi`, `uvicorn` (vedi `requirements.txt`).
- Entrypoint: `python -m app.main` (avvia bot e web GUI insieme).
- Configurazione unica in `app/config.py` (nessun `.env` o variabili ambiente).

Buon download! 🎬
