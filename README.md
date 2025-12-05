# Sainathai Automation Project

This repository contains the services for a social media automation pipeline. The project is structured for easy deployment on Hugging Face Spaces.

## Repository Structure

The repository is now organized into two main services:

-   `n8n/`: Contains the n8n workflow automation engine. This is a Docker-based service that orchestrates the entire content pipeline. See the `n8n/README.md` for detailed deployment instructions.
-   `video_renderer/`: Contains the Python Flask service for dynamically generating videos. This is a Python-based service. See the `video_renderer/README.md` for detailed deployment instructions.

## Deployment on Hugging Face

To deploy the full system, you will need to create **two separate Hugging Face Spaces**:

1.  **n8n Service:** A Docker Space pointing to the `n8n` directory.
2.  **Video Renderer Service:** A Python Space pointing to the `video_renderer` directory.

Please refer to the `README.md` file inside each directory for specific setup and configuration instructions.
