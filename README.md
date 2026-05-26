# 🍔 Food Delivery Time Estimation System

## Overview

Food Delivery Time Estimation System is a Streamlit-based web application that combines:

* Food ordering
* User authentication
* Location selection using maps
* Delivery tracking
* Machine Learning-based delivery estimation

The application provides a complete mini food-ordering workflow where users can:

1. Register/Login
2. Browse food items
3. Select a food item
4. Choose quantity
5. Select delivery location on a map
6. Place an order
7. Track delivery progress

This project is focused on combining Machine Learning concepts with frontend UI and backend logic using Python and Streamlit.

---

# 🚀 Features

## Authentication System

* User Registration
* Login System
* Password visibility toggle
* Session handling

## Food Ordering

* Food menu interface
* Food detail page
* Quantity selection
* Price calculation

## Location Tracking

* Interactive map selection
* Latitude & Longitude capture
* Selected location display

## Delivery Estimation

* Delivery progress tracker
* Estimated delivery time
* Completion status

## Machine Learning

* Uses trained ML model (`rfr_model.pkl`)
* Random Forest Regression based prediction system

---

# 🛠️ Technologies Used

* Python
* Streamlit
* Machine Learning
* Random Forest Regression
* Pickle Model
* HTML/CSS
* Folium Maps
* Pandas
* NumPy

---

# 📂 Project Structure

```bash
Food-Delivery-Time-Estimation-main/
│
├── f.py                     # Main Streamlit application
├── s.py                     # Supporting logic
├── image.py                 # Image handling
├── rfr_model.pkl            # Trained ML model
├── style2.css               # Main UI styling
├── style_register.css       # Registration page styling
├── food.webp                # Background image
└── README.md
```

---

# 📸 Application Screenshots

## 1. Login Page

The application starts with a login interface where users can enter email and password.

<img src="Screenshot 2025-12-24 175041.png" width="100%">

---

## 2. Registration Page

New users can create an account using the registration form.

<img src="Screenshot 2025-12-24 175119.png" width="100%">

---

## 3. Food Menu Interface

Users can browse multiple food items from the menu.

Features:

* Food image
* Food name
* Selection button

<img src="Screenshot 2025-12-24 175242.png" width="100%">

---

## 4. Food Details Page

After selecting a food item, the system displays detailed information.

Features:

* Food image
* Hotel name
* Price
* Quantity selector
* Total price calculation

<img src="Screenshot 2025-12-24 175339.png" width="100%">

---

## 5. Location Selection System

Users can select their delivery location directly from an interactive map.

Features:

* Map integration
* Latitude & Longitude detection
* Area identification

<img src="Screenshot 2025-12-24 175747.png" width="100%">

---

## 6. Delivery Progress Tracking

After placing an order, users can monitor delivery progress.

Features:

* Progress bar
* Delivery time tracking
* Completion status

<img src="Screenshot 2025-12-22 204352.png" width="100%">

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/suriyaelumalai08/Food-Delivery-Time-Estimation.git
```

---

## Move into Project Folder

```bash
cd Food-Delivery-Time-Estimation
```

---

## Install Required Libraries

```bash
pip install streamlit pandas numpy scikit-learn folium streamlit-folium
```

---

# ▶️ Run the Project

```bash
streamlit run f.py
```

The application will open in:

```bash
http://localhost:8501
```

---

# 🧠 Machine Learning Component

This project uses:

## Random Forest Regression

The trained model:

```bash
rfr_model.pkl
```

is used to estimate delivery-related predictions.

Possible input factors:

* Distance
* Location
* Order details
* Delivery conditions

---

# 🎨 UI Design

The project contains custom CSS styling for:

* Login page
* Registration page
* Food cards
* Buttons
* Layout design
* Delivery tracker

Files:

```bash
style2.css
style_register.css
```

---

# 📈 Future Improvements

Current project is visually good for a student-level project, but technically it still has limitations.

Recommended improvements:

## Important Improvements

* Add real database integration
* Use MongoDB or MySQL
* Add payment gateway
* Add real-time order tracking
* Improve ML prediction accuracy
* Add admin dashboard
* Add responsive mobile UI
* Deploy using Streamlit Cloud or Render
* Add proper backend API structure
* Separate frontend and backend

Right now the project is mainly UI + workflow simulation with partial ML integration.

---

# 📚 Learning Outcomes

This project demonstrates:

* Streamlit development
* Machine Learning integration
* Random Forest Regression
* UI design with CSS
* Interactive maps
* Authentication workflow
* Session management
* Python application structure

---

# 👨‍💻 Author

## Suriya Elumalai

BCA Graduate | Python & AI Enthusiast

### Skills

* Python
* Machine Learning
* Deep Learning Basics
* Computer Vision
* NLP Basics
* Streamlit
* Flask
* FastAPI
* Data Analysis

GitHub:

[https://github.com/suriyaelumalai08](https://github.com/suriyaelumalai08)

---

# 📄 License

This project is created for educational and learning purposes.
