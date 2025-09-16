# 🎓 Multilingual Campus Chatbot

A multilingual conversational assistant designed for college campuses to handle repetitive student queries like fee deadlines, scholarship forms, and timetable changes.  
It understands **English, Hindi, and multiple regional languages**, maintains context across follow-up questions, logs conversations for review, and integrates seamlessly into the college website and messaging platforms.

---

## 🚀 Features

- 🗣️ **Multilingual Support** – English + Hindi + 3 regional languages (extensible).
- 🤖 **Intelligent Query Handling** – Uses Rasa NLU for accurate intent recognition & entity extraction.
- 🔄 **Context Management** – Handles multi-turn conversations.
- 👥 **Fallback to Human** – Routes complex queries to staff when needed.
- 📜 **Daily Logs** – Stores interactions for continuous improvement.
- 🌐 **Multi-Channel Integration** – Works on college website & popular messaging apps.
- 🔒 **Privacy-Focused** – Self-hosted, no external API fees.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
|Frontend (UI)|ReactJS (custom chatbot widget)|
|Backend (NLU & Dialogue)|Rasa (Open Source) + IndicBERT/MuRIL embeddings|
|Messaging Connectors|Rasa Channels (REST, WhatsApp, Telegram)|
|Hosting|College server / Cloud (for backend); Netlify/Vercel for frontend|
|Database (Logs)|SQLite / PostgreSQL|

---

## 📂 Project Structure

