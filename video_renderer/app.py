
import os
from flask import Flask, request, jsonify
from moviepy.editor import *
import requests
import textwrap

app = Flask(__name__)

# Define the path for temporary files
TMP_PATH = "/tmp/"

def download_file(url, local_path):
    """Downloads a file from a URL to a local path."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_path

@app.route('/render-video', methods=['POST'])
def render_video():
    """
    Main endpoint to render the video.
    Expects a JSON payload with:
    - audio_url: URL to the voiceover audio file.
    - visual_urls: A list of URLs for background images/videos.
    - script_lines: A list of strings, where each string is a line of the script for subtitles.
    - logo_url: URL to the logo image for the watermark.
    """
    data = request.json

    if not all(k in data for k in ['audio_url', 'visual_urls', 'script_lines', 'logo_url']):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # 1. Download all assets
        audio_path = download_file(data['audio_url'], os.path.join(TMP_PATH, "audio.mp3"))
        logo_path = download_file(data['logo_url'], os.path.join(TMP_PATH, "logo.png"))

        visual_paths = []
        for i, url in enumerate(data['visual_urls']):
            # Determine file extension, default to .jpg
            extension = os.path.splitext(url)[1] or '.jpg'
            path = download_file(url, os.path.join(TMP_PATH, f"visual_{i}{extension}"))
            visual_paths.append(path)

        # 2. Load audio and determine video duration
        audio_clip = AudioFileClip(audio_path)
        video_duration = audio_clip.duration

        # 3. Create video clips from visuals
        # Each visual will have an equal share of the total video duration
        clip_duration = video_duration / len(visual_paths)
        visual_clips = [ImageClip(path).set_duration(clip_duration).set_pos("center") for path in visual_paths]

        # 4. Concatenate visual clips to form the main video track
        final_video = concatenate_videoclips(visual_clips, method="compose")
        final_video.audio = audio_clip

        # 5. Create subtitles (TextClips)
        subtitle_clips = []
        for line in data['script_lines']:
            # Wrap text to fit the screen
            wrapped_text = "\\n".join(textwrap.wrap(line, width=30))

            txt_clip = TextClip(
                wrapped_text,
                fontsize=70,
                color='white',
                font='Arial-Bold',
                stroke_color='black',
                stroke_width=2,
                bg_color='rgba(0,0,0,0.5)', # Semi-transparent background
                size=(final_video.w * 0.8, None) # 80% of video width
            ).set_pos(('center', 'center'))
            subtitle_clips.append(txt_clip)

        # Assume each subtitle line is shown for an equal amount of time for now
        # A more advanced implementation would sync this with the audio
        subtitle_duration = video_duration / len(subtitle_clips)
        for i, clip in enumerate(subtitle_clips):
            clip.start = i * subtitle_duration
            clip.duration = subtitle_duration

        # 6. Add watermark
        logo_clip = (ImageClip(logo_path)
                     .set_duration(video_duration)
                     .resize(height=100) # Adjust size as needed
                     .margin(right=20, top=20, opacity=0) # Add padding
                     .set_pos(("right","top")))

        # 7. Composite all layers together
        final_composition = CompositeVideoClip([final_video, logo_clip] + subtitle_clips)

        # 8. Define output path and write the final video file
        output_filename = "final_video.mp4"
        output_path = os.path.join(TMP_PATH, output_filename)
        final_composition.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")

        # In a real-world scenario, you would upload this file to a cloud storage
        # and return the URL. For now, we'll just confirm completion.

        return jsonify({
            "status": "success",
            "message": "Video rendered successfully.",
            "output_path": output_path # This path is inside the container
        })

    except Exception as e:
        # Clean up downloaded files on error
        for f in os.listdir(TMP_PATH):
            os.remove(os.path.join(TMP_PATH, f))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # The default port is 5000. Google Cloud Run expects the container
    # to listen on the port defined by the PORT environment variable.
    port = int(os.environ.get("PORT", 8080))
    app.run(debug=True, host='0.0.0.0', port=port)
