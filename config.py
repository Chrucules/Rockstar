import os
from dotenv import load_dotenv

load_dotenv()


# ==========================
# ROCKSTAR OWNER
# ==========================

OWNER_ID = 1123499695831003197


# ==========================
# BOT TOKEN
# ==========================

TOKEN = os.getenv("DISCORD_TOKEN")


# ==========================
# EMBED SETTINGS
# ==========================

BOT_NAME = "⭐ Rockstar"

EMBED_COLOR = 0xFFD700

FOOTER_TEXT = "Powered by Paran LLC"

DEFAULT_GIF = ""


# ==========================
# BOT SETTINGS
# ==========================

BOT_ENABLED = True

SAFETY_MODE = False


# ==========================
# JOIN / LEAVE SETTINGS
# ==========================

JOIN_CHANNEL_ID = 1529493555779993600

LEAVE_CHANNEL_ID = 1529493555779993600


# ==========================
# JOIN EMBED
# ==========================

JOIN_TITLE = "Cool person alert"

JOIN_MESSAGE = (
    "Welcome {member} to **{server}**!\n\n"
    "You are member **#{count}**.\n\n"
    "Thanks for being a real one."
)

JOIN_GIF = "https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXAyZGp2NjZvMXg2eGptNTUyaGFvdHJ0NHl6eTdtanY4NHgxajdoYSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/UfkRsHmoNZtjXjQT6S/giphy.gif"


# ==========================
# LEAVE EMBED
# ==========================

LEAVE_TITLE = "Lame person alert"

LEAVE_MESSAGE = (
    "{member} was a bitch and left **{server}**.\n\n"
    "psi ah nih"
)

LEAVE_GIF = "https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExb2lhcTl2NGh1bTdlMG43N3ltbGJjM2lsM252dm94djVmZGp6aDZ2MCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/KAAPBD2YIoB6UFprmg/giphy.gif"