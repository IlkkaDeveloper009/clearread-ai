# 📖 ClearRead AI

**An inclusive AI-powered reading assistant designed to help students with ADHD and dyslexia break down complex study materials.**

Built for the **STEM2Connect AI Hackathon 2026** (Track: **Education**).

---

## 💡 The Problem
Dense textbook paragraphs, academic articles, and long PDF study guides create significant cognitive overload for neurodivergent learners—especially students with **ADHD** (who struggle to maintain visual focus on long blocks of text) and **dyslexia** (who experience visual crowding and fatigue on bright white screens).

## ✨ What ClearRead AI Does
ClearRead AI transforms overwhelming educational texts or PDF documents into an accessible, structured study guide in seconds:
* **TL;DR Summary:** Captures the core idea in 1–2 plain sentences.
* **Bite-Sized Study Cards:** Breaks dense text into 3–4 short, digestible cards with clear headings.
* **Key Vocabulary:** Extracts difficult academic terms and explains them in everyday language.
* **Quick Self-Check:** Generates an interactive multiple-choice mini-quiz for active recall.
* **Dyslexia-Friendly Mode:** Switches the interface to a warm, low-glare cream background (`#FAF3E0`) with increased font size and line spacing.
* **Bionic Reading Mode:** Bolds the initial letters of words to guide the eyes and prevent line-skipping.
* **Audio Read-Aloud (TTS):** Converts the summary and study cards into speech for auditory learners.
* **PDF Support:** Extracts text directly from uploaded PDF study guides.

---

## 🛠️ Tech Stack & APIs Used
* **Frontend & Web Framework:** Python, [Streamlit](https://streamlit.io)
* **AI Model:** [Google Gemini API](https://google.dev) (`gemini-3.8-flash` with automatic fallback to `gemini-3.6-flash` / `gemini-3.5-flash-lite`) using Pydantic structured outputs
* **PDF Parsing:** `pypdf`
* **Text-to-Speech:** `gTTS` (Google Text-to-Speech)

---

## 🚀 How to Run Locally

1. **Clone this repository:**
   ```bash
   git clone https://github.com
   cd clearread-ai
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run app.py
   ```

4. **Add your API Key:**
   Get a free API key from [Google AI Studio](https://google.com), paste it into the left sidebar of the app, and start adapting texts!

---

## 🤖 AI Disclosure & Attribution
In accordance with the STEM2Connect AI Hackathon 2026 rules:
* **In-App AI:** The application uses the Google Gemini API to summarize, simplify, structure study cards, and generate comprehension quizzes.
* **Development Assistance:** An AI coding assistant was used during development to help structure the Streamlit UI layout, implement Pydantic JSON schema validation, and debug API fallback handling. All features, accessibility modes, prompts, and user flows were designed, tested, and verified by the author.
