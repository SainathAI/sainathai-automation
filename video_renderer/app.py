
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

    if not all(k in data for k in ['audio_url', 'visual_urls', 'timed_script']):
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

        # 3. Define video resolution (9:16 aspect ratio)
        video_size = (1080, 1920)

        # 4. Create video clips from visuals
        # Each visual will have an equal share of the total video duration
        clip_duration = video_duration / len(visual_paths)
        visual_clips = []
        for path in visual_paths:
            clip = ImageClip(path).set_duration(clip_duration)
            # Resize and crop to fit the 9:16 aspect ratio
            cropped_clip = clip.fx(vfx.resize, newsize=video_size)
            visual_clips.append(cropped_clip)

        # 5. Concatenate visual clips to form the main video track
        final_video = concatenate_videoclips(visual_clips, method="compose").set_position("center")
        final_video.audio = audio_clip

        # 5. Create Dynamic Subtitles
        subtitle_clips = []
        timed_script = data['timed_script']

        # Group words into lines for display
        lines = []
        current_line = []
        max_line_length = 30 # Approx chars per line
        current_length = 0
        for word_info in timed_script:
            word = word_info['word']
            if current_length + len(word) > max_line_length and current_line:
                lines.append(current_line)
                current_line = []
                current_length = 0
            current_line.append(word_info)
            current_length += len(word) + 1
        if current_line:
            lines.append(current_line)

        # Generate a clip for each word, showing the active word in gold
        for line in lines:
            for i, word_info in enumerate(line):
                start_time = word_info['start']
                duration = word_info['end'] - word_info['start']

                words_before = " ".join(w['word'] for w in line[:i])
                current_word = word_info['word']
                words_after = " ".join(w['word'] for w in line[i+1:])

                # Build the Pango markup string for rich text
                pango_markup = (f'<span foreground="#FFFFFF">{words_before} </span>' if words_before else "") + \
                               f'<span foreground="#EAB600">{current_word}</span>' + \
                               (f'<span foreground="#FFFFFF"> {words_after}</span>' if words_after else "")

                # Clean up double spaces that might occur
                pango_markup = pango_markup.strip()

                txt_clip = TextClip(
                    pango_markup,
                    fontsize=70,
                    font='Arial-Bold',
                    stroke_color='black',
                    stroke_width=2,
                    method='pango',
                    size=(final_video.w * 0.9, None) # 90% of video width
                ).set_pos(('center', 'bottom')).set_start(start_time).set_duration(duration)

                subtitle_clips.append(txt_clip)

        # 6. Add watermark
        logo_path = "assets/logo.png"
        logo_clip = (ImageClip(logo_path)
                     .set_duration(video_duration)
                     .resize(width=final_video.w // 10) # Resize to 1/10th of video width
                     .set_opacity(0.35)
                     .set_pos(("left", "top")))

        # 7. Composite all layers together for the main video
        main_video_composition = CompositeVideoClip([final_video, logo_clip] + subtitle_clips)

        # 8. Create the 1.5s branded outro
        outro_duration = 1.5
        outro_bg = ColorClip(size=final_video.size, color=(0,0,0), duration=outro_duration)
        outro_logo = (ImageClip(logo_path)
                      .set_duration(outro_duration)
                      .resize(width=final_video.w * 0.3) # Scale to 30% of video width
                      .set_pos("center"))

        # Animate the logo: fade in and scale up
        outro_logo_animated = outro_logo.fx(vfx.fadein, duration=outro_duration * 0.5) \
                                        .fx(vfx.resize, lambda t: 1 + t * 0.2) # Gentle zoom in effect

        outro_composition = CompositeVideoClip([outro_bg, outro_logo_animated.set_pos("center")])

        # 9. Concatenate the main video and the outro
        final_composition = concatenate_videoclips([main_video_composition, outro_composition])

        # 10. Define output path and write the final video file
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
