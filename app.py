import sqlite3
from pathlib import Path
import streamlit as st
import pandas as pd
import tempfile
import os

from match_song import find_song

DATABASE = "database/fingerprints.db"
IMAGE_DIR = Path("fingerprint_images")


st.set_page_config(
    page_title="Sonic Signatures",
    page_icon="🎵",
    layout="wide",
)

st.title("🎵 Sonic Signatures")
st.caption("EE200 : Signals, Systems and Networks Project")


@st.cache_data
def load_library():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            s.name,
            COUNT(f.hash)
        FROM songs s
        LEFT JOIN fingerprints f
            ON s.id = f.song_id
        GROUP BY s.id
        ORDER BY s.name
    """)

    songs = cursor.fetchall()

    conn.close()

    return songs


songs = load_library()

tab1, tab2, tab3 = st.tabs(
    [
        "📚 Library",
        "🔍 Song Recognition",
        "📊 Batch Upload",
    ]
)


# ==========================================================
# Library
# ==========================================================

with tab1:

    st.subheader("Song Library")

    cols = st.columns(4)

    for i, (name, hashes) in enumerate(songs):

        image_path = IMAGE_DIR / f"{name}.png"

        with cols[i % 4]:

            if image_path.exists():
                st.image(
                    str(image_path),
                    use_container_width=True,
                )
            else:
                st.image(
                    "https://placehold.co/600x400?text=No+Image",
                    use_container_width=True,
                )

            st.markdown(f"**{name}**")
            st.caption(f"{hashes:,} hashes")


# ==========================================================
# Song Recognition
# ==========================================================

with tab2:

    st.subheader("Recognize a Song")

    uploaded_file = st.file_uploader(
        "Upload an audio clip",
        type=["mp3", "wav", "flac", "ogg", "m4a"],
    )

    if uploaded_file is not None:

        st.audio(uploaded_file)

        if st.button("Try", type="primary"):

            suffix = Path(uploaded_file.name).suffix

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=suffix,
            ) as tmp:

                tmp.write(uploaded_file.read())
                temp_path = tmp.name

            with st.spinner("Searching database..."):

                result = find_song(temp_path)

            os.remove(temp_path)

            if result is None:

                st.error("No matching song found.")

            else:

                st.success("Match Found!")

                col1, col2 = st.columns([1, 2])

                with col1:

                    image_path = IMAGE_DIR / f"{result['song']}.png"

                    if image_path.exists():
                        st.image(
                            str(image_path),
                            use_container_width=True,
                        )

                with col2:

                    st.markdown(f"### 🎵 {result['song']}")

                    st.metric(
                        "Votes",
                        result["votes"],
                    )

                    st.metric(
                        "Time Offset",
                        f"{result['offset']:.2f} s",
                    )

# ==========================================================
# Batch Recognition
# ==========================================================

with tab3:

    st.subheader("Batch Song Recognition")

    uploaded_files = st.file_uploader(
        "Upload multiple audio clips",
        type=["mp3", "wav", "flac", "ogg", "m4a"],
        accept_multiple_files=True,
    )

    if uploaded_files:

        st.success(f"{len(uploaded_files)} file(s) selected.")

        if st.button("Try Batch", type="primary"):

            results = []

            progress = st.progress(0.0)

            for i, uploaded_file in enumerate(uploaded_files):

                suffix = Path(uploaded_file.name).suffix

                with tempfile.NamedTemporaryFile(
                    delete=False,
                    suffix=suffix,
                ) as tmp:

                    tmp.write(uploaded_file.read())
                    temp_path = tmp.name

                result = find_song(temp_path)

                os.remove(temp_path)

                if result is None:

                    results.append({
                        "Query": uploaded_file.name,
                        "Matched Song": "No Match",
                        "Votes": "-",
                        "Offset (s)": "-",
                    })

                else:

                    results.append({
                        "Query": uploaded_file.name,
                        "Matched Song": result["song"],
                        "Votes": result["votes"],
                        "Offset (s)": f"{result['offset']:.2f}",
                    })

                progress.progress((i + 1) / len(uploaded_files))

            st.success("Batch recognition complete.")

            st.dataframe(
                pd.DataFrame(results),
                use_container_width=True,
                hide_index=True,
            )