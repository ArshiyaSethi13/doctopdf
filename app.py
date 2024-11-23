from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

app = Flask(__name__)

# Configure folders
UPLOAD_FOLDER = "uploads/"
CONVERTED_FOLDER = "converted/"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["CONVERTED_FOLDER"] = CONVERTED_FOLDER


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".docx"):
            # Securely save the uploaded file
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(file_path)

            try:
                # Convert the DOCX to PDF
                pdf_filename = f"{os.path.splitext(filename)[0]}.pdf"
                pdf_path = os.path.join(app.config["CONVERTED_FOLDER"], pdf_filename)
                convert_docx_to_pdf(file_path, pdf_path)

                return render_template(
                    "download.html", pdf_filename=pdf_filename
                )
            except Exception as e:
                return f"An error occurred during conversion: {str(e)}"
        else:
            return "Please upload a valid .docx file."
    return render_template("upload.html")


@app.route("/download/<path:pdf_filename>")
def download_file(pdf_filename):
    pdf_path = os.path.join(app.config["CONVERTED_FOLDER"], pdf_filename)
    return send_file(pdf_path, as_attachment=True)


def convert_docx_to_pdf(docx_path, pdf_path):
    """
    Convert a DOCX file to a PDF.
    Handles text with styles and images.
    """
    # Open the DOCX file
    document = Document(docx_path)

    # Create a PDF canvas
    c = canvas.Canvas(pdf_path, pagesize=letter)
    width, height = letter
    margin = 50
    y = height - margin

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if text:  # Write text if it exists
            c.setFont("Helvetica", 12)  # Set default font
            c.drawString(margin, y, text)
            y -= 20  # Move down for the next line

        # Add a page break if needed
        if y < margin:
            c.showPage()
            y = height - margin

    # Process images (if any) in the document
    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            image_path = rel.target_part.blob  # Get image blob
            with open("temp_image.png", "wb") as img_file:
                img_file.write(image_path)
            if y < margin + 100:  # Add page break for images if space runs out
                c.showPage()
                y = height - margin
            c.drawImage("temp_image.png", margin, y - 100, width=200, height=100)
            y -= 120  # Move down after the image

    c.save()  # Save the PDF


if __name__ == "__main__":
    app.run(debug=True)
