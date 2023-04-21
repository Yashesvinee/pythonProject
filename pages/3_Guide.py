import streamlit as st

def main_loop():

    st.title("Guide to Posture Risk Assessment")
    st.subheader("Learn about how your Posture Risk Assessment is done.")
    st.subheader("REBA - Rapid Entire Body Assessment")
    st.text("It helps evaluate standing postures.")
    st.text("Here is the table used to determine the risk score")
    st.image("images/reba sheet.png")
    st.text("Match your score to this table to find the risk level.")
    col1, col2, col3 = st.columns([2, 6, 1])

    with col1:
        st.write("")

    with col2:
        st.image("images/reba score.png")

    with col3:
        st.write("")

    st.subheader("RULA - Rapid Upper Limb Assessment")
    st.text("It helps evaluate sitting postures.")
    st.text("Here is the table used to determine the risk score")
    st.image("images/RULA sheet.png",width=1100)
    st.text("Match your score to this table to find the risk level.")
    col1, col2, col3 = st.columns([2, 6, 1])

    with col1:
        st.write("")

    with col2:
        st.image("images/rula score.png")

    with col3:
        st.write("")



if __name__ == '__main__':
    main_loop()