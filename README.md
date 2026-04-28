# NutriMind AI – Smart Diet Planner

NutriMind AI is a clean, practical diet planner designed for everyday users, families, and fitness enthusiasts. It helps track nutrition, health goals, and progress with a simple, responsive interface.

## ✨ Features
- Secure login/signup with password hashing  
- Personalized BMI, calorie, water, and step targets  
- Allergy‑aware meal recommendations (Veg / Eggetarian / Non‑Veg)  
- Optional live recipe search via Spoonacular API  
- Daily tracking: steps, water, weight, and notes  
- Auto‑generated 7‑day health records for demo/presentation  
- Progress charts and tables  
- PDF report export  
- Responsive UI for desktop and mobile  

---

## 🚀 Getting Started

### 1. Open in VS Code
```bash
# Extract the project
# Open folder ai_diet_planner_vscode in VS Code
```

### 2. Create Virtual Environment
**Windows**
```bash
python -m venv .venv
.venv\Scripts\activate
```

**Mac / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Requirements
```bash
pip install -r requirements.txt
```

### 4. Run the App
```bash
python app.py
```
Open in browser:  
`http://127.0.0.1:5000`

Alternative port:
```bash
python -m flask --app app run --port 5001
```

---

## 🧪 Testing
Install dev dependencies:
```bash
pip install -r requirements-dev.txt
pytest
```

Covers signup/login, dashboard, meal generation, progress saving, PDF export, and AI rules.

---

## 🔑 Optional: Enable Recipe API
Set your Spoonacular API key as an environment variable:

**Windows PowerShell**
```powershell
$env:SPOONACULAR_API_KEY="your_api_key_here"
python app.py
```

**Mac / Linux**
```bash
export SPOONACULAR_API_KEY="your_api_key_here"
python app.py
```


# 📂 Project Structure
```
app.py              # Flask routes, database, PDF export
ai_engine.py        # Meal scoring & recommendation logic
templates/          # Jinja HTML pages
static/css/         # Styling
static/js/          # Step counter & UI behavior
tests/              # Automated tests
requirements.txt    # Runtime dependencies
requirements-dev.txt# Dev/test dependencies