import streamlit as st
import os
import random
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path
TEXT_MODELS = [
    "gemini-2.0-flash",
    "gemini-2.5-flash",
    "gemini-2.5-flash-lite",
    "gemini-3-flash"
]

# --------------------------------------------------
# 1. CONFIGURATION
# --------------------------------------------------

load_dotenv(dotenv_path=Path(__file__).parent / ".env")

GEMINI_KEY = None

try:
    if "GEMINI_API_KEY" in st.secrets:
        GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    pass

if not GEMINI_KEY:
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_KEY:
    genai.configure(api_key=GEMINI_KEY)

# --------------------------------------------------
# 2. CORE LOGIC
# --------------------------------------------------

AUDIO_FOLDER = Path(__file__).parent / "audio"

def get_random_demo_audio():
    if not AUDIO_FOLDER.exists():
        return None
    files = list(AUDIO_FOLDER.glob("*.wav")) + list(AUDIO_FOLDER.glob("*.mp3"))
    return random.choice(files) if files else None

def split_lyrics_and_vibe(text):
    if not text:
        return None, None
    if "VIBE:" in text:
        lyrics, vibe = text.rsplit("VIBE:", 1)
        return lyrics.strip(), vibe.strip()
    return text.strip(), "punk rock raw distorted chaotic fast aggressive"

def get_diss_lyrics(prompt_input):
    prompt = (
        f"Act as a satirical punk-rocker. Write a loud, rebellious punk track about {prompt_input}. "
        "Use [Verse] and [Chorus] tags. "
        "Make it chaotic, sarcastic, and raw. "
        "End the response with a single line labeled 'VIBE:' followed by a 10-word music genre prompt."
    )

    last_error = None

    for model_name in TEXT_MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt)

            # Optional debug log (remove later if you want)
            st.caption(f"🧠 Lyrics generated using `{model_name}`")

            return response.text

        except Exception as e:
            error_text = str(e)
            last_error = error_text

            # If quota/rate issue → try next model
            if "429" in error_text or "RESOURCE_EXHAUSTED" in error_text:
                continue
            else:
                # Non-quota error → stop immediately
                break

    # All models failed
    st.error(
        "⚠️ All lyric engines are tapped out.\n\n"
        "The words are dead. The noise is not."
    )

    # Optional: log last error for debugging
    st.error(f"Last Gemini error: {last_error}")

    return None


# --------------------------------------------------
# 3. UI CONFIG — ORIGINAL CHAOS (VERSION A)
# --------------------------------------------------

st.set_page_config(
    page_title="Punky Pandey",
    page_icon="🎸",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Permanent+Marker&family=Special+Elite&display=swap');

/* Background: Tri-color Punk Grunge Gradient */
.stApp {
    background: linear-gradient(180deg, #0f0f0f, #ff00ff, #00ffff, #ffff00);
    background-size: 400% 400%;
    animation: gradientShift 8s ease infinite;
}

/* Lyrics Box */
.lyrics-display {
    background: #000;
    color: #00ff00;
    padding: 28px;
    border: 10px solid #ff00ff;
    border-style: outset;
    font-family: 'Special Elite', monospace;
    white-space: pre-wrap;
    margin-top: 40px;
    box-shadow: 15px 15px 0 #ffff00;
    transform: rotate(1deg);
    animation: boxWobble 2s ease-in-out infinite alternate;
}

/* Animations */
@keyframes gradientShift {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

@keyframes boxWobble {
    from { transform: rotate(1deg) scale(1); }
    to { transform: rotate(-1deg) scale(1.02); }
}

/* Main Poster */
.main .block-container {
    position: relative;
    z-index: 2;
    max-width: 700px;
    min-height: 90vh;
    padding: 55px 45px;
    border: 10px solid #000;
    box-shadow: 22px 22px 0 #111;
    background: #e0e0e0;
}

/* Fixed Guitar */
#guitar-bg {
    position: fixed;
    top: 50%;
    left: 50%;
    width: 620px;
    height: 620px;
    transform: translate(-50%, -50%) rotate(-12deg);
    background: url("https://images.unsplash.com/photo-1511379938547-c1f69419868d")
                center / contain no-repeat;
    opacity: 0.6;
    z-index: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
}

/* LOGO */
.logo-wrap {
    text-align: center;
    margin-bottom: 25px;
    transform: rotate(-2deg);
}

.logo-main {
    font-family: 'Permanent Marker', cursive;
    font-size: 4.2rem;
    color: #ff00ff;
    background: #000;
    display: inline-block;
    padding: 10px 25px;
    border: 6px solid #ffff00;
    box-shadow: 8px 8px 0 #00ffff;
    text-shadow: 3px 3px 0 #000;
}

.logo-sub {
    font-family: 'Special Elite', monospace;
    font-size: 2.2rem;
    margin-top: 8px;
    color: #00ff00;
    letter-spacing: 6px;
    text-shadow: -2px 0 #ff0000, 2px 0 #00ffff;
}

/* FAKE TORN PAPER UNDERLINE */
.torn-underline {
    width: 220px;
    height: 14px;
    margin: 12px auto 0 auto;
    background: #ffff00;
    position: relative;
    transform: rotate(-1deg);
    box-shadow: 4px 4px 0 #000;
    clip-path: polygon(
        0% 40%, 5% 60%, 10% 45%, 15% 65%, 20% 50%,
        25% 70%, 30% 48%, 35% 68%, 40% 52%, 45% 72%,
        50% 50%, 55% 70%, 60% 48%, 65% 68%, 70% 52%,
        75% 72%, 80% 50%, 85% 65%, 90% 45%, 95% 60%, 100% 40%
    );
    animation: tearWiggle 1.8s infinite alternate ease-in-out;
}

@keyframes tearWiggle {
    from { transform: rotate(-1deg) translateX(-1px); }
    to { transform: rotate(1deg) translateX(1px); }
}

/* Input */
.stTextInput input {
    background: #ffff00;
    color: #ff00ff;
    border: 5px dashed #000;
    font-family: 'Special Elite', monospace;
    font-size: 1.25rem;
    padding: 14px;
    box-shadow: 10px 10px 0 #00ffff;
}

.stTextInput input:hover {
    transform: rotate(-2deg) scale(1.05);
    background: #00ffff;
    color: #000;
    box-shadow: -10px -10px 0 #ff00ff;
}

.stTextInput input:focus {
    transform: scale(1.1);
    border: 5px solid #ff0000;
    animation: jitter 0.1s infinite;
}

/* Button */
.stButton > button {
    width: 100%;
    background: #ff00ff;
    color: #fff;
    border: 6px double #ffff00;
    font-family: 'Permanent Marker', cursive;
    font-size: 2.2rem;
    padding: 16px;
    margin-top: 20px;
    text-shadow: 3px 3px 0 #000;
}

.stButton > button:hover {
    background: #ffff00;
    color: #000;
    transform: skew(10deg) scale(1.02);
    cursor: help;
}

.stButton > button:active {
    transform: scale(0.8) rotate(10deg);
    background: #ff0000;
    border: 10px solid #000;
}

@keyframes jitter {
    0% { transform: translate(1px, 1px); }
    50% { transform: translate(-1px, -1px); }
    100% { transform: translate(1px, 1px); }
}

</style>

<div id="guitar-bg"></div>

<script>
window.addEventListener("scroll", () => {
    const guitar = document.getElementById("guitar-bg");
    guitar.style.opacity = window.scrollY > 150 ? "0" : "0.6";
});
</script>
""", unsafe_allow_html=True)

# --------------------------------------------------
# 4. UI LOGIC (FINAL — CONDITIONAL AUDIO)
# --------------------------------------------------

st.markdown("""
<div class="logo-wrap">
  <div class="logo-main">PUNKY</div>
  <div class="logo-sub">PΛNDEY</div>
  <div class="torn-underline"></div>
</div>
""", unsafe_allow_html=True)

prompt_input = st.text_input(
    "DROP A NAME, MOOD, OR THOUGHT:",
    placeholder="rage, boredom, system, noise, freedom..."
)

# Initialize state flags safely
if "generation_attempted" not in st.session_state:
    st.session_state.generation_attempted = False
if "gemini_failed" not in st.session_state:
    st.session_state.gemini_failed = False
if "lyrics" not in st.session_state:
    st.session_state.lyrics = None

# --- MAIN ACTION ---
if st.button("IGNITE PUNK ⚡"):
    st.session_state.generation_attempted = True
    st.session_state.gemini_failed = False
    st.session_state.lyrics = None

    raw = get_diss_lyrics(
        prompt_input.strip() if prompt_input.strip() else "the system"
    )

    if raw:
        lyrics, vibe = split_lyrics_and_vibe(raw)
        st.session_state.lyrics = lyrics
        st.session_state.vibe = vibe
    else:
        st.session_state.gemini_failed = True

# --------------------------------------------------
# RESULT AREA (ONLY AFTER BUTTON CLICK)
# --------------------------------------------------

# Case 1: Lyrics generated
if st.session_state.generation_attempted and st.session_state.lyrics:
    st.markdown(
        f'<div class="lyrics-display">{st.session_state.lyrics}</div>',
        unsafe_allow_html=True
    )

    st.markdown("### 🔊 TURN IT UP")
    st.caption("Lyrics locked in. Now let the noise speak.")

    if st.button("🎸 GENERATE PUNK AUDIO"):
        audio_file = get_random_demo_audio()
        if audio_file:
            st.audio(str(audio_file))
        else:
            st.error("No demo audio files found in /audio.")

# Case 2: Gemini failed → fallback
elif st.session_state.generation_attempted and st.session_state.gemini_failed:
    st.error(
        "⚠️ The lyricist didn’t show up today.\n\n"
        "Gemini’s probably taking a smoke break.\n\n"
        "Till it crawls back, the amps are still hot."
    )

    if st.button("🔥 PLAY RANDOM PUNK NOISE"):
        audio_file = get_random_demo_audio()
        if audio_file:
            st.audio(str(audio_file))
        else:
            st.error("No demo audio files found in /audio.")
