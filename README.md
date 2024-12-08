# 🚑 Accident Severity Prediction Web Application 🚗

Welcome to our **Accident Severity Prediction Web Application** project! This repository showcases a cutting-edge solution for predicting the severity of traffic accidents and offers insights into road safety. 🌍💡

## 🚀 **Project Overview**
Our project combines **Machine Learning** and **Streamlit** to create a user-friendly web application tailored for:
1. **Emergency services**: Allowing paramedics to quickly predict the severity of an accident and allocate resources efficiently.
2. **Cities and municipalities**: Offering data-driven insights to improve road safety.
3. **Automotive manufacturers**: Enabling integration of our model into autonomous vehicles to automate accident severity detection and notify emergency services.

### 🌟 **The Vision**
With the rise of autonomous vehicles equipped with advanced sensors, vast amounts of real-time accident data will become available. Our vision is to leverage this data to:
- Predict accident severity (property damage vs. personal injury).
- Automatically alert police or ambulances in case of critical accidents. 🚔🚨
- Improve response times and potentially save lives. ❤️‍🩹

In addition, our tool empowers cities to analyze accident hotspots using interactive maps and take proactive measures to enhance road safety.

---

## 🔍 **Use Case**
- **Emergency Services**: Predict the severity of a reported accident.
- **City Analysis**: Visualize accident data on an interactive map (currently focused on Zürich) to identify high-risk areas and improve infrastructure.
- **Automotive Integration**: Future-proofing our model for real-time accident detection in autonomous vehicles.

---

## 🛠️ **How It Works**
1. **Data Collection**:
   - Accident data for Zürich (2012–2023) obtained via an API.
   - Additional features like weather conditions, pedestrian density, and traffic volume were also integrated using an api, to enhance predictions.

2. **Model Training**:
   - Multiple Machine Learning models were trained and tested, focusing on **Logistic Regression** and **Random Forest** classifiers.
   - Hyperparameter tuning for Random Forest was conducted using **RandomizedSearchCV** and **BayesSearchCV**.

3. **Deployment**:
   - The best-performing model is deployed in a **Streamlit** web application.
   - Available here: 👉 [Accident Severity Prediction App](https://fcs-group-project-5-7.streamlit.app)

---

## 📂 **Repository Structure**
- **Data**:
  - Download accident data via the API script: `data/api/get_data.py`.
- **Preprocessing and Modeling**:
  - Jupyter notebooks for data preprocessing and model training are in the folder: `Jupyter Notebooks for Data Preprocessing`.
- **Streamlit App**:
  - Code for the web application is in the file: `app.py`.

---

## 🌍 **Why It Matters**
- Faster and more efficient emergency responses save lives. 🚑
- Cities gain actionable insights to reduce accidents and improve infrastructure. 🛣️
- A step towards smarter, safer autonomous vehicle systems. 🚘

---

## 📊 **Features**
- **Interactive Map**: Explore accidents in Zürich by severity and location.
- **Severity Prediction**: Instantly predict the severity of an accident by inputting details.
- **Road Safety Analysis**: Identify accident-prone areas and improve road planning.

---

### 🎉 Explore, Predict, and Make Roads Safer!
We hope you enjoy exploring our project and its potential to revolutionize road safety! Feel free to contribute or share feedback.

**With 🚦 and ❤️,**  
**Team 5.7**
