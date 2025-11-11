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

def gpt_msg(message_in, prompt='Translate this sentence into English'):
  """
  message_in = message_in or 'this is a test message'
  prompt = prompt or 'translate this sentence into German'
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
      model="gpt-4-turbo-preview",
  )
  return out.choices[0].message.content

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {"role": "assistant", "content": "Please enter text here to translate it into English"}
    ]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input(placeholder="enter your text"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    response = gpt_msg(message_in=prompt)
    st.session_state.messages.append({"role": "assistant", "content": response})
    st.chat_message("assistant").write(response)

    #llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=os.environ.get("OPENAI_API_KEY"), streaming=True)
    #search = DuckDuckGoSearchRun(name="Search")
    #search_agent = initialize_agent(
    #    [search], llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION, handle_parsing_errors=True
    #)
    #with st.chat_message("assistant"):
    #    st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
    #    response = search_agent.run(st.session_state.messages, callbacks=[st_cb])
    #    st.session_state.messages.append({"role": "assistant", "content": response})
    #    st.write(response)
