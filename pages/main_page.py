import streamlit as st


if st.button("Stream data"):
    st.write_stream(stream_data)


st.markdown("# Main page 🎈")
st.sidebar.markdown("# Main page 🎈")
st.title("Trat Provincial Health Data v.1")
st.image('images/kk.jpeg', caption='Trat sea')
st.write_stream(stream_data)