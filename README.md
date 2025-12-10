# Tgautodownloader

Bot Telegram Docker-friendly per scaricare video da link (YouTube, Instagram, TikTok, X/Twitter, Facebook, ecc.) usando `yt-dlp`, salvarli in una cartella e rimandarli all'utente. Include una web GUI locale per vedere stato download e log.

## 1. Preparazione rapidissima (versione breve)
1. Installa Python 3.11+ e Docker (opzionale ma consigliato).
2. Clona o scarica questa cartella.
3. Apri `app/config.py` e:
   - Incolla il tuo `BOT_TOKEN` di Telegram.
   - Metti il tuo ID Telegram in `ALLOWED_USER_IDS` (es. `[123456789]`). Solo questi ID potranno usare il bot.
   - (Opzionale) regola `DOWNLOAD_DIR`, `MAX_UPLOAD_NO_API_MB`, `MAX_UPLOAD_WITH_LOCAL_API_MB`, `MAX_DOWNLOAD_SIZE_MB` e la porta web `WEB_APP_PORT`.
   - (Opzionale) abilita `TELEGRAM_BOT_API_ENABLED` e imposta `TELEGRAM_BOT_API_BASE_URL`/`TELEGRAM_BOT_API_FILE_URL` se vuoi usare un server Telegram Bot API self-hosted per inviare file fino al limite locale configurato.
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
4. (Opzionale) Per inviare file fino a 2 GB abilita `TELEGRAM_BOT_API_ENABLED = True` e indica le URL del tuo server Bot API (`TELEGRAM_BOT_API_BASE_URL` e `TELEGRAM_BOT_API_FILE_URL`). Puoi regolare i limiti di upload via `MAX_UPLOAD_NO_API_MB` (API ufficiale) e `MAX_UPLOAD_WITH_LOCAL_API_MB` (API locale), mentre `MAX_DOWNLOAD_SIZE_MB` impedisce di scaricare file troppo grandi in locale.
5. Salva il file. Non servono `.env` o variabili ambiente: tutto è in `config.py`.

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
   - Se il file è entro il limite attivo (50 MB con l'API ufficiale, ~2 GB con Bot API self-hosted), ricevi il video (o un documento se l'invio video fallisce). Se la dimensione stimata supera `MAX_DOWNLOAD_SIZE_MB`, il download viene bloccato a monte.
   - Se supera il limite, ricevi un messaggio di file troppo grande. Se l'API self-hosted non è configurata, il bot ti dirà che il file è stato scaricato completamente ma non può caricarlo per il limite da 50 MB.
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

## 7. Come abilitare Telegram Bot API self-hosted (upload fino a 2 GB)
La Telegram Bot API ufficiale consente upload fino a 50 MB. Se vuoi spedire file più grandi (fino a circa 2 GB) devi far girare un'istanza self-hosted del server Bot API e puntare il bot verso di essa.

### Avvio rapido con Docker
```bash
docker run --name telegram-bot-api --rm -p 8081:8081 \
  -v telegram-bot-api-data:/var/lib/telegram-bot-api \
  ghcr.io/tdlib/telegram-bot-api:latest --api-id=<API_ID> --api-hash=<API_HASH> --http-port=8081
```
Note importanti:
- Recupera `api_id` e `api_hash` dal tuo account su https://my.telegram.org/apps.
- Esporre la porta 8081 è solo un esempio: puoi cambiarla, ma dovrai aggiornare `TELEGRAM_BOT_API_BASE_URL` e `TELEGRAM_BOT_API_FILE_URL` di conseguenza.
- Monta un volume per preservare i dati tra i riavvii (es. `telegram-bot-api-data`).

### Configurazione in `app/config.py`
1. Imposta `TELEGRAM_BOT_API_ENABLED = True`.
2. Imposta `TELEGRAM_BOT_API_BASE_URL` con il tuo endpoint `/bot` (es. `http://127.0.0.1:8081/bot`).
3. Imposta `TELEGRAM_BOT_API_FILE_URL` con l'endpoint `/file/bot` (es. `http://127.0.0.1:8081/file/bot`).
4. Avvia il bot normalmente (`python -m app.main` o via Docker). Ora il limite attivo sarà ~2 GB (configurabile con `MAX_UPLOAD_WITH_LOCAL_API_MB`).

### Comportamento lato bot
- **Bot API disabilitata (default):** limite 50 MB. Se il file scaricato è più grande, il bot segnala che è stato scaricato ma non può inviarlo per il limite ufficiale.
- **Bot API abilitata:** limite ~2 GB. Se superi comunque il limite, ricevi il messaggio standard di file troppo grande.

Buon download! 🎬
