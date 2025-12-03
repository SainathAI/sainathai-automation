# pylint: disable=no-member
"""
Flask application for rendering videos using MoviePy.
"""
import os
import requests
from flask import Flask, request, jsonify
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    TextClip,
    ColorClip,
)
from moviepy.video.fx import all as vfx

app = Flask(__name__)

# Temporary storage for downloaded files
TMP_PATH = "tmp"
if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)


def download_file(url, local_filename):
    """Downloads a file from a URL to a local path."""
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return local_filename


def create_visuals(visual_paths, duration, size):
    """Creates a video clip from a list of visual assets."""
    clips = []
    clip_duration = duration / len(visual_paths)
    for path in visual_paths:
        clip = ImageClip(path).set_duration(clip_duration)
        cropped_clip = clip.fx(vfx.resize, newsize=size)
        clips.append(cropped_clip)
    return concatenate_videoclips(clips, method="compose").set_position("center")


def group_words_into_lines(timed_script, max_line_length=30):
    """Groups words into lines based on a maximum line length."""
    lines = []
    current_line = []
    current_length = 0
    for word_info in timed_script:
        word = word_info["word"]
        if current_length + len(word) > max_line_length and current_line:
            lines.append(current_line)
            current_line = []
            current_length = 0
        current_line.append(word_info)
        current_length += len(word) + 1
    if current_line:
        lines.append(current_line)
    return lines


def create_subtitles(final_video, timed_script):
    """Creates dynamic subtitles from a timed script."""
    subtitle_clips = []
    lines = group_words_into_lines(timed_script)

    for line in lines:
        for i, word_info in enumerate(line):
            start_time = word_info["start"]
            duration = word_info["end"] - word_info["start"]
            words_before = " ".join(w["word"] for w in line[:i])
            current_word = word_info["word"]
            words_after = " ".join(w["word"] for w in line[i + 1 :])
            pango_markup = (
                f'<span foreground="#FFFFFF">{words_before} </span>'
                if words_before
                else ""
            ) + f'<span foreground="#EAB600">{current_word}</span>'
            if words_after:
                pango_markup += f'<span foreground="#FFFFFF"> {words_after}</span>'

            pango_markup = pango_markup.strip()
            txt_clip = (
                TextClip(
                    pango_markup,
                    fontsize=70,
                    font="Arial-Bold",
                    stroke_color="black",
                    stroke_width=2,
                    method="pango",
                    size=(final_video.w * 0.9, None),
                )
                .set_pos(("center", "bottom"))
                .set_start(start_time)
                .set_duration(duration)
            )
            subtitle_clips.append(txt_clip)
    return subtitle_clips


def create_watermark(final_video, duration):
    """Creates a watermark clip."""
    logo_path = "assets/logo.png"
    return (
        ImageClip(logo_path)
        .set_duration(duration)
        .resize(width=final_video.w // 10)
        .set_opacity(0.35)
        .set_pos(("left", "top"))
    )


def create_outro(final_video):
    """Creates a branded outro clip."""
    logo_path = "assets/logo.png"
    outro_duration = 1.5
    outro_bg = ColorClip(
        size=final_video.size, color=(0, 0, 0), duration=outro_duration
    )
    outro_logo = (
        ImageClip(logo_path)
        .set_duration(outro_duration)
        .resize(width=final_video.w * 0.3)
        .set_pos("center")
    )
    outro_logo_animated = outro_logo.fx(
        vfx.fadein, duration=outro_duration * 0.5
    ).fx(vfx.resize, lambda t: 1 + t * 0.2)
    return CompositeVideoClip([outro_bg, outro_logo_animated.set_pos("center")])


@app.route("/render-video", methods=["POST"])
def render_video():
    """
    Main endpoint to render the video.
    """
    data = request.json
    if not all(k in data for k in ["audio_url", "visual_urls", "timed_script"]):
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        audio_path = download_file(
            data["audio_url"], os.path.join(TMP_PATH, "audio.mp3")
        )
        visual_paths = [
            download_file(
                url,
                os.path.join(TMP_PATH, f"visual_{i}{os.path.splitext(url)[1] or '.jpg'}"),
            )
            for i, url in enumerate(data["visual_urls"])
        ]

        audio_clip = AudioFileClip(audio_path)
        video_size = (1080, 1920)

        final_video = create_visuals(visual_paths, audio_clip.duration, video_size)
        final_video.audio = audio_clip

        subtitle_clips = create_subtitles(final_video, data["timed_script"])
        logo_clip = create_watermark(final_video, audio_clip.duration)

        main_video = CompositeVideoClip([final_video, logo_clip] + subtitle_clips)
        outro = create_outro(final_video)

        final_composition = concatenate_videoclips([main_video, outro])

        output_path = os.path.join(TMP_PATH, "final_video.mp4")
        final_composition.write_videofile(
            output_path, fps=24, codec="libx264", audio_codec="aac"
        )

        return jsonify(
            {
                "status": "success",
                "message": "Video rendered successfully.",
                "output_path": output_path,
            }
        )

    except (requests.exceptions.RequestException, IOError) as e:
        app.logger.error("Error downloading assets: %s", str(e))
        return jsonify({"error": "Failed to download assets"}), 500
    except Exception as e:
        app.logger.error("An unexpected error occurred: %s", str(e))
        for f in os.listdir(TMP_PATH):
            os.remove(os.path.join(TMP_PATH, f))
        return jsonify(
            {"error": "An unexpected error occurred during video rendering."}
        ), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
