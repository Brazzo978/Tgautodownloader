"""
Configurazione centralizzata per il bot Telegram di download video.
Modifica i valori qui sotto per personalizzare il comportamento del bot.
"""

BOT_TOKEN = "INSERISCI_QUI_IL_TUO_TOKEN_TELEGRAM"
DOWNLOAD_DIR = "/downloads"
MAX_FILE_SIZE_MB = 45
LOG_LEVEL = "INFO"

# Controlla se eliminare i file locali dopo l'invio su Telegram
DELETE_AFTER_SEND = False

# Solo gli ID Telegram indicati qui possono usare il bot (whitelist forte)
# Puoi ottenere il tuo ID tramite @userinfobot o simili.
ALLOWED_USER_IDS = [123456789]

# Configurazione web GUI locale
WEB_APP_HOST = "0.0.0.0"
WEB_APP_PORT = 8000
LOG_BUFFER_LIMIT = 200

WELCOME_MESSAGE = (
    "👋 Ciao! Inviami un link YouTube/Instagram/TikTok ecc. "
    "e proverò a scaricare il video e rimandartelo come file.\n"
    "Dimensione massima invio: {max_mb} MB."
)

DOWNLOADING_MESSAGE = "Sto scaricando il video, un attimo..."
INVALID_URL_MESSAGE = "Per favore inviami un link valido (http/https)."
UNAUTHORIZED_MESSAGE = "Accesso non autorizzato: questo bot è privato."
ERROR_MESSAGE = (
    "❌ Errore durante il download o l'invio del video. "
    "Riprova con un altro link."
)
FILE_TOO_LARGE_MESSAGE = (
    "❌ Il file scaricato supera il limite di {max_mb} MB e non può essere inviato."
)
