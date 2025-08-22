from flask import Flask, request, send_file
import subprocess
import tempfile
import os
import shutil

app = Flask(__name__)

# ✅ Full path to realesrgan binary in your server
REALESRGAN_PATH = "/home/cholai/realesrgan-ncnn-vulkan-v0.2.0-ubuntu/realesrgan-ncnn-vulkan"

@app.route("/upscale", methods=["POST"])
def upscale_image():
    print("📩 Request received at /upscale")

    if "image" not in request.files:
        print("❌ No image uploaded in request")
        return {"error": "No image uploaded"}, 400

    file = request.files["image"]
    print(f"✅ Image received: {file.filename}")

    # Save input to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_in:
        temp_in_path = temp_in.name
        file.save(temp_in_path)

    print(f"📂 Temp input file saved: {temp_in_path}")

    # Output file path
    temp_out_path = tempfile.mktemp(suffix=".jpg")

    # Build realesrgan command
    cmd = [
        REALESRGAN_PATH,
        "-i", temp_in_path,
        "-o", temp_out_path,
        "-s", "2"  # scale factor 2x
    ]

    print(f"🚀 Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Upscale successful, output saved: {temp_out_path}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Upscale failed: {e}")
        return {"error": f"Upscale failed: {str(e)}"}, 500
    except FileNotFoundError:
        print(f"❌ Executable not found: {REALESRGAN_PATH}")
        return {"error": f"Executable not found: {REALESRGAN_PATH}"}, 500

    # Copy output to avoid file lock issues
    final_out = tempfile.mktemp(suffix=".jpg")
    shutil.copy(temp_out_path, final_out)

    # Cleanup temp files
    os.remove(temp_in_path)
    os.remove(temp_out_path)

    print(f"📤 Sending upscaled image back: {final_out}")

    return send_file(
        final_out,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="upscaled.jpg"
    )

if __name__ == "__main__":
    print("🚀 Starting Flask Real-ESRGAN server on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
