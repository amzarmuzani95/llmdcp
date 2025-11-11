import streamlit as st
from openai import OpenAI
import os
import hmac



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
    
    


st.title("Translate text to English")


client = OpenAI(
    api_key=st.secrets["OPENAI_API_KEY"],
)

def gpt_msg(message_in, prompt='Translate this document into English'):
  """Call to OpenAI ChatGPT.
  
  Args: 
    message_in: Message to send to ChatGPT.
    prompt: The system prompt for ChatGPT.
  # """
  out = client.chat.completions.create(
      messages=[
          {
              "role": "system",
              "content": prompt,
          },
          {
              "role": "user",
              "content": message_in,
          }
      ],
      model="gpt-4o-mini",
  )
  return out.choices[0].message.content

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Please upload a file to translate it into English"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# file upload and translation
uploaded_file = st.file_uploader("Upload a file to translate", type=["doc", "pdf"])
if uploaded_file is not None:
    # Read the contents of the uploaded file
    with open(uploaded_file, "r") as f:
        text = f.read()

    # translate the text
    response = gpt_msg(text)

    # Show the translated text in a new chat message
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

