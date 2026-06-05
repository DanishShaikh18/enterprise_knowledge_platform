# Streamlit application UI
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Enterprise Knowledge Platform", layout="wide")

def main():
    st.title("Enterprise Knowledge Platform UI")
    # TODO: Integrate LangGraph execution tracing and query submission

if __name__ == "__main__":
    main()
