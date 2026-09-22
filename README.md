# Ultradub

Your voice, in every language.

Upload a video you recorded, pick the language you speak and up to 3 languages to dub into
(20 of the world's most spoken languages). Choose a natural AI voice or your own voice, add lip
matching if you want it, watch a free 15-second preview, then pay once and download every
version with subtitles.

## Settings (Streamlit secrets)

Required
- GOOGLE_API_KEY: Speech-to-Text, Translation and Text-to-Speech enabled
- STRIPE_SECRET_KEY
- APP_URL: the public address of this app, used for the payment return

Optional
- ELEVENLABS_API_KEY: turns on the "My own voice" option
- SYNCLABS_API_KEY: turns on lip matching
- SUPPORT_EMAIL: shown in the footer and in delivery messages
- DEMO_ORIGINAL_URL, DEMO_DUBBED_URL, DEMO_CAPTION: demo clips (or commit demo/original.mp4 and demo/dubbed.mp4)

Finished videos are kept for 24 hours. If a paid video is missing (for example after a server
restart), the customer is refunded automatically.
