
import io
import os
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

import streamlit as st
from PIL import Image

from masking import pil_open, make_edit_mask, mask_preview, to_png_bytes, to_jpeg_bytes
from editing import edit_image_bytes

st.set_page_config(page_title="Parkwood Photo Processor", page_icon="🚗", layout="wide")

st.title("🚗 Parkwood Photo Processor")
st.caption("Batch forecourt cleanup for dealership stock photos — conservative, realistic, car-first.")

with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("OpenAI API key", type="password", value=os.getenv("OPENAI_API_KEY", ""))
    floor_start = st.slider("Floor starts at (% of image height)", 52, 78, 64, 1)
    concurrency = st.slider("Concurrent edits", 1, 5, 2, 1)
    st.markdown("---")
    st.markdown("**Use case:** upload 8–20 exterior photos for one car.")
    st.markdown("**Red preview area = editable floor.**")
    st.markdown("Always do a final quick QA check before listing.")

uploaded = st.file_uploader(
    "Upload exterior stock photos",
    type=["jpg", "jpeg", "png", "webp"],
    accept_multiple_files=True
)

if uploaded:
    st.success(f"{len(uploaded)} photo(s) uploaded.")
    preview = st.checkbox("Show mask previews", value=True)

    originals = []
    masks = []
    previews = []
    filenames = []

    for file in uploaded:
        try:
            img = pil_open(file)
            mask = make_edit_mask(img, floor_start_ratio=floor_start / 100.0)
            prev = mask_preview(img, mask)
            originals.append(img)
            masks.append(mask)
            previews.append(prev)
            filenames.append(file.name)
        except Exception as e:
            st.error(f"{file.name}: {e}")

    if previews and preview:
        st.subheader("Mask previews")
        cols = st.columns(2)
        for i, (name, prev) in enumerate(zip(filenames, previews)):
            with cols[i % 2]:
                st.image(prev, caption=name, use_container_width=True)

    if st.button("Process batch", type="primary"):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar.")
            st.stop()

        progress = st.progress(0, text="Starting batch...")
        results = []
        failures = []

        jobs = []
        for name, img, mask in zip(filenames, originals, masks):
            image_bytes = to_png_bytes(img)
            mask_bytes = to_png_bytes(mask)
            jobs.append((name, image_bytes, mask_bytes))

        with ThreadPoolExecutor(max_workers=concurrency) as ex:
            futs = {
                ex.submit(edit_image_bytes, image_bytes, mask_bytes, api_key): name
                for name, image_bytes, mask_bytes in jobs
            }
            completed = 0
            total = len(futs)
            for fut in as_completed(futs):
                name = futs[fut]
                try:
                    edited_bytes = fut.result()
                    results.append((name.rsplit(".", 1)[0] + "_EDITED.jpg", edited_bytes))
                except Exception as e:
                    failures.append((name, str(e)))
                completed += 1
                progress.progress(completed / total, text=f"Processed {completed}/{total}")

        if results:
            st.subheader("Finished images")
            zip_buf = io.BytesIO()
            with zipfile.ZipFile(zip_buf, "w", zipfile.ZIP_DEFLATED) as z:
                for out_name, edited_bytes in results:
                    z.writestr(out_name, edited_bytes)
            zip_buf.seek(0)

            gallery_cols = st.columns(2)
            for i, (out_name, edited_bytes) in enumerate(results):
                with gallery_cols[i % 2]:
                    st.image(Image.open(io.BytesIO(edited_bytes)), caption=out_name, use_container_width=True)

            st.download_button(
                "Download edited ZIP",
                data=zip_buf.getvalue(),
                file_name="parkwood_edited_photos.zip",
                mime="application/zip"
            )

        if failures:
            st.warning(f"{len(failures)} file(s) failed.")
            for name, err in failures:
                st.write(f"**{name}** — {err}")

else:
    st.info("Upload one car’s exterior photos to begin.")
