import streamlit as st
from pymongo import MongoClient
from bson import ObjectId
import base64
from io import BytesIO
from PIL import Image
import json
from datetime import datetime
from streamlit_folium import st_folium
import folium
import requests
from math import radians, sin, cos, sqrt, atan2
import random
import pickle
import numpy as np
import time

# ---------------- MongoDB ----------------
client = MongoClient("mongodb://localhost:27017/")

# Database + collections
db = client["FOOD_DELIVERY_APP"]
users = db["users"]
food_items = db["item"]
Oder = db["Oder"]   # NEW collection to store map clicks
dname=db['demo']


#-----------------Model Prediction function------------------------

# ✅ Load model ONCE (global, not inside function)
with open("rfr_model.pkl", "rb") as f:
    MODEL = pickle.load(f)


# -------------------------------------------------
# SESSION STATE INIT
# -------------------------------------------------
if "delivery_active" not in st.session_state:
    st.session_state.delivery_active = False

if "delivery_start_ts" not in st.session_state:
    st.session_state.delivery_start_ts = None

if "est_minutes" not in st.session_state:
    st.session_state.est_minutes = None
 

def model_prediction(distance, weather, vehicle_type):

    # Normalize inputs
    weather = weather.strip().lower()
    vehicle_type = vehicle_type.strip().lower()

    mapping_weather = {
        "clear": 0,
        "windy": 1,
        "snowy": 2,
        "foggy": 3,
        "rainy": 4,
        "rain": 4
    }

    mapping_vehicle = {
        "bike": 0,
        "car": 1,
        "scooter": 2,
        "bicycle": 3,
        "scooty": 2
    }

    weather_encode = mapping_weather.get(weather)
    vehicle_encode = mapping_vehicle.get(vehicle_type)

    if weather_encode is None:
        raise ValueError(f"Unknown weather value: {weather}")

    if vehicle_encode is None:
        raise ValueError(f"Unknown vehicle type: {vehicle_type}")

    X = np.array([[distance, weather_encode, vehicle_encode]])

    return MODEL.predict(X)[0]



#-----------------Random vehicle Type------------------------
def random_vehicle():
    vehicle_list=['Bike','Scooty','Car']
    return random.choice(vehicle_list)

# SLIDER FUNCTION (AUTO RUN)
# -------------------------------------------------

def slider_devlivery(est_minutes):
    """
    Auto-running delivery progress
    1 → 2 → ... → est_minutes (real-time minutes)
    """

    # Initialize start time once
    if st.session_state.delivery_start_ts is None:
        st.session_state.delivery_start_ts = time.time()

    # Time calculations
    elapsed_sec = time.time() - st.session_state.delivery_start_ts
    elapsed_min = int(elapsed_sec // 60)   # full minutes passed

    # Clamp value
    if elapsed_min > est_minutes:
        elapsed_min = est_minutes

    # Progress (0.0 → 1.0)
    progress = elapsed_min / est_minutes if est_minutes > 0 else 1.0

    # UI
    st.progress(progress)
    st.markdown(
        f"""
        ### 🚚 Delivery Progress  
        ⏱ **{elapsed_min} / {est_minutes} minutes completed**
        """
    )

    # Completion
    if elapsed_min >= est_minutes:
        st.success("🎉 Delivery Completed")
        return

    # Refresh every second
    time.sleep(1)
    st.rerun()


# ---------------- Simplify Weather Description ----------------
def distance_weather(total_price):

    # ---------- BACKGROUND COLOR ----------
    st.markdown("""
    <style>
    .stApp {
        background-color: #F0F8FF;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Select your Order Location")

    # -------------------------------
    # Create a clickable map
    # -------------------------------
    m = folium.Map(location=[12.95, 80.1], zoom_start=8)
    m.add_child(folium.LatLngPopup())

    map_data = st_folium(m, width=900, height=500)

    # -------------------------------
    # SIMPLE WEATHER CATEGORY
    # -------------------------------
    def simplify_weather(desc):
        desc = desc.lower()
        if "rain" in desc or "drizzle" in desc:
            return "Rainy"
        if "fog" in desc or "mist" in desc or "haze" in desc:
            return "Foggy"
        if "snow" in desc or "sleet" in desc:
            return "Snowy"
        if "wind" in desc:
            return "Windy"
        return "Clear"

    # -------------------------------
    # FIXED REVERSE GEOCODING
    # -------------------------------
    def get_place_name(lat, lon):
        try:
            url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                "lat": lat,
                "lon": lon,
                "format": "json",
                "zoom": 18,
                "addressdetails": 1
            }
            headers = {
                "User-Agent": "FoodDeliveryApp/1.0"
            }

            res = requests.get(url, params=params, headers=headers, timeout=10)
            res.raise_for_status()
            data = res.json()

            addr = data.get("address", {})

            # ✅ Expanded priority for Indian locations
            return (
                addr.get("city")
                or addr.get("town")
                or addr.get("suburb")
                or addr.get("village")
                or addr.get("municipality")
                or addr.get("county")
                or addr.get("state_district")
                or addr.get("state")
                or "Unknown Place"
            )

        except Exception:
            return "Unknown Place"

    # -------------------------------
    # HANDLE USER CLICK
    # -------------------------------
    if map_data and map_data.get("last_clicked"):

        lat = map_data["last_clicked"]["lat"]
        lon = map_data["last_clicked"]["lng"]

        place_clicked = get_place_name(lat, lon)

        st.success(f"Selected Location → **{place_clicked}**")

        if st.button("Order Now"):

            # Base Location: Chepet
            base_lat = 12.466389
            base_lon = 79.350694

            # -------------------------------
            # Distance Calculation
            # -------------------------------
            def calc_distance(lat1, lon1, lat2, lon2):
                R = 6371
                dlat = radians(lat2 - lat1)
                dlon = radians(lon2 - lon1)
                a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            distance = calc_distance(base_lat, base_lon, lat, lon)

            # -------------------------------
            # WEATHER API (SAFE)
            # -------------------------------
            try:
                weather_url = f"https://wttr.in/{lat},{lon}?format=j1"
                weather_data = requests.get(weather_url, timeout=8).json()
                desc = weather_data["current_condition"][0]["weatherDesc"][0]["value"]
            except:
                desc = "Clear"

            simple_weather = simplify_weather(desc)

            # -------------------------------
            # DB FETCH
            # -------------------------------
            email_col = db["users"]
            user = email_col.find_one()

            item_col = db["item"]
            food = item_col.find_one({"_id": ObjectId(st.session_state.get("selected_food"))})

            if not food or not user:
                st.error("Order data missing")
                return

            # -------------------------------
            # INSERT ORDER
            # -------------------------------
            Oder.insert_one({
                "user_email": user["email"],
                "Food_name": food["Food_name"],
                "Total_price": total_price,
                "Distance_km": distance,
                "Weather": simple_weather,
                "vehicle_type": random_vehicle()
            })

            latest = Oder.find_one({}, sort=[("_id", -1)])

            est = model_prediction(
                latest["Distance_km"],
                latest["Weather"],
                latest["vehicle_type"]
            )

            st.info(f"""
            ### 🕒 Time Taken Prediction (in minutes)
            **{est:.2f} minutes**
            """)

            st.session_state.est_minutes = int(est)
            st.session_state.delivery_active = True
            st.session_state.delivery_start_ts = None
            st.rerun()

    else:
        st.warning("⚠ Click a location on the map first!")

# ---------------- Food Details ----------------
def show_food_details():

    food_id = st.session_state.get("selected_food")
    if not food_id:
        return

    food = food_items.find_one({"_id": ObjectId(food_id)})
    if not food:
        st.error("Food not found")
        return

    st.markdown("<hr>", unsafe_allow_html=True)
    st.header(food.get("Food_name", "Food"))

    # ---------------- IMAGE ----------------
    try:
        img_b64 = food.get("image", "")  # ✅ FIXED KEY
        if not img_b64:
            st.warning("No image available")
        else:
            if "," in img_b64:
                img_b64 = img_b64.split(",")[-1]

            img_bytes = base64.b64decode(img_b64)
            img = Image.open(BytesIO(img_bytes))
            img.load()

            st.image(img, width="stretch")  # ✅ updated

    except Exception as e:
        st.error(f"Image error: {e}")

    # ---------------- DETAILS ----------------
    st.subheader("Food Name")
    st.write(food.get("Food_name", "No Food name available"))

    st.subheader("Hotel")
    st.write(food.get("Hotal_name", "Unknown"))

    st.subheader("Price")
    price_str = food.get("Price", "₹0")
    st.write(price_str)

    # ---------------- PRICE CALC ----------------
    quantity = st.number_input("Quantity", 1, 100, 1)

    try:
        unit_price = int(price_str.replace("₹", "").replace(",", "").strip())
    except:
        unit_price = 0

    total_food_price = unit_price * quantity
    st.markdown(f"### 💰 Total Price: ₹ {total_food_price}")

    # ---------------- MAP ----------------
    distance_weather(total_food_price)

    if st.button("⬅ Back to Menu"):
        st.session_state["selected_food"] = None
        st.rerun()






#---------------Image to display-----------
def set_background_image(image_path):
    with open(image_path, "rb") as img:
        encoded = base64.b64encode(img.read()).decode()

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{encoded}");
    
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# ---------------- Food Grid ----------------
def display_food_list():
    st.markdown("""
    <style>
    .menu-title {
        text-align: center;
        font-size: 32px;
        font-weight: 800;
        margin-bottom: 40px;
    }

    .food-card {
        background: #fffaf0;
        border-radius: 22px;
        padding: 14px;
        text-align: center;
        box-shadow: 0 10px 25px rgba(0,0,0,0.08);
        transition: transform 0.35s ease, box-shadow 0.35s ease;
        cursor: pointer;
    }

    .food-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.18);
    }

    .img-box {
        overflow: hidden;
        border-radius: 18px;
    }

    .img-box img {
        width: 100%;
        height: 180px;
        object-fit: cover;
        transition: transform 0.5s ease;
    }

    /* 🔥 THIS IS THE KEY */
    .food-card:hover .img-box img {
        transform: scale(1.15);
    }

    .food-title {
        margin-top: 14px;
        font-weight: 700;
        font-size: 16px;
    }

    div.stButton > button {
        width: 100%;
        margin-top: 12px;
        background-color: #f5b400;
        color: white;
        border: none;
        padding: 8px 18px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 600;
    }

    div.stButton > button:hover {
        background-color: #e0a300;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='menu-title'>View Our Menu</div>", unsafe_allow_html=True)

    foods = list(food_items.find())
    if not foods:
        st.warning("No foods found.")
        return

    cols = st.columns(4)

    for i, food in enumerate(foods):
        try:
            img_b64 = food.get("image", "")
            if not img_b64:
                continue

            if "," in img_b64:
                img_b64 = img_b64.split(",")[-1]

            with cols[i % 4]:
                st.markdown(f"""
                <div class="food-card">
                    <div class="img-box">
                        <img src="data:image/jpeg;base64,{img_b64}">
                    </div>
                    <div class="food-title">
                        {food.get("Food_name","FOOD").upper()}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("Select", key=f"select_{food['_id']}"):
                    st.session_state["selected_food"] = str(food["_id"])
                    st.rerun()

        except Exception as e:
            st.error(f"Image load failed: {e}")
            continue
       
# ---------------- Login ----------------
def login_page():
    set_background_image("food.webp")
    with open("style2.css",'r') as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    
    st.markdown(
    '<div class="login-wrapper"><h2 class="login-title">Login</h2></div>',
    unsafe_allow_html=True)

    st.markdown('<div class="email-label">Email</div>', unsafe_allow_html=True)
    email=st.text_input("Email", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

   # PASSWORD (styled using markdown)
    st.markdown('<div class="password-box">', unsafe_allow_html=True)

    st.markdown('<div class="password-label">Password</div>', unsafe_allow_html=True)
    password=st.text_input("Password", type="password", label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)

    # BUTTONS (styled)
    st.markdown('<div class="button-box">', unsafe_allow_html=True)

    # Login button
    st.markdown('<div class="login-btn">', unsafe_allow_html=True)
    login_clicked = st.button("Login")
    st.markdown('</div>', unsafe_allow_html=True)

    # Register button
    st.markdown('<div class="register-btn">', unsafe_allow_html=True)
    register_clicked = st.button("Register")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if login_clicked:
        user = users.find_one({"email": email, "password": password})
        if user:
            st.session_state["user"] = user
            st.rerun()
        else:
            st.error("Invalid Credentials")

    if register_clicked:
        st.session_state["page"] = "register"
        st.rerun()

# ---------------- Register ----------------
def register_page():
    with open("style_register.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    # REGISTER PAGE WRAPPER
    st.markdown('<div class="register-page">', unsafe_allow_html=True)

    st.markdown('<div class="register-card">', unsafe_allow_html=True)
    st.markdown('<div class="register-header">REGISTRATION FORM</div>', unsafe_allow_html=True)
    st.markdown('<div class="register-body">', unsafe_allow_html=True)

    username = st.text_input("Username")
    email = st.text_input("Email")
    mobile = st.text_input("Mobile Number")
    password = st.text_input("Password", type="password")

    if st.button("Register"):
        if users.find_one({"email": email}):
            st.error("Email already exists")
        else:
            users.insert_one({
                "username": username,
                "email": email,
                "mobile": mobile,
                "password": password
            })
            st.success("Account created! Go to login.")
            st.session_state["page"] = "login"
            st.rerun()

    if st.button("Back to Login"):
        st.session_state["page"] = "login"
        st.rerun()

st.markdown('</div></div></div>', unsafe_allow_html=True)


# ---------------- Home ----------------
def home_page():
    st.success(f"Welcome {st.session_state['user']['email']} ! 🎉")

    if st.session_state.get("selected_food"):
        show_food_details()
    else:
        display_food_list()
    if st.session_state.delivery_active:
        slider_devlivery(st.session_state.est_minutes)
        st.stop()


    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()

# ---------------- Main ----------------
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "login"

    if "selected_food" not in st.session_state:
        st.session_state["selected_food"] = None

    if "user" in st.session_state:
        home_page()
    else:
        if st.session_state["page"] == "login":
            login_page()
        else:
            register_page()

if __name__ == "__main__":
    main()


