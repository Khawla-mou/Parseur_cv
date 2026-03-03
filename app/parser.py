from flask import Flask, render_template, request
import pdfplumber
import re
import os

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "uploads"

# Fonction extraction texte PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

# Extraction informations
def extract_info(text):
    email = re.findall(r'\S+@\S+', text)
    phone = re.findall(r'\+?\d[\d\s-]{8,}', text)

    skills_keywords = ["Python", "Java", "C++", "Machine Learning",
                       "Deep Learning", "SQL", "HTML", "CSS", "JavaScript",
                       "ذكاء اصطناعي", "برمجة", "تعلم الآلة"]

    skills = []
    for skill in skills_keywords:
        if skill.lower() in text.lower():
            skills.append(skill)

    return {
        "email": email[0] if email else "Non trouvé",
        "phone": phone[0] if phone else "Non trouvé",
        "skills": skills if skills else ["Non trouvées"]
    }

@app.route("/", methods=["GET", "POST"])
def index():
    data = None

    if request.method == "POST":
        file = request.files["cv"]
        if file:
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)

            text = extract_text_from_pdf(filepath)
            data = extract_info(text)

    return render_template("index.html", data=data)

if __name__ == "__main__":
    app.run(debug=True)