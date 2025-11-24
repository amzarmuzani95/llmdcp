import streamlit as st
from openai import OpenAI
import hmac
from pathlib import Path

from helper import read_docx, read_pdf_chunks, download_txt, download_docx, perplexity_check, file_hash, split_into_token_chunks

# --- Config ---
ALLOWED_TONES = [
    "formal",
    "professorial",
    "polite",
    "casual",
    "festive",
]

def check_password():
    """Returns `True` if the user had the correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False

    # Return True if the password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show input for password.
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password():
    st.stop()  # Do not continue if check_password is not True.

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def write_email(input_text: str, tone: str, model="gpt-4o-mini") -> str:
    """Request OpenAI ChatGPT to write an email, based on the info & tone.
  
    Args: 
        input_text: Info to include in the email.
        tone: Tone of the email.
        model: The model to be used.
    """
    prompt = f"""Write an email in German using the following information '{input_text}'. " \
    "The tone of the email should be '{tone}'."""

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": prompt}],
        temperature=0.2,
        max_tokens=4000,
    )
    return str(response.choices[0].message.content).strip()

# --- UI ---

st.title("Write an email in German!")
st.write("Choose a tone, add some information, and get email-ready text!")
st.caption("NOTE: Please do NOT share any sensitive information as OpenAI servers are still stored in the US (not under GDPR)") 

input_text = st.text_area(
    label="What do you want the email to say?",
    height=150,
)

# choose tone
tone = st.selectbox(
    label="Choose the email tone",
    options = ALLOWED_TONES,
)

if st.button("Generate Email"):
    # initial validatition 
    if not input_text.strip():
        st.error("Input text cannot be empty.")
    elif tone not in ALLOWED_TONES:
        st.error("Invalid tone selected.")
    else:
        
        try:
            # send to API for response
            email_text = write_email(input_text, tone)

            # display the text
            st.subheader("Generated Email:")
            st.text_area(
                label="You can edit the text below or copy and paste it",
                value=email_text,
                height=300,
            )
        except Exception as e:
            st.error(f"API error: {str(e)}")
