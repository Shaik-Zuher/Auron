# 🏥 E-Pharmacy ML Web App

A machine learning-powered web application for symptom-based diagnosis and medicine recommendations.

---

## 🚀 Features

- Flask-based web interface
- Machine learning model for symptom-based prediction
- Automatic setup using `.bat` file
- Auto-generates `model.pkl` and `db_config.json` if missing

---

## 💻 How to Set Up and Run on a New Laptop

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Shaik-Zuher/Auron.git
cd Auron
2️⃣ Use the Batch File (Recommended on Windows)
Run:

bash
Copy code
setup_and_run.bat
This will:

Check MySQL installation

Ask for MySQL username/password (only once)

Save them securely in db_config.json

Create virtual environment if needed

Install required packages

Train the ML model if not already present

Start the Flask app

🛠 Manual Setup (Alternative)
✅ 1. Create and activate a virtual environment
bash
Copy code
python -m venv .venv
.\.venv\Scripts\activate   # Windows
source .venv/bin/activate  # Linux/Mac
✅ 2. Install requirements
bash
Copy code
pip install -r requirements.txt
✅ 3. Set up MySQL credentials
On first run, app.py will prompt for your MySQL username and password, then store them in db_config.json.

✅ 4. Train the model (only once)
bash
Copy code
python train_model.py
✅ 5. Run the app
bash
Copy code
flask run
⚙️ Database Configuration
We use a JSON file to store DB credentials. This keeps passwords out of the codebase.

File: db_config.json

Format:

json
Copy code
{
  "host": "localhost",
  "user": "your_mysql_username",
  "password": "your_mysql_password"
}
This file is automatically created the first time you run the app or .bat file.

✅ It is ignored by Git using .gitignore.

🧰 Troubleshooting
❌ MySQL not found
Error:

pgsql
Copy code
MySQL is not installed or not added to PATH!
Fix:

Install MySQL Server from https://dev.mysql.com/downloads/

Make sure mysql is added to your system PATH

❌ Missing db_config.json
Error:

vbnet
Copy code
FileNotFoundError: [Errno 2] No such file or directory: 'db_config.json'
Fix:

Just run app.py, and it will prompt you for DB credentials

Or delete the file and re-run to regenerate it

❌ model.pkl too large or missing
We do not commit model.pkl to GitHub (it's large).

If it's missing, the .bat file or train_model.py will recreate it.