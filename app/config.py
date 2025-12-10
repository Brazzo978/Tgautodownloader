"""
Configurazione centralizzata per il bot Telegram di download video.
Modifica i valori qui sotto per personalizzare il comportamento del bot.
"""

BOT_TOKEN = "INSERISCI_QUI_IL_TUO_TOKEN_TELEGRAM"
DOWNLOAD_DIR = "/downloads"
MAX_FILE_SIZE_MB = 50
LOG_LEVEL = "INFO"

# Abilita l'uso di un'istanza self-hosted di Telegram Bot API per inviare file fino a 2 GB
TELEGRAM_BOT_API_ENABLED = False
TELEGRAM_BOT_API_BASE_URL = "http://127.0.0.1:8081/bot"
TELEGRAM_BOT_API_FILE_URL = "http://127.0.0.1:8081/file/bot"
TELEGRAM_BOT_API_MAX_FILE_SIZE_MB = 2000

# Controlla se eliminare i file locali dopo l'invio su Telegram
DELETE_AFTER_SEND = False

# Solo gli ID Telegram indicati qui possono usare il bot (whitelist forte)
# Puoi ottenere il tuo ID tramite @userinfobot o simili.
ALLOWED_USER_IDS = [123456789]

# Configurazione web GUI locale
WEB_APP_HOST = "0.0.0.0"
WEB_APP_PORT = 12000
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
SELF_HOSTED_TIMEOUT_MESSAGE = (
    "⚠️ Il server Bot API self-hosted sta ancora elaborando il video. "
    "Attendilo qualche secondo: se non arriva, riprova più tardi."
)
FILE_TOO_LARGE_MESSAGE = (
    "❌ Il file scaricato supera il limite di {max_mb} MB e non può essere inviato."
)

FILE_TOO_LARGE_BOT_API_DISABLED = (
    "✅ Ho scaricato il file (circa {size_gb:.2f} GB), ma non posso caricarlo perché "
    "il limite dell'API ufficiale è {max_mb} MB. Abilita una Telegram Bot API self-hosted "
    "per inviare file fino a 2 GB."
)

FILE_ALREADY_PRESENT_MESSAGE = (
    "♻️ Il file '{filename}' è già presente sul server. Lo reinvio subito su Telegram."
)


def active_upload_limit_mb() -> int:
    """Restituisce il limite massimo di upload attualmente configurato."""

    if TELEGRAM_BOT_API_ENABLED:
        return TELEGRAM_BOT_API_MAX_FILE_SIZE_MB
    return MAX_FILE_SIZE_MB
