---
title: Python Video Renderer
emoji: 🎬
colorFrom: yellow
colorTo: orange
sdk: python
sdk_version: 3.11
python_version: 3.11
pinned: false
app_file: app.py
---

# 🎬 Python Video Rendering Service

This service is a Flask-based API that generates dynamic videos based on input scripts. It is designed to be called by the n8n orchestration service.

## Deployment

This directory is pre-configured to be deployed as a **Python Hugging Face Space**.

1.  **Create a Hugging Face Space:**
    *   Choose "Python" as the Space SDK.
    *   Select this repository and ensure the "Space directory" is set to `video_renderer`.
2.  The Space will automatically install the dependencies from `requirements.txt` and launch the application using `app.py`.
