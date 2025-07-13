# How to Set Up and Run

## 1.Follow any one of options.

### A.Clone the Repository

```bash
git clone https://github.com/Shaik-Zuher/Auron.git
cd Auron
```
Clone this in the location you want.
### B.Download Zip File

Download zip file from green code bar on top right side and extract it.

## 2.Follow Any one of following.
### A.Use the Batch File (Recommended on Windows)

Click run_server.bat in in folder directory.
```bash
This will:

Check MySQL installation

Ask for MySQL username/password (only once)

Save them securely in db_config.json

Create virtual environment if needed

Install required packages

Train the ML model if not already present

Start the Flask app
```

### B. Manual Setup (Alternative)

Open VScode or bash

 1.Create and activate a virtual environment
```bash
    python -m venv .venv
    .\.venv\Scripts\activate   # Windows
    source .venv/bin/activate  # Linux/Mac
```
2.Install requirements
```bash
pip install -r requirements.txt
```
3.Set up MySQL credentials
On first run, app.py will prompt for your MySQL username and password, then store them in db_config.json.

4.Train the model (only once)
 Run the train_model.py in model folder

5.Run the app
```bash
flask run
```
## Database Configuration
 We use a JSON file to store DB credentials. This keeps passwords out of the codebase.

 File: db_config.json

Format:

``` bash
json
    {
    "host": "localhost",
    "user": "your_mysql_username",
    "password": "your_mysql_password"
    }
```
This file is automatically created the first time you run the app or .bat file.

It is ignored by Git using .gitignore.

# Troubleshooting
## 1.MySQL not found

Error:

``` bash
pgsql

MySQL is not installed or not added to PATH!
```
Fix:

Install MySQL Server from https://dev.mysql.com/downloads/

Make sure mysql is added to your system PATH

## 2.Missing db_config.json

Error:

```bash
FileNotFoundError: [Errno 2] No such file or directory: 'db_config.json'
```

Fix:

Just run app.py, and it will prompt you for DB credentials

Or delete the file and re-run to regenerate it

## 3.model.pkl too large or missing
We do not commit model.pkl to GitHub (it's large).

If it's missing, the .bat file or train_model.py will recreate it.