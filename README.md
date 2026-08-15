# Telegram Image Format Converter Bot (@sillysistbot)

A production-ready Telegram bot built with **Python 3**, **python-telegram-bot (v20+)**, and **Pillow** that converts image files between common formats seamlessly inside Telegram.

---

## 🌟 Features

- **Supported Output Formats:** `JPG`, `PNG`, `WEBP`, `GIF`, `BMP`, `TIFF`.
- **Smart Transparency Handling:** Automatically blends transparent `RGBA`/`PNG` images over a solid white background when converting to `JPG` or `BMP`.
- **Flexible File Input:** Accepts compressed Telegram photo messages as well as original file document attachments.
- **Auto-Cleanup:** Immediate deletion of temporary uploaded and converted files to safeguard memory and privacy.
- **Robust Error Handling:** File size validation, corrupted file rejection, and graceful user error messages.
- **Render Ready:** Includes a background HTTP health server endpoint for Render Web Service deployment compatibility.

---

## 📁 Project Structure

```text
image-format-converter-bot/
├── .env.example
├── .gitignore
├── render.yaml
├── requirements.txt
├── config.py
├── bot.py
├── utils/
│   ├── cleanup.py
│   └── image_converter.py
├── handlers/
│   ├── start.py
│   ├── help.py
│   └── conversion.py
└── README.md
