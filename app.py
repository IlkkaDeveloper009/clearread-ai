import streamlit as st
from google import genai
from pydantic import BaseModel
from pypdf import PdfReader
from gtts import gTTS
import io

# 1. Page configuration
st.set_page_config(page_title="ClearRead AI", page_icon="📖", layout="centered")

# 2. Structured output schema for AI
class StudyCard(BaseModel):
    title: str
    simple_text: str

class QuizQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str

class AdaptedMaterial(BaseModel):
    tldr: str
    cards: list[StudyCard]
    difficult_words: list[str]
    quiz: list[QuizQuestion]

# 3. Sidebar: Settings & Accessibility
with st.sidebar:
    st.header("⚙️ Settings")
    user_api_key = st.text_input("Custom Gemini API Key (Optional):", type="password")
    api_key = user_api_key if user_api_key else st.secrets.get("GEMINI_API_KEY", "")
    
    st.divider()
    st.subheader("👁️ Accessibility Modes")
    dyslexia_mode = st.toggle("Dyslexia-Friendly Mode (Warm background + Larger font)")
    bionic_mode = st.toggle("Bionic Reading (Bold word beginnings for focus)")

# Apply custom CSS for Dyslexia-Friendly Mode
if dyslexia_mode:
    st.markdown("""
        <style>
        .stApp { background-color: #FAF3E0; color: #2C2C2C; }
        p, li, div { font-size: 19px !important; line-height: 1.7 !important; letter-spacing: 0.5px; }
        </style>
    """, unsafe_allow_html=True)

# Helper function for Bionic Reading
def to_bionic(text):
    words = text.split()
    bionic_words = []
    for w in words:
        mid = max(1, len(w) // 2)
        bionic_words.append(f"**{w[:mid]}**{w[mid:]}")
    return " ".join(bionic_words)

# Sample text for quick demo
SAMPLE_TEXT = (
    "Photosynthesis is a biological process used by many cellular organisms to convert light energy "
    "into chemical energy, which is stored in organic compounds that can later be metabolized through "
    "cellular respiration to fuel the organism's activities. Usually, this process involves oxygenic "
    "photosynthesis, where water is oxidized to release oxygen gas, and carbon dioxide is reduced to "
    "synthesize carbohydrates such as glucose. These reactions occur within specialized organelles called "
    "chloroplasts, utilizing chlorophyll pigments to absorb photons and initiate an electron transport "
    "chain that generates ATP and NADPH."
)

# 4. Main interface
st.title("📖 ClearRead AI")
st.write("An inclusive AI reading assistant helping students with ADHD and dyslexia break down complex study materials.")

# Input tabs: Paste Text or Upload PDF
tab1, tab2 = st.tabs(["✍️ Paste Text", "📄 Upload PDF"])

if "input_text" not in st.session_state:
    st.session_state["input_text"] = ""

with tab1:
    if st.button("📋 Load Sample Biology Text"):
        st.session_state["input_text"] = SAMPLE_TEXT
    user_text = st.text_area(
        "Paste a complex textbook paragraph or article:",
        value=st.session_state["input_text"],
        height=180,
        placeholder="Paste any dense educational text here..."
    )

with tab2:
    uploaded_file = st.file_uploader("Upload a study PDF (first 3 pages will be extracted):", type=["pdf"])
    pdf_text = ""
    if uploaded_file is not None:
        try:
            reader = PdfReader(uploaded_file)
            pages_to_read = min(len(reader.pages), 3)
            for i in range(pages_to_read):
                pdf_text += reader.pages[i].extract_text() + "\n"
            st.info(f"Extracted {len(pdf_text)} characters from {pages_to_read} page(s).")
        except Exception as e:
            st.error(f"Could not read PDF: {e}")

# Determine which text to process
final_text = pdf_text.strip() if pdf_text.strip() else user_text.strip()

if st.button("✨ Simplify & Adapt Text", type="primary"):
    if not api_key:
        st.error("Please enter your Gemini API Key in the sidebar on the left!")
    elif not final_text:
        st.warning("Please paste some text or upload a PDF first.")
    else:
        with st.spinner("AI is structuring your accessible study guide..."):
            try:
                client = genai.Client(api_key=api_key)
                prompt = f"""
                You are an expert in inclusive education. Adapt the following educational text for a student 
                who struggles with focus (ADHD) or dense reading (dyslexia). Respond in the same language as the input text.
                1. Write a clear summary in 1-2 simple sentences (tldr).
                2. Break the material down into 3-4 short, bite-sized study cards with clear headings.
                3. Extract up to 4 difficult terms from the text and explain them in plain language (format: 'Term — simple explanation').
                4. Create 2 multiple-choice quiz questions (with 3 options each) for quick self-check.
                
                Text: {final_text[:8000]}
                """
                
                models_to_try = ["gemini-3.8-flash", "gemini-3.6-flash", "gemini-3.5-flash-lite"]
                response = None
                for model_name in models_to_try:
                    try:
                        response = client.models.generate_content(
                            model=model_name,
                            contents=prompt,
                            config={
                                "response_mime_type": "application/json",
                                "response_schema": AdaptedMaterial,
                            },
                        )
                        break
                    except Exception as model_err:
                        err_msg = str(model_err)
                        if ("503" in err_msg or "404" in err_msg) and model_name != models_to_try[-1]:
                            continue
                        raise model_err
                
                st.session_state["result"] = AdaptedMaterial.model_validate_json(response.text)
                st.session_state.pop("audio_bytes", None)
                
            except Exception as e:
                st.error(f"An error occurred: {e}")

# 5. Display results
if "result" in st.session_state:
    res = st.session_state["result"]
    
    st.success(f"**TL;DR (Main Idea):** {res.tldr}")
    
    # Audio Read-Aloud Feature
    if st.button("🔊 Listen to Summary & Cards"):
        with st.spinner("Generating audio..."):
            full_speech = f"Main Idea: {res.tldr}. " + " ".join(
                [f"Card {i}: {c.title}. {c.simple_text}" for i, c in enumerate(res.cards, 1)]
            )
            tts = gTTS(text=full_speech, lang="en")
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            st.session_state["audio_bytes"] = audio_fp.getvalue()
            
    if "audio_bytes" in st.session_state:
        st.audio(st.session_state["audio_bytes"], format="audio/mp3")
    
    st.subheader("🗂️ Bite-Sized Study Cards")
    for i, card in enumerate(res.cards, 1):
        with st.container(border=True):
            st.markdown(f"#### {i}. {card.title}")
            content = to_bionic(card.simple_text) if bionic_mode else card.simple_text
            st.markdown(content)
            
    st.subheader("📚 Key Vocabulary")
    for word in res.difficult_words:
        st.markdown(f"- {word}")
        
    st.subheader("🧠 Quick Self-Check")
    for idx, q in enumerate(res.quiz):
        st.markdown(f"**Question {idx+1}:** {q.question}")
        choice = st.radio("Choose an answer:", q.options, key=f"q_{idx}", index=None)
        if choice:
            if choice == q.correct_answer:
                st.success("Correct! 🎉")
            else:
                st.error(f"Not quite. The correct answer is: {q.correct_answer}")
