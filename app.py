import os
import subprocess
import time
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

BASE_DIR = "/home/cholai/realesrgan-ncnn-vulkan-v0.2.0-ubuntu"
REALESRGAN_BIN = os.path.join(BASE_DIR, "realesrgan-ncnn-vulkan")

@app.route('/upscale', methods=['POST'])
def upscale():
    try:
        print("🔹 Step 1: Checking request method...")
        print("   Method received:", request.method)

        print("🔹 Step 2: Checking uploaded file...")
        if 'image' not in request.files:
            print("❌ No file part in request.files")
            return jsonify({"error": "No image uploaded"}), 400

        file = request.files['image']
        print("✅ File received:", file.filename)

        # 🔹 Add timestamp to avoid overwriting files
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        input_path = os.path.join(BASE_DIR, f"input_{timestamp}.jpg")
        output_path = os.path.join(BASE_DIR, f"output_{timestamp}.png")

        print(f"🔹 Step 3: Saving input file to {input_path} ...")
        file.save(input_path)
        print("✅ File saved")

        print(f"🔹 Step 4: Preparing ESRGAN command...")
        cmd = [
            REALESRGAN_BIN,
            "-i", input_path,
            "-o", output_path
        ]
        print("⚡ Command:", " ".join(cmd))

        print("🔹 Step 5: Running ESRGAN...")
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print("✅ ESRGAN finished")

        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode != 0:
            print("❌ ESRGAN process failed")
            return jsonify({
                "error": "Real-ESRGAN failed",
                "stderr": result.stderr,
                "stdout": result.stdout
            }), 500

        print("🔹 Step 6: Checking output file...")
        if not os.path.exists(output_path):
            print("❌ Output not generated")
            return jsonify({"error": "Output not generated"}), 500

        print("✅ Output file ready, sending info back")
        return jsonify({
            "message": "Upscaling successful",
            "input_file": os.path.basename(input_path),
            "output_file": os.path.basename(output_path),
            "download_url": f"/get-file/{os.path.basename(output_path)}"
        })

    except Exception as e:
        print("🔥 Exception:", str(e))
        return jsonify({"error": str(e)}), 500


@app.route("/get-file/<filename>", methods=["GET"])
def get_file(filename):
    """Allow downloading any saved input/output file by name"""
    file_path = os.path.join(BASE_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    return send_file(file_path)


if __name__ == "__main__":
    print("🚀 Starting Flask server at http://0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True)
