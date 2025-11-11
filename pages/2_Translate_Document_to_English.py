import streamlit as st
from openai import OpenAI
import os
import hmac
from pathlib import Path

from helper import read_docx, read_pdf, download_txt, download_docx, perplexity_check

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


st.title("Translate documents to English")
st.caption("Translate docs or PDFs into English")

client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

def auto_review(english_text: str, model="gpt-5-nano") -> str:
    prompt = f"""
        You are an expert English editor. The following text has already been translated.
        Check it for mistranslations, missing context, and awkward phrasing, then correct
        it. Return only the corrected text.

        **Translated text:**

        {english_text}
    """
    response = client.chat.completions.create(
        model=model,
        messages=[{
                "role": "user",
                "content": prompt
                }],
        temperature=0.2,
        max_tokens=4000,
    )
    return response.choices[0].message.content.strip()

def translate_document(raw_text: str, model="gpt-4o-mini") -> str:
    """Request OpenAI ChatGPT to translate a document.
  
    Args: 
        raw_text: Message to send to ChatGPT for translation.
        model: The model to be used..
    """
    prompt = f"""You are an expert translator and language model.  
Your task is to translate the entire document below from its original language into clear, natural English.  
The document may contain headings, bullet points, tables, and a mix of formal and informal tone.  
Please preserve the original structure and formatting as much as possible (use Markdown if needed).  
If you encounter ambiguous terms or cultural references, provide a brief note in brackets.

**Input Document:**

[START OF DOCUMENT]
{raw_text}
[END OF DOCUMENT]

**Output Format:**

1. Translate the whole text into English.  
2. Keep headings, lists, and tables exactly as in the source (convert tables to Markdown).  
3. If you need to clarify a phrase, add a short note in brackets right after the sentence.  
4. Do NOT add any explanatory text outside the translated content.  
5. Do NOT alter numbers or proper nouns unless they are obviously incorrect in English.

**Now translate the document above.**
"""
    response = client.chat.completions.create(
        model=model,
        messages=[{
                "role": "user",
                "content": prompt
                }],
        temperature=0.2,
        max_tokens=4000,
    )
    return response.choices[0].message.content.strip()

# file upload
uploaded_file = st.file_uploader("Upload a file to translate", type=["docx", "pdf"])

raw_text = None
if uploaded_file is not None:
    file_type = Path(uploaded_file.name).suffix.lower()
    if file_type == ".docx":
        raw_text = read_docx(uploaded_file)
    elif file_type == ".pdf":
        raw_text = read_pdf(uploaded_file)

    st.success(f"Extracted {len(raw_text.split()):,} words from the file.")

# translate
if raw_text:
    with st.spinner("Translating..."):
        translated = translate_document(raw_text)

    st.subheader("Initial Translation")
    st.write(translated)

    # auto-review
    with st.spinner("Auto-reviewing..."):
        reviewed = auto_review(translated)

    st.subheader("After auto-review")
    st.write(reviewed)

    # external sanity check
    perplexity_score = perplexity_check(reviewed)
    st.info(f"Perplexity estimate: {perplexity_score:.1f}")
    if perplexity_score > 1500:
        st.warning("Perplexity score is high. Please double-check the translation manually.")

    # user confirmation
    st.subheader("Side-by-side comparison")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Original**")
        st.write(raw_text[:1500] + ("..." if len(raw_text) > 1500 else ""))
    with col2:
        st.markdown("**Translated**")
        st.write(reviewed[:1500] + ("..." if len(reviewed) > 1500 else ""))

    st.markdown("""
        You can **edit** the translated text directly below if you spot an error.
        Once satisfied, click one of the download buttons.
    """)

    edited_text = st.text_area("Edit translation (optional)", value=reviewed, height=300)

    # Download buttons
    download_txt(edited_text, filename=f"{uploaded_file.name}_translated.txt")
    download_docx(edited_text, filename=f"{uploaded_file.name}_translated.docx")

