# 📄 Parseur de CV FR/AR – Extraction Automatique d’Informations

## 👩‍💻 Présentation du Projet

Ce projet est une application web développée en **Python (Flask)** permettant d’analyser automatiquement des CV en format PDF (Français / Arabe) et d’extraire les informations importantes telles que :

* 📧 Email
* 📱 Numéro de téléphone
* 💡 Compétences

L’objectif principal est d’automatiser le processus de lecture des CV afin de faciliter le travail des recruteurs et des entreprises.

---

## 🎯 Objectifs du Projet

* Extraire automatiquement les informations depuis un CV PDF
* Supporter les CV en Français et en Arabe
* Identifier les compétences techniques
* Offrir une interface web simple et intuitive
* Préparer une base pour une future amélioration avec NLP (Traitement du Langage Naturel)

---

## 🛠️ Technologies Utilisées

* **Python 3**
* **Flask** (Framework Web)
* **pdfplumber** (Extraction de texte depuis PDF)
* **HTML5**
* **CSS3**
* **Regex (Expressions régulières)** pour l’extraction des emails et téléphones

---

## 📂 Structure du Projet

```
cv_parser_project/
│
├── app.py
├── templates/
│     └── index.html
├── static/
│     └── style.css
└── uploads/
```

---

## ⚙️ Installation et Exécution

### 1️⃣ Cloner le projet

```
git clone <lien_du_repo>
```

### 2️⃣ Installer les dépendances

```
pip install flask pdfplumber
```

### 3️⃣ Lancer l’application

```
python app.py
```

### 4️⃣ Ouvrir dans le navigateur

```
http://127.0.0.1:5000/
```

---

## 🔍 Fonctionnement

1. L’utilisateur télécharge un CV en format PDF.
2. Le système extrait le texte du fichier.
3. Des expressions régulières sont utilisées pour détecter :

   * Email
   * Numéro de télé
