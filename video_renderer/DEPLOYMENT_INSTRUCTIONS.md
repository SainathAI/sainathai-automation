# Google Cloud Run Deployment Instructions

This guide provides the step-by-step instructions to deploy the video rendering service to Google Cloud Run.

## Prerequisites

1.  **Google Cloud Account:** You must have a Google Cloud Platform (GCP) account with billing enabled. The Cloud Run "Always Free Tier" is very generous and should be sufficient for your stated needs.
2.  **Google Cloud SDK:** You need to have the `gcloud` command-line tool installed and initialized on your local machine. You can find installation instructions [here](https://cloud.google.com/sdk/docs/install).
3.  **Docker:** Docker must be installed and running on your local machine.
4.  **Enable APIs:** In your GCP project, make sure you have the following APIs enabled:
    *   Cloud Run API (`run.googleapis.com`)
    *   Artifact Registry API (`artifactregistry.googleapis.com`)
    *   Cloud Build API (`cloudbuild.googleapis.com`)

You can enable them with these gcloud commands:

```bash
gcloud services enable run.googleapis.com artifactregistry.googleapis.com cloudbuild.googleapis.com
```

## Deployment Steps

Follow these commands from your terminal, in the root directory of this repository.

### 1. Set Your Project ID and Region

First, configure your environment with your specific GCP Project ID and the region you want to deploy to (e.g., `us-central1`).

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1 # Or your preferred region
```

### 2. Create an Artifact Registry Repository

Artifact Registry is where your Docker container images will be stored. You only need to do this once per project.

```bash
gcloud artifacts repositories create video-renderer-repo \\
    --repository-format=docker \\
    --location=$REGION \\
    --description="Repository for video renderer images"
```

### 3. Configure Docker Authentication

Configure the Docker client to authenticate with Artifact Registry. This allows you to push images to your repository.

```bash
gcloud auth configure-docker $REGION-docker.pkg.dev
```

### 4. Build and Deploy with a Single Command

Google Cloud Run can build and deploy directly from your source code using Cloud Build. This is the simplest and recommended method.

Navigate into the `video_renderer` directory:
```bash
cd video_renderer
```

Then, run the following `gcloud run deploy` command. This command will:
*   Build the Docker image from your `Dockerfile`.
*   Push the image to the Artifact Registry repository we created.
*   Deploy the image to Cloud Run as a new service named `video-renderer-service`.

```bash
gcloud run deploy video-renderer-service \\
    --source . \\
    --platform managed \\
    --region $REGION \\
    --allow-unauthenticated \\
    --memory=2Gi \\
    --timeout=900 \\
    --project=$PROJECT_ID
```
**Command Flags Explained:**
*   `--source .`: Tells Cloud Run to build from the current directory.
*   `--platform managed`: Use the fully managed Cloud Run environment.
*   `--allow-unauthenticated`: This makes your service public so that your n8n workflow can call it.
*   `--memory=2Gi`: Allocates 2 GiB of memory. Video processing is memory-intensive, and this is a good starting point.
*   `--timeout=900`: Sets the request timeout to the maximum of 15 minutes (900 seconds). This is **critical** as video rendering can take a long time.

### 5. Get Your Service URL

After the deployment completes successfully, the command will output the **Service URL**. It will look something like this:

`https://video-renderer-service-xxxxxxxxxx-uc.a.run.app`

This is the public URL for your video rendering service.

## Final Step: Update Your n8n Workflow

1.  Copy the **Service URL** from the deployment output.
2.  Go to your n8n workflow (`social_media_workflow.json`).
3.  Find the node named "**5. Call Video Rendering Service**".
4.  Paste your Service URL into the "URL" field, replacing the placeholder `https://YOUR-CLOUD-RUN-SERVICE-URL.a.run.app/render-video`.

Your video automation pipeline is now fully configured!
