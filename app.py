import os
import re
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from werkzeug.utils import secure_filename
import PyPDF2
from docx import Document
import spacy
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

# --- Configuration de l'Application ---
app = Flask(__name__)
app.secret_key = 'votre_cle_secrete_tres_securisee_a_changer'

# Dossiers
UPLOAD_FOLDER = 'uploads'
REPORTS_FOLDER = 'reports'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['REPORTS_FOLDER'] = REPORTS_FOLDER

# Extensions de fichiers autorisées
ALLOWED_EXTENSIONS = {'pdf', 'docx'}

# Créer les dossiers s'ils n'existent pas
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(REPORTS_FOLDER, exist_ok=True)

# --- Chargement du Modèle NLP ---
print("Chargement du modèle spaCy...")
try:
    nlp = spacy.load("fr_core_news_sm")
    print("Modèle spaCy chargé avec succès.")
except OSError:
    print("ERREUR: Le modèle spaCy 'fr_core_news_sm' n'est pas installé.")
    print("Veuillez l'installer avec la commande : python -m spacy download fr_core_news_sm")
    exit()

# --- Fonctions Utilitaires ---

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ""
    try:
        with open(filepath, 'rb') as f:
            reader = PyPDF2.PdfReader(f)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF {filepath}: {e}")
        return None
    return text

def extract_text_from_docx(filepath):
    text = ""
    try:
        doc = Document(filepath)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Erreur lors de la lecture du DOCX {filepath}: {e}")
        return None
    return text

# --- FONCTION D'ANALYSE AMÉLIORÉE ET CORRIGÉE ---
def parse_cv(text):
    doc = nlp(text)
    
    # --- 1. Extraction du Nom (plus intelligente) ---
    nom = "Non trouvé"
    potential_names = []
    for i, line in enumerate(text.split('\n')):
        if i > 5: break
        line_doc = nlp(line)
        for ent in line_doc.ents:
            if ent.label_ == "PER" and len(ent.text.strip()) > 3:
                potential_names.append(ent.text.strip())
    if potential_names:
        nom = max(potential_names, key=len)

    # --- 2. Extraction Email et Téléphone ---
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    telephone = re.search(r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}', text)
            
    parsed_data = {
        "nom": nom,
        "email": email.group(0) if email else "Non trouvé",
        "telephone": telephone.group(0) if telephone else "Non trouvé",
        "competences": [],
        "experience": "Non trouvé",
        "diplome": "Non trouvé"
    }

    # --- 3. EXTRACTION DES COMPÉTENCES (MÉTHODE FIABLE) ---
    SKILL_KEYWORDS = [
        "python", "java", "javascript", "c++", "c#", "php", "ruby", "swift", "kotlin", "go", "rust",
        "sql", "nosql", "mongodb", "mysql", "postgresql", "oracle", "sql server", "pgadmin",
        "html", "css", "sass", "less", "react", "angular", "vue.js", "node.js", "express.js", "django", "flask",
        "git", "github", "gitlab", "docker", "kubernetes", "jenkins", "aws", "azure", "gcp",
        "linux", "windows", "ubuntu", "debian",
        "visual studio code", "vs code", "intellij idea", "eclipse", "postman", "figma", "canva", "lucidchart",
        "machine learning", "deep learning", "nlp", "intelligence artificielle", "ia", "data science", "data analysis",
        "neo4j"
    ]
    
    lower_text = text.lower()
    found_skills = set()
    for skill in SKILL_KEYWORDS:
        if re.search(r'\b' + re.escape(skill) + r'\b', lower_text):
            found_skills.add(skill.replace('_', ' ').title())
            
    parsed_data["competences"] = sorted(list(found_skills))

    # --- 4. Extraction des sections Expérience et Formation ---
    experience_headers = ['expérience', 'expériences', 'experience', 'experiences', 'parcours professionnel', 'expériences professionnelles']
    experience_stop_headers = ['formation', 'formations', 'education', 'éducation', 'diplôme', 'diplômes', 'compétences', 'skills', 'langues', 'centres d\'intérêt', 'projets']
    parsed_data["experience"] = _extract_section_text(text, experience_headers, experience_stop_headers)
    
    diplome_headers = ['formation', 'formations', 'education', 'éducation', 'diplôme', 'diplômes', 'parcours académique']
    diplome_stop_headers = ['expérience', 'expériences', 'experience', 'experiences', 'compétences', 'skills', 'langues', 'centres d\'intérêt', 'projets']
    parsed_data["diplome"] = _extract_section_text(text, diplome_headers, diplome_stop_headers)

    return parsed_data

def _extract_section_text(full_text, start_headers, stop_headers):
    lower_text = full_text.lower()
    start_index = -1
    found_header = ""
    for header in start_headers:
        start_index = lower_text.find(header)
        if start_index != -1:
            found_header = header
            break
            
    if start_index != -1:
        end_index = len(full_text)
        for stop_header in stop_headers:
            potential_end_index = lower_text.find(stop_header, start_index + len(found_header))
            if potential_end_index != -1 and potential_end_index < end_index:
                end_index = potential_end_index
        
        section_text = full_text[start_index:end_index]
        header_pos = section_text.lower().find(found_header)
        if header_pos != -1:
            section_text = section_text[header_pos + len(found_header):].strip()
        
        section_text = re.sub(r'\n\s*\n', '\n\n', section_text)
        
        return section_text if section_text else "Non trouvé"
    return "Non trouvé"

def calculate_score(parsed_data):
    score = 0
    if parsed_data.get("email") != "Non trouvé": score += 15
    if parsed_data.get("telephone") != "Non trouvé": score += 15
    if parsed_data.get("competences"): score += min(len(parsed_data["competences"]) * 2, 30)
    if parsed_data.get("experience") and parsed_data.get("experience") != "Non trouvé": score += 20
    if parsed_data.get("diplome") and parsed_data.get("diplome") != "Non trouvé": score += 20
    return min(score, 100)

def generate_pdf_report(parsed_data, score, filename):
    filepath = os.path.join(app.config['REPORTS_FOLDER'], filename)
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    style_normal = styles['Normal']
    style_normal.leading = 14 # Espacement entre les lignes

    story.append(Paragraph("Rapport d'Analyse de CV", styles['h1']))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Informations Générales</b>", styles['h2']))
    story.append(Paragraph(f"<b>Nom:</b> {parsed_data.get('nom', 'N/A')}", style_normal))
    story.append(Paragraph(f"<b>Email:</b> {parsed_data.get('email', 'N/A')}", style_normal))
    story.append(Paragraph(f"<b>Téléphone:</b> {parsed_data.get('telephone', 'N/A')}", style_normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Formation / Diplôme</b>", styles['h2']))
    story.append(Paragraph(parsed_data.get('diplome', 'N/A').replace('\n', '<br/>'), style_normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Expérience Professionnelle</b>", styles['h2']))
    story.append(Paragraph(parsed_data.get('experience', 'N/A').replace('\n', '<br/>'), style_normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph("<b>Compétences Détectées</b>", styles['h2']))
    for comp in parsed_data.get("competences", []):
        story.append(Paragraph(f"  - {comp}", style_normal))
    story.append(Spacer(1, 12))

    story.append(Paragraph(f"<b>Score de Complétude:</b> {score}/100", styles['h2']))

    doc.build(story)
    return filepath

# --- Routes de l'Application ---
@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['logged_in'] = True
            return redirect(url_for('upload'))
        else:
            error = 'Identifiants invalides. Veuillez réessayer.'
    return render_template('login.html', error=error)

@app.route('/upload')
def upload():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('upload.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    files = request.files.getlist('files')
    results = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)

            text = None
            try:
                if filename.endswith('.pdf'):
                    text = extract_text_from_pdf(file_path)
                elif filename.endswith('.docx'):
                    text = extract_text_from_docx(file_path)
                
                if text:
                    parsed_data = parse_cv(text)
                    score = calculate_score(parsed_data)
                    pdf_filename = f"rapport_{filename.rsplit('.', 1)[0]}.pdf"
                    generate_pdf_report(parsed_data, score, pdf_filename)
                    
                    results.append({
                        "filename": filename,
                        "parsed_data": parsed_data,
                        "score": score,
                        "pdf_report_url": url_for('download_pdf', filename=pdf_filename)
                    })
                else:
                    results.append({"filename": filename, "error": "Impossible d'extraire le texte du fichier."})

            except Exception as e:
                results.append({"filename": filename, "error": f"Une erreur est survenue lors de l'analyse: {e}"})
            
            finally:
                if os.path.exists(file_path):
                    os.remove(file_path)
        elif file.filename != '':
            results.append({"filename": file.filename, "error": "Type de fichier non autorisé."})

    session['analysis_results'] = results
    return redirect(url_for('show_results'))

@app.route('/results')
def show_results():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
        
    results = session.get('analysis_results', [])
    session.pop('analysis_results', None)
    return render_template('results.html', results=results)

@app.route('/download-pdf/<filename>')
def download_pdf(filename):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    try:
        return send_from_directory(app.config['REPORTS_FOLDER'], filename, as_attachment=True)
    except FileNotFoundError:
        return "Fichier non trouvé", 404

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)