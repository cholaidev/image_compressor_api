from flask import Flask, request, send_file, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)

# ✅ Path to realesrgan binary
REALESRGAN_PATH = "/home/cholai/realesrgan-ncnn-vulkan-v0.2.0-ubuntu/realesrgan-ncnn-vulkan"


@app.route("/upscale", methods=["POST"])
def upscale_image():
    if "image" not in request.files:
        print("❌ No image uploaded in request")
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    # Save input to temp file
    temp_in = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    file.save(temp_in.name)
    temp_in_path = temp_in.name
    temp_in.close()

    # Temp output file
    temp_out_path = tempfile.mktemp(suffix=".jpg")

    # Build realesrgan command
    cmd = [
        REALESRGAN_PATH,
        "-i", temp_in_path,
        "-o", temp_out_path,
        "-s", "2"  # scale factor (2x)
    ]

    print(f"📥 Input file saved at: {temp_in_path}")
    print(f"⚙️ Running command: {' '.join(cmd)}")

    try:
        subprocess.run(cmd, check=True)
        print(f"✅ Upscale process finished successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Upscale failed: {e}")
        return jsonify({"error": f"Upscale failed: {str(e)}"}), 500
    except FileNotFoundError:
        print(f"❌ Executable not found at {REALESRGAN_PATH}")
        return jsonify({"error": f"Executable not found: {REALESRGAN_PATH}"}), 500
    finally:
        # Always cleanup input file
        if os.path.exists(temp_in_path):
            os.remove(temp_in_path)
            print(f"🗑️ Deleted temp input file {temp_in_path}")

    if not os.path.exists(temp_out_path):
        print("❌ No output image generated")
        return jsonify({"error": "No output image generated"}), 500

    print(f"📤 Sending file back: {temp_out_path}")

    # ✅ Send back the result
    return send_file(
        temp_out_path,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="upscaled.jpg"
    )


if __name__ == "__main__":
    # Run Flask on server (port 5000)
    print("🚀 Flask Real-ESRGAN server started on http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
