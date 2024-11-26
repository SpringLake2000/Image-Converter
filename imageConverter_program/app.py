from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from PIL import Image, ImageFilter
import numpy as np
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULT_FOLDER'] = 'static'
app.config['SECRET_KEY'] = 'secret-key'  # Change to a random secret for production use

# Ensure upload and result directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['RESULT_FOLDER'], exist_ok=True)


@app.route("/", methods=["GET", "POST"])
def upload_image():
    if request.method == "POST":
        # Get the uploaded file
        image = request.files.get("image")
        if not image:
            return render_template("index.html", error="Please upload an image!")

        # Save the file to the upload folder
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(input_path)

        # Get the selected operation (grayscale or blur)
        operation = request.form.get("operation")
        if not operation:
            return render_template("index.html", error="Please select an operation!")

        # Process the image
        output_path = os.path.join(app.config['RESULT_FOLDER'], f"processed_{image.filename}")
        process_image(input_path, output_path, operation)

        # Redirect to the result page
        return redirect(url_for("show_result", input_image=image.filename, output_image=f"processed_{image.filename}"))

    return render_template("index.html")


@app.route("/result")
def show_result():
    input_image = request.args.get("input_image")
    output_image = request.args.get("output_image")

    return render_template("result.html", 
                           input_image=url_for("uploaded_file", filename=input_image), 
                           output_image=output_image)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


def process_image(input_path, output_path, operation):
    """Process the image using NumPy for pixel manipulation."""
    # Open the image using PIL and convert to a NumPy array
    with Image.open(input_path) as img:
        image_array = np.array(img)

        if operation == "grayscale":
            # Convert to grayscale by calculating the mean of the R, G, and B channels
            grayscale_array = np.mean(image_array[..., :3], axis=2, dtype=int)  # Mean across R, G, B channels
            result_array = np.stack([grayscale_array] * 3, axis=-1)  # Stack grayscale values back into 3 channels

            # Ensure the resulting array is of the correct data type (uint8)
            result_array = result_array.astype(np.uint8)

        elif operation == "blur":
            # Apply blur using PIL's GaussianBlur (unchanged from original)
            processed_img = img.filter(ImageFilter.GaussianBlur(radius=10))  # Stronger blur
            processed_img.save(output_path)
            return  # Return early since the blur operation is handled by PIL directly

        else:
            raise ValueError("Invalid operation")

        # Save the processed grayscale image
        result_image = Image.fromarray(result_array)
        result_image.save(output_path)

if __name__ == "__main__":
    app.run(debug=True)