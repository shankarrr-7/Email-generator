import streamlit as st
import os
import time
import hashlib
from dotenv import load_dotenv
import utils
from streamlit_option_menu import option_menu
from pathlib import Path
import requests
import json

# --- Load environment variables ---
load_dotenv()

# --- Configure API Clients ---
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Gemini client if key exists
gemini_client = None
if GOOGLE_API_KEY:
    import google.genai as genai
    gemini_client = genai.Client(api_key=GOOGLE_API_KEY)

# --- Response Cache to prevent duplicate API calls ---
@st.cache_data(ttl=300, show_spinner=False)
def cached_generate_email(prompt_hash, prompt_text, provider, model):
    """Cache email generation results so Streamlit reruns don't waste API calls."""
    if provider == "groq":
        return _call_groq_api(prompt_text, model)
    else:
        return _call_gemini_api(prompt_text, model)


def _call_groq_api(prompt, model):
    """Call Groq API (free, fast, generous limits)."""
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a professional email writer. Write clear, well-structured emails based on the user's requirements."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "top_p": 0.95,
        "max_tokens": 2048,
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _call_gemini_api(prompt, model):
    """Call Google Gemini API."""
    if not gemini_client:
        raise Exception("Gemini API key not configured")
    response = gemini_client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "temperature": 0.7,
            "top_p": 0.95,
        }
    )
    return response.text


# --- Client-side rate limiter ---
def check_rate_limit():
    """Prevent more than 1 request per 5 seconds from the UI."""
    now = time.time()
    last_request = st.session_state.get("_last_api_request", 0)
    if now - last_request < 5:
        wait_time = int(5 - (now - last_request))
        return False, wait_time
    return True, 0


def mark_request():
    """Mark that an API request was just made."""
    st.session_state["_last_api_request"] = time.time()


# --- Streamlit UI ---
def main():
    # Sidebar for Navigation
    with st.sidebar:
        selected = option_menu(
            "Email Generator",
            ["Compose Email", "Email Preview", "Settings"],
            icons=["pencil-fill", "eye-fill", "gear-fill"],
            menu_icon="envelope-fill",
            default_index=0,
        )
    if selected == "Compose Email":
        compose_email_page()
    elif selected == "Email Preview":
        email_preview_page()
    elif selected == "Settings":
        settings_page()


# --- Page Functions ---
def compose_email_page():
    st.title("📧 Compose New Email")

    # --- Show API status ---
    if GROQ_API_KEY:
        st.success("✨ Using Groq API (FREE & Fast!) — Llama 3 powered")
        st.info(
            "**Groq Free API Features:**\n\n"
            "✅ **Primary Model**: Llama 3.3 70B (high quality)\n"
            "✅ **Fallback Model**: Llama 3.1 8B (ultra fast)\n"
            "✅ **Free tier**: 30 requests/min, 14,400 req/day\n"
            "✅ **No credit card required**\n"
            "✅ **Lightning fast**: Groq's LPU hardware\n"
            "✅ **Smart caching**: Duplicate prompts served instantly\n\n"
            "**Your API Status**: ✅ Groq Connected"
        )
    elif GOOGLE_API_KEY:
        st.success("✨ Using Google Gemini Free API")
        st.info(
            "**Tip**: For better rate limits, add a free Groq API key!\n"
            "Get one at: https://console.groq.com/keys\n\n"
            "**Your API Status**: ✅ Gemini Connected"
        )
    else:
        st.error(
            "❌ No API key found!\n\n"
            "Add one of these to your `.env` file:\n"
            "- `GROQ_API_KEY=your_key` (recommended, get free at https://console.groq.com/keys)\n"
            "- `GOOGLE_API_KEY=your_key`"
        )
        return

    # --- User Input Form ---
    sender_email = st.text_input("Your Email Address")
    receiver_name = st.text_input("Recipient's Name")
    receiver_email = st.text_input("Recipient's Email Address")

    email_types = [
        "Professional", "Feedback", "Sick Leave", "Personal", "Survey",
        "Confirmation", "Invitation", "Other"
    ]
    email_type = st.selectbox("Email Type", email_types)

    if email_type == "Other":
        email_type = st.text_input("Enter Email Type")

    tones = [
        "Formal", "Friendly", "Encouraging", "Neutral", "Professional",
        "Casual", "Optimistic", "Convincing", "Urgent", "Appreciative"
    ]
    tone = st.selectbox("Email Tone", tones)

    email_subject = st.text_input("Email Subject")
    email_body_prompt = st.text_area("Describe the email content you want to generate:", height=150)

    # --- File Upload Section ---
    uploaded_files = st.file_uploader("Attach files (optional)", type=["pdf", "docx", "txt", "jpg", "png", "mp4"], accept_multiple_files=True)

    # --- Generate Email Button ---
    if st.button("Generate Email"):
        if not all([sender_email, receiver_email, email_type, tone, email_body_prompt, email_subject]):
            st.warning("Please fill in all required fields.")
            return

        # --- Client-side rate limit check ---
        can_proceed, wait_time = check_rate_limit()
        if not can_proceed:
            st.warning(f"⏳ Please wait {wait_time} more seconds before generating again...")
            return

        # --- Construct Prompt ---
        prompt = f"""Write an email with the following specifications:
Type: {email_type}
Tone: {tone}
Subject: {email_subject}
Recipient Name: {receiver_name}
Sender: {sender_email}
Main Content/Purpose: {email_body_prompt}"""

        # --- Create a hash for caching ---
        prompt_hash = hashlib.md5(prompt.encode()).hexdigest()

        attachment_paths = []

        # --- Determine which providers/models to try ---
        attempts = []
        if GROQ_API_KEY:
            attempts.append(("groq", "llama-3.3-70b-versatile"))
            attempts.append(("groq", "llama-3.1-8b-instant"))
        if GOOGLE_API_KEY:
            attempts.append(("gemini", "gemini-2.0-flash-lite"))
            attempts.append(("gemini", "gemini-1.5-flash"))

        if not attempts:
            st.error("❌ No API keys configured!")
            return

        # --- Try each provider/model ---
        email_content = None
        for i, (provider, model) in enumerate(attempts):
            try:
                st.info(f"⏳ Generating email using **{provider.upper()} / {model}**...")
                mark_request()
                email_content = cached_generate_email(prompt_hash, prompt, provider, model)
                break  # Success!

            except Exception as model_error:
                error_str = str(model_error)
                is_rate_limit = any(kw in error_str.lower() for kw in [
                    "429", "quota", "rate", "resource_exhausted", "rate_limit", "too many"
                ])

                if is_rate_limit and i < len(attempts) - 1:
                    next_provider, next_model = attempts[i + 1]
                    st.warning(f"⚠️ Rate limit on {provider}/{model}. Switching to {next_provider}/{next_model}...")
                    time.sleep(2)
                    continue
                elif i == len(attempts) - 1:
                    # Last attempt failed
                    st.error(
                        f"❌ **All API providers exhausted**\n\n"
                        f"Last error: {error_str}\n\n"
                        f"**Solutions:**\n"
                        f"- Wait 1-2 minutes and try again\n"
                        f"- Get a free Groq API key at https://console.groq.com/keys\n"
                        f"- Check your API keys in the .env file"
                    )
                    return
                else:
                    st.error(f"❌ Error with {provider}/{model}: {error_str}")
                    if i < len(attempts) - 1:
                        continue
                    return

        if email_content:
            st.session_state.generated_email = email_content
            st.session_state.attachment_paths = attachment_paths
            st.session_state.sender_email = sender_email
            st.session_state.receiver_email = receiver_email
            st.success("✅ Email generated successfully! Go to the 'Email Preview' tab.")


# Email preview and operations
def email_preview_page():
    st.title("Email Preview")
    if "generated_email" in st.session_state:
        # --- Email Display ---
        st.subheader("Generated Email:")
        st.write(st.session_state.generated_email)

        # --- Read Aloud ---
        if st.button("Read Aloud"):
            utils.text_to_speech(st.session_state.generated_email)

        # --- Translation ---
        target_language = st.selectbox("Translate to:", ["", "Spanish", "French", "German", "Chinese", "Japanese","Telugu","Hindi"] + sorted(utils.get_supported_languages()))
        if target_language:
            translated_text = utils.translate_text(st.session_state.generated_email, target_language)
            st.subheader(f"Translated Email ({target_language}):")
            st.write(translated_text)

        # --- Send Email ---
        if st.button("Send Email"):
            if "sender_email" not in st.session_state or "receiver_email" not in st.session_state:
                st.error("Sender or receiver email not found. Please generate the email again.")
                return
            with st.spinner("Sending email..."):
                try:
                    if "attachment_paths" in st.session_state:
                        result = utils.send_email(
                            st.session_state.sender_email,
                            st.session_state.receiver_email,
                            "Generated Email Subject",
                            st.session_state.generated_email,
                            st.session_state.attachment_paths
                        )
                    else:
                        result = utils.send_email(
                            st.session_state.sender_email,
                            st.session_state.receiver_email,
                            "Generated Email Subject",
                            st.session_state.generated_email,
                        )

                    if result:
                        st.success("Email sent successfully!")
                    else:
                        st.error("Failed to send email.")
                except Exception as e:
                    st.error(f"An error occurred while sending: {e}")
    else:
        st.info("Please generate an email first.")


# Email settings
def settings_page():
    st.title("⚙️ Settings")

    st.subheader("API Configuration")

    # Show current API status
    st.write("**Current API Keys:**")
    if GROQ_API_KEY:
        st.success(f"✅ Groq API: Connected (key: ...{GROQ_API_KEY[-6:]})")
    else:
        st.warning("❌ Groq API: Not configured")
        st.markdown(
            "**Get a free Groq API key:**\n"
            "1. Go to [console.groq.com/keys](https://console.groq.com/keys)\n"
            "2. Sign up (free, no credit card)\n"
            "3. Create an API key\n"
            "4. Add `GROQ_API_KEY=your_key_here` to your `.env` file\n"
            "5. Restart the app"
        )

    if GOOGLE_API_KEY:
        st.success(f"✅ Gemini API: Connected (key: ...{GOOGLE_API_KEY[-6:]})")
    else:
        st.info("ℹ️ Gemini API: Not configured (optional if Groq is set)")

    st.divider()

    st.subheader("Rate Limit Info")
    st.markdown(
        "| Provider | Model | Free Tier Limit |\n"
        "|----------|-------|----------------|\n"
        "| **Groq** | Llama 3.3 70B | 30 req/min, 14,400/day |\n"
        "| **Groq** | Llama 3.1 8B | 30 req/min, 14,400/day |\n"
        "| **Gemini** | 2.0 Flash Lite | 30 req/min |\n"
        "| **Gemini** | 1.5 Flash | 15 req/min |"
    )

    # Clear cache button
    st.divider()
    if st.button("🗑️ Clear Response Cache"):
        cached_generate_email.clear()
        st.success("Cache cleared!")


if __name__ == "__main__":
    main()