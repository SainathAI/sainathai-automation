---
title: n8n Workflow Automation
emoji: 🚀
colorFrom: green
colorTo: blue
sdk: docker
pinned: false
app_port: 5678
# Add persistent storage for n8n data (workflows, credentials, etc.)
# This ensures your data is not lost on restart.
persistent_storage:
  - path: /root/.n8n
    name: n8n-data

# Secrets configuration
# IMPORTANT: You must create these secrets in your Hugging Face Space settings.
# 1. N8N_ENCRYPTION_KEY: A long, random string for securing credentials.
#    You can generate one here: https://www.random.org/strings/?num=1&len=32&digits=on&upperalpha=on&loweralpha=on&unique=on&format=html&rnd=new
# 2. DB_USER, DB_PASSWORD, DB_HOST, DB_DATABASE, DB_PORT: Your PostgreSQL database credentials.
secrets:
  - key: N8N_ENCRYPTION_KEY
    description: "A long, random string used to encrypt credential data. DO NOT LOSE THIS."
  - key: DB_TYPE
    value: "postgresdb" # This is fixed for PostgreSQL
  - key: DB_USER
    description: "The username for your PostgreSQL database."
  - key: DB_PASSWORD
    description: "The password for your PostgreSQL database."
  - key: DB_HOST
    description: "The host address of your PostgreSQL database."
  - key: DB_DATABASE
    description: "The name of your PostgreSQL database."
  - key: DB_PORT
    description: "The port for your PostgreSQL database (usually 5432)."
---

# 🚀 n8n Workflow Automation Engine

This is the central orchestration service for the social media automation pipeline, powered by [n8n](https://n8n.io/).

## ⚠️ Important Setup Instructions

This service requires a **PostgreSQL database** to function correctly. The free tier on Render is no longer sufficient, but you can get a free PostgreSQL database from services like [Neon](https://neon.tech/) or [Supabase](https://supabase.com/).

### Steps to Deploy:

1.  **Create a Hugging Face Space:**
    *   Choose "Docker" as the Space SDK.
    *   Select this repository and ensure the "Space directory" is set to `n8n`.
    *   Configure the secrets listed above in the "Settings" tab of your new Space.

2.  **Set up a Free PostgreSQL Database:**
    *   Go to a provider like [Neon](https://neon.tech/).
    *   Create a new project and a new database.
    *   Find your database connection details (Host, Database Name, User, Password, Port).

3.  **Add Secrets to Hugging Face:**
    *   In your Hugging Face Space, go to **Settings > Secrets**.
    *   Add each of the database credentials (`DB_USER`, `DB_PASSWORD`, etc.) as separate secrets.
    *   **Crucially**, also add the `N8N_ENCRYPTION_KEY`. Create a strong, unique key and save it somewhere safe. If you lose it, your n8n credentials will be unrecoverable.

Once the secrets are set and the Space is running, your n8n instance will be live and ready to automate your workflows.

### Post-Deployment Step:

After both the `n8n` and `video_renderer` Spaces are deployed and running, remember to:

1.  Navigate to your n8n instance.
2.  Open your `social_media_workflow`.
3.  Update any "HTTP Request" nodes that call the video renderer to use your new Hugging Face Space URL for the `video_renderer`.
