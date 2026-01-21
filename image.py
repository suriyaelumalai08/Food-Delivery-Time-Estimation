import streamlit as st
from pymongo import MongoClient
import base64
from PIL import Image, ImageFile
from io import BytesIO

# ---------------- PIL SAFETY ----------------
ImageFile.LOAD_TRUNCATED_IMAGES = True

# ---------------- DB CONNECTION ----------------
client = MongoClient("mongodb://localhost:27017/")
db = client["FOOD_DELIVERY_APP"]
images_col = db["item"]

# ---------------- SESSION STATE ----------------
if "refresh_gallery" not in st.session_state:
    st.session_state.refresh_gallery = False

# ---------------- CSS ----------------
st.markdown("""
<style>
.image-card {
    width: 260px;
    height: 260px;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.image-card:hover {
    transform: scale(1.05);
    box-shadow: 0 14px 35px rgba(0,0,0,0.25);
}
</style>
""", unsafe_allow_html=True)

# ---------------- ADD IMAGE ----------------
def add_image():
    st.header("➕ Add Food Item")

    Food_name = st.text_input("Food Name")
    Hotal_name = st.text_input("Hotel Name")
    Price = st.text_input("Price")

    uploaded_file = st.file_uploader(
        "Upload Food Image",
        type=["jpg", "jpeg", "png"],
        key="food_uploader"
    )

    if uploaded_file and st.button("Insert to Database"):
        try:
            # validate image
            img = Image.open(uploaded_file)
            img.verify()
            uploaded_file.seek(0)

            img_bytes = uploaded_file.read()
            img_b64 = base64.b64encode(img_bytes).decode("utf-8")

            images_col.insert_one({
                "Food_name": Food_name,
                "Hotal_name": Hotal_name,
                "Price":"₹"+Price,
                "image": img_b64,
                "latitude": "12.466387",
                "longitude": "79.350739"
            })

            st.success("✅ Image stored successfully")
            st.session_state.refresh_gallery = True
            st.rerun()


        except Exception as e:
            st.error("❌ Invalid or corrupted image")

# ---------------- SHOW IMAGES ----------------
def show_all_images():
    st.header("🍽 Food Gallery")

    docs = list(images_col.find())  # 🔴 VERY IMPORTANT

    if not docs:
        st.info("No images found in database")
        return

    cols = st.columns(3)

    for i, doc in enumerate(docs):
        try:
            img_b64 = doc.get("image")
            food_name = doc.get("Food_name", "")
            hotel_name = doc.get("Hotal_name", "")
            price = doc.get("Price", "")

            if not img_b64:
                continue

            img_bytes = base64.b64decode(img_b64)
            img = Image.open(BytesIO(img_bytes))
            img.load()

            with cols[i % 3]:
                st.image(img, width="stretch")
                st.markdown(f"**{food_name}**")
                st.write(hotel_name)
                st.write(f"{price}")

        except Exception:
            continue
# ---------------- MAIN ----------------
add_image()
show_all_images()
