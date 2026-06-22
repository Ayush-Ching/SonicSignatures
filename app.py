import sqlite3
from pathlib import Path

import streamlit as st

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
        "📊 Project Statistics",
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

        st.success(f"Loaded **{uploaded_file.name}**")

        st.info(
            "Recognition algorithm will be connected here."
        )

        if st.button("Recognize Song"):
            st.warning("Recognition not implemented yet.")


# ==========================================================
# Statistics
# ==========================================================

with tab3:

    st.subheader("Database Statistics")

    total_songs = len(songs)
    total_hashes = sum(hashes for _, hashes in songs)

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Songs", total_songs)

    with col2:
        st.metric("Fingerprint Hashes", f"{total_hashes:,}")

    st.divider()

    st.subheader("Library")

    st.dataframe(
        {
            "Song": [s for s, _ in songs],
            "Hashes": [h for _, h in songs],
        },
        use_container_width=True,
        hide_index=True,
    )