import streamlit as st
import pandas as pd
import numpy as np

st.title("This is a title")
st.header("This is a header")
st.subheader("This is a subheader")
st.markdown("This is a *markdown,* :rainbow[this feature is so cool]")
st.text("This is text")
st.write("Hello World")
x = st.text_input("Favorite Movie?")
st.write(f"Your favorite movie is: {x}")

is_clicked = st.button("Click Me")

df = pd.DataFrame(
    np.random.randn(1000,2) / [50, 50] + [47.366669, 8.55],
    columns=["lat", "lon"],
)

st.title("This is a randomized scatterplot of the city of Zürich")
st.map(df)


on = st.toggle("Power Rangers Activate")

if on:
    st.write("Pwer Rangers activated!")


import streamlit as st


st.subheader("This is a numeric slider")
age = st.slider("How old are you?", 0, 130, 25)
st.write("I'm ", age, "years old")