from flask import Flask, request, send_file
from PIL import Image, ImageEnhance
import io

app = Flask(__name__)

@app.route("/compress", methods=["POST"])
def compress_image():
    if "image" not in request.files:
        return {"error": "No image uploaded"}, 400

    file = request.files["image"]

    # Open the uploaded image
    img = Image.open(file.stream)

    # ✅ Fix transparency issue (RGBA → RGB)
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # 🔹 Enhance sharpness
    sharpness = ImageEnhance.Sharpness(img)
    img = sharpness.enhance(1.5)

    # 🔹 Enhance color
    color = ImageEnhance.Color(img)
    img = color.enhance(1.3)

    # 🔹 Enhance brightness
    brightness = ImageEnhance.Brightness(img)
    img = brightness.enhance(1.1)

    # 🔹 Enhance contrast
    contrast = ImageEnhance.Contrast(img)
    img = contrast.enhance(1.2)

    # Save to memory with compression
    compressed_io = io.BytesIO()
    img.save(compressed_io, format="JPEG", optimize=True, quality=75)
    compressed_io.seek(0)

    return send_file(
        compressed_io,
        mimetype="image/jpeg",
        as_attachment=True,
        download_name="enhanced_compressed.jpg"
    )

if __name__ == "__main__":
    app.run(debug=True)
