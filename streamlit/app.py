import streamlit as st

from statics import mitroiki_functs

st.title("Welcome to Your Project")
st.write("This is a Streamlit app served from a src/ layout!")


a = mitroiki_functs.K_without_axial(E=30000, I=2.0, L=4.0)

st.write("This is a test of the K_without_axial function from mitroiki_functs.")
st.write("E = 30000, I = 2.0, L = 4.0")

st.write("Result of K_without_axial function:", a)

