import streamlit as st
from modules.data_layer import save_property
from modules.display_layer import get_all_properties
from modules.formatter import format_currency

st.title("Property Manager")

name = st.text_input("Property Name")
price = st.number_input("Price")

if st.button("Save Property"):
    save_property(name, price)
    st.success("Saved!")

st.divider()
st.subheader("Saved Properties")

# Show the list
for line in get_all_properties():
    name, price = line.split(",")
    st.write(f"{name}: {format_currency(price)}")