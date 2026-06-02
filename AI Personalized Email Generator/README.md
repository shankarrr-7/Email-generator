# 📧 AI Personalized Email Generator

An intelligent email generation tool powered by **Groq AI (Llama 3.3 70B)** and **Google Gemini**, built with **Streamlit**. Generate professional, personalized emails instantly with smart AI fallback, response caching, and multi-language translation support.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.58+-FF4B4B?logo=streamlit&logoColor=white)
![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?logo=meta&logoColor=white)
![Gemini](https://img.shields.io/badge/Google-Gemini_API-4285F4?logo=google&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🤖 **Multi-AI Provider** | Groq (primary) + Google Gemini (fallback) with automatic switching |
| ⚡ **Smart Rate Limit Handling** | Auto-fallback between 4 models if rate limited |
| 📦 **Response Caching** | Identical prompts served instantly from cache — zero wasted API calls |
| 🌐 **Multi-Language Translation** | Translate generated emails into 100+ languages |
| 🔊 **Text-to-Speech** | Read generated emails aloud |
| 📎 **File Attachments** | Attach PDFs, images, documents to emails |
| 📧 **Direct Email Sending** | Send emails directly via Gmail SMTP |
| 🎨 **Multiple Email Types** | Professional, Feedback, Sick Leave, Personal, Survey, Invitation & more |
| 🎭 **Tone Selection** | Formal, Friendly, Casual, Urgent, Convincing & more |

---

## 🏗️ Architecture

```
User Input → Streamlit UI → AI Provider Selection → Model Fallback Chain → Response Cache → Email Output
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              Groq Llama 3.3   Groq Llama 3.1   Gemini Flash
              (70B Versatile)  (8B Instant)     (Lite / 1.5)
```

### Model Fallback Chain

| Priority | Provider | Model | Free Tier Limit |
|----------|----------|-------|-----------------|
| 1️⃣ | **Groq** | Llama 3.3 70B Versatile | 30 req/min, 14,400/day |
| 2️⃣ | **Groq** | Llama 3.1 8B Instant | 30 req/min, 14,400/day |
| 3️⃣ | **Gemini** | 2.0 Flash Lite | 30 req/min |
| 4️⃣ | **Gemini** | 1.5 Flash | 15 req/min |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or higher
- A free **Groq API key** (recommended) → [Get one here](https://console.groq.com/keys)
- A free **Google Gemini API key** (optional) → [Get one here](https://aistudio.google.com/apikey)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/shankarrr-7/Email-generator.git
   cd Email-generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   .\venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure API keys**
   
   Create a `.env` file in the project root:
   ```env
   GROQ_API_KEY="gsk_your_groq_key_here"
   GOOGLE_API_KEY="your_gemini_key_here"
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Open in browser**
   ```
   http://localhost:8501
   ```

---

## 📁 Project Structure

```
AI Personalized Email Generator/
├── app.py              # Main Streamlit application
├── utils.py            # Utility functions (translation, TTS, email sending)
├── requirements.txt    # Python dependencies
├── .env                # API keys (not committed)
├── .gitignore          # Git ignore rules
└── README.md           # This file
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | Recommended | Free Groq API key for Llama models |
| `GOOGLE_API_KEY` | Optional | Google Gemini API key (fallback) |
| `EMAIL_PASSWORD` | Optional | Gmail app password for sending emails |

### Gmail SMTP Setup (for sending emails)

1. Enable 2-Factor Authentication on your Google account
2. Generate an [App Password](https://myaccount.google.com/apppasswords)
3. Add `EMAIL_PASSWORD="your_app_password"` to `.env`

---

## 🛠️ Tech Stack

- **Frontend**: [Streamlit](https://streamlit.io/) — Interactive web UI
- **AI (Primary)**: [Groq API](https://groq.com/) — Llama 3.3 70B on Groq LPU hardware
- **AI (Fallback)**: [Google Gemini](https://ai.google.dev/) — Gemini Flash models
- **Translation**: [googletrans](https://pypi.org/project/googletrans/) — 100+ languages
- **Text-to-Speech**: [pyttsx3](https://pypi.org/project/pyttsx3/) — Offline TTS engine
- **Email**: Python `smtplib` — Gmail SMTP integration

---

## 📝 Usage

1. **Select Email Type** — Professional, Feedback, Sick Leave, etc.
2. **Choose Tone** — Formal, Friendly, Casual, Urgent, etc.
3. **Fill in Details** — Subject, recipient, and describe what you want
4. **Generate** — AI creates a polished email instantly
5. **Preview & Edit** — Review the generated email
6. **Translate** — Convert to any language (optional)
7. **Send** — Deliver directly via Gmail SMTP

---

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the MIT License.

---

## 👤 Author

**Shankar Kongari**  
📧 shankar.k7993@gmail.com  
🔗 [GitHub](https://github.com/shankarrr-7)