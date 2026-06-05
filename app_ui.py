import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Enterprise Knowledge Platform", layout="wide")

def main():
    st.title("Enterprise Knowledge Platform")
    st.subheader("Interactive Query Interface & Graph Trace Viewer")
    
    # TODO: Implement Streamlit UI components and Graph execution trace viewer
    st.info("Starter UI template loaded.")

if __name__ == "__main__":
    main()
