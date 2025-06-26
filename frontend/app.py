import streamlit as st
import requests

st.set_page_config(page_title="HR Assistant Chatbot", layout="centered")
st.title("🤖 HR Assistant Chatbot")

API_URL = "http://localhost:8000/chat"

if 'history' not in st.session_state:
    st.session_state['history'] = []

with st.form("chat_form"):
    user_query = st.text_input("Ask about employees, skills, or projects:", "")
    submitted = st.form_submit_button("Send")

if submitted and user_query:
    resp = requests.post(API_URL, json={"query": user_query})
    if resp.status_code == 200:
        data = resp.json()
        st.session_state['history'].append((user_query, data['response'], data['employees']))
    else:
        st.error("Error from backend.")

for user_q, bot_r, employees in reversed(st.session_state['history']):
    st.markdown(f"**You:** {user_q}")
    st.markdown(f"**Bot:**")
    st.markdown(bot_r)
    st.markdown("---")

st.markdown("""
    <style>
    body {
        background-color: #b3ccff !important;
    }
    .stApp {
        background-color: #b3ccff;
    }
    </style>
""", unsafe_allow_html=True) 