import streamlit as st
import math
import time

st.set_page_config(layout="wide")

st.markdown("""
<style>
body, .stApp {
    background: black;
}
pre {
    color: #00ff99;
    font-family: Consolas, monospace;
    font-size: 12px;
    line-height: 11px;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

frame = st.empty()

chars = " .:-=+*#%@"

while True:
    output = "So jao bhai.<br>"

    t = time.time() * 2

    for y in range(169):
        for x in range(169):
            v = (
                math.sin(x * 0.15 + t)
                + math.cos(y * 0.18 + t * 1.3)
                + math.sin((x + y) * 0.08 + t * 0.7)
            )

            idx = int((v + 3) / 6 * (len(chars) - 1))
            output += chars[idx]

        output += "\n"
    
    output += "<br>So ja ladle."

    frame.markdown(f"<pre>{output}</pre>", unsafe_allow_html=True)
    time.sleep(0.03)