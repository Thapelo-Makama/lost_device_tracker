# 🔍 Lost Device Tracker

A full-stack web application that helps South Africans recover lost or stolen devices with police assistance.

**🌐 Live Demo:** https://lost-device-tracker.onrender.com
**💻 Code:** https://github.com/Thapelo-Makama/lost_device_tracker

---

## 📋 Overview

Users register devices with IMEI numbers, upload ownership evidence (affidavits, receipts), share GPS locations, and file police reports. Admins verify evidence and assist with recovery.

---

## ✨ Features

### For Users
- 🔐 Secure registration with admin approval workflow
- 📱 Register devices with IMEI, serial, brand, model
- 📍 Live GPS tracking with interactive maps
- 📄 Upload evidence (affidavits, receipts, photos)
- 🚔 File police reports with case numbers
- 💬 Message admin publicly or privately
- 🤖 AI chatbot for platform help

### For Admins
- 📊 Real-time dashboard with statistics
- 👥 Approve / reject new user registrations
- ✅ Verify or reject uploaded evidence
- 🗂 Manage devices, reports, and messages
- 📝 Full activity log with IP addresses
- 🚫 Ban users and manage admin privileges

---

## 🛠 Tech Stack

- **Backend:** Python 3, Flask, SQLAlchemy
- **Database:** MySQL (Aiven Cloud)
- **Auth:** Flask-Login + Werkzeug hashing
- **Frontend:** Jinja2, Bootstrap 5
- **Maps:** Leaflet.js + OpenStreetMap
- **AI:** Keyword + fuzzy matching
- **Hosting:** Render + UptimeRobot

---

## 🚀 Local Setup

    git clone https://github.com/Thapelo-Makama/lost_device_tracker.git
    cd lost_device_tracker
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    python init_db.py
    python run.py

Open http://localhost:5000

**Admin Login:** admin / Admin@2024!

---

## 📄 License

MIT © Thapelo Makama
