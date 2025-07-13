import joblib
import mysql.connector
import requests 
import wikipediaapi
from flask import Flask,flash, request, render_template, redirect, url_for, session
import socket
import json
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Change this to a secure key

# Load the trained model
model = joblib.load('model.pkl')

CONFIG_FILE = "db_config.json"

# If config file doesn't exist, prompt user to create it
if not os.path.exists(CONFIG_FILE):
    print("Database config not found.")

    user = input("Enter your MySQL username: ")
    password = input("Enter your MySQL password: ")

    db_config = {
        "host": "localhost",
        "user": user,
        "password": password
    }

    with open(CONFIG_FILE, "w") as f:
        json.dump(db_config, f, indent=4)

    print("✅ Saved database config to db_config.json")
else:
    with open(CONFIG_FILE, "r") as f:
        db_config = json.load(f)


def get_db_connection():
    return mysql.connector.connect(**db_config)

# Function to create the database and tables if they don't exist
def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("CREATE DATABASE IF NOT EXISTS epharma")
    cursor.close()
    conn.close()
    
    db_config["database"] = "epharma"
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            security_question VARCHAR(255) NOT NULL
        );
    """)

    conn.commit()
    cursor.close()
    conn.close()

initialize_database()

def check_internet_connection():
    """
    Check if there is an active internet connection
    Returns True if connected, False otherwise
    """
    try:
        # Try connecting to Google's DNS server
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return True
    except (socket.timeout, socket.error):
        return False


def get_wikimedia_image(medicine_name):
    """
    Fetch the most relevant medicine or molecular structure image from Wikimedia.
    """
    if not check_internet_connection():
        return None
        
    try:
        # Try multiple search patterns for better image retrieval
        search_patterns = [
            f"{medicine_name}",
            f"{medicine_name}_tablet",
            f"{medicine_name}_pill",
            f"{medicine_name}_drug",
            f"{medicine_name}_medicine"
        ]
        
        for pattern in search_patterns:
            pattern = pattern.replace(" ", "_")
            search_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={pattern}&srnamespace=6&origin=*"
            
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                search_results = data.get("query", {}).get("search", [])
                
                if search_results:
                    # Get the first image result
                    first_result = search_results[0]["title"]
                    # Extract just the filename portion from the title
                    filename = first_result.split(":", 1)[1] if ":" in first_result else first_result
                    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename.replace(' ', '_')}"
    except (requests.RequestException, ValueError, KeyError):
        return None
    
    return None  # If no image found, return None

def get_molecular_structure(medicine_name):
    """
    Fetch molecular structure image if no medicine image is found.
    """
    if not check_internet_connection():
        return None
        
    try:
        search_terms = [
            f"{medicine_name} chemical structure",
            f"{medicine_name} molecular structure",
            f"{medicine_name} molecule"
        ]
        
        for term in search_terms:
            search_url = f"https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch={term}&srnamespace=6&origin=*"
            
            response = requests.get(search_url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                search_results = data.get("query", {}).get("search", [])
                
                if search_results:
                    # Get the first image result
                    first_result = search_results[0]["title"]
                    # Extract just the filename portion from the title
                    filename = first_result.split(":", 1)[1] if ":" in first_result else first_result
                    return f"https://commons.wikimedia.org/wiki/Special:FilePath/{filename.replace(' ', '_')}"
    except (requests.RequestException, ValueError, KeyError):
        return None
    
    # If no molecular structure found, try another API as fallback
    try:
        # Try PubChem as a fallback
        pubchem_url = f"https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{medicine_name}/PNG"
        response = requests.get(pubchem_url, timeout=5)
        if response.status_code == 200:
            return pubchem_url
    except:
        pass
        
    return None

def get_medicine_symptoms(medicine_name):
    """
    Fetch symptoms related to a medicine from Wikipedia.
    """
    if not check_internet_connection():
        return "Internet connection is required to fetch symptoms information."
        
    try:
        user_agent = "ePharmaBot/1.0 (contact: your-email@example.com)"  # Set your own user-agent
        wiki_wiki = wikipediaapi.Wikipedia(language='en', user_agent=user_agent)
        
        page = wiki_wiki.page(medicine_name)

        if page.exists():
            summary = page.summary
            sentences = summary.split(". ")  # Split into sentences
            
            # If we only have random data, return an error message
            if len(sentences) < 2 or "medicine" in summary.lower():
                return "Did you enter correct Medicine? Because no symptoms found for this medicine."
            
            # Return first 2 sentences or summary if it's meaningful
            return ". ".join(sentences[:2]) + "."  # First 2 sentences
    except Exception:
        return "Failed to fetch symptoms. Please check your internet connection."

    return "Did you enter correct Medicine? Because no symptoms found for this medicine."

@app.route('/', methods=['GET'])
def home():
    """ Redirect to login page by default """
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cursor.fetchone()

        cursor.close()
        conn.close()

        if user:
            session['user'] = username
            return redirect(url_for('main_page'))
        else:
            flash("Invalid username or password", "login-msg")
            session['show_modal'] = True
            return redirect(url_for('login'))

    show_modal = session.pop('show_modal', False)
    return render_template('login.html', show_modal=show_modal)

@app.route('/reset_password', methods=['POST'])
def reset_password():
    username = request.form['reset_username'].strip()
    answer = request.form['reset_answer'].strip()
    new_password = request.form['new_password'].strip()

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Debug: List all users
    cursor.execute("SELECT username FROM users")
    all_users = cursor.fetchall()

    # Case-insensitive match
    cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(%s)", (username,))
    user = cursor.fetchone()

    if not user:
        flash("Username not found", "forgot-msg")
        cursor.close()
        conn.close()
        return render_template("login.html", forgot_dialog=True)

    if user['security_question'].strip().lower() != answer.lower():
        flash("Security answer incorrect", "forgot-msg")
        cursor.close()
        conn.close()
        return render_template("login.html", forgot_dialog=True)

    cursor.execute("UPDATE users SET password = %s WHERE username = %s", (new_password, user['username']))
    conn.commit()
    flash("Password reset successful!", "success")

    cursor.close()
    conn.close()
    return render_template("login.html", show_modal=True)



#signup.html route
@app.route('/signup_page', methods=['GET', 'POST'])
def signup_page():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        security=request.form["forget"].strip()
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user:
            cursor.close()
            conn.close()
            return render_template('signup.html', error="Username already exists!")

        cursor.execute("INSERT INTO users (username, password, security_question) VALUES (%s, %s, %s)", (username, password, security))
        conn.commit()

        cursor.close()
        conn.close()

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

#index.html route

@app.route('/main_page', methods=['GET', 'POST'])
def main_page():
    """ Allow access to index even if the user is not logged in """
    if request.method == 'POST':
        try:
            age = request.form.get('age')
            gender = request.form.get('Gender')
            symptoms = request.form.get('symptoms', '').strip()

            # Check if age and symptoms are provided
            if not age or not symptoms:
                flash("Please provide valid inputs.")
                return redirect(url_for('main_page'))

            # Split and clean up symptom list
            symptom_list = [sym.strip() for sym in symptoms.split(",") if sym.strip()]
            
            # Validate number of symptoms
            if len(symptom_list) < 1 or len(symptom_list) > 3:
                flash("Please enter 1 to 3 symptoms.")
                return redirect(url_for('main_page'))

            # Validate each symptom using the updated get_medicine_symptoms function
            invalid_symptoms = []
            for symptom in symptom_list:
                result = get_medicine_symptoms(symptom)
                if result == "Did you enter correct Medicine? Because no symptoms found for this medicine.":
                    invalid_symptoms.append(symptom)

            if invalid_symptoms:
                invalid_symptom_str = ', '.join(invalid_symptoms)
                flash(f"Invalid symptoms: {invalid_symptom_str}")
                return redirect(url_for('main_page'))

            # Proceed with model prediction if symptoms are valid
            symptom_string = ' '.join(symptom.lower() for symptom in symptom_list)
            while len(symptom_list) < 3:
                symptom_list.append("null")
            symptom_string = ' '.join(symptom_list[:3])
            prediction = model.predict([symptom_string])
            medicine = prediction[0]

            # Check if internet is available
            internet_available = check_internet_connection()
            medicine_image = None

            # Only try to fetch images if internet is available
            if internet_available:
                # Try fetching a real medicine image
                medicine_image = get_wikimedia_image(medicine.replace(" ", "_"))
                # If no medicine image found, fallback to molecular structure
                if not medicine_image:
                    medicine_image = get_molecular_structure(medicine.replace(" ", "_"))

            # Pass the results to result page
            return redirect(url_for('result_page', 
                                   gender=gender, 
                                   age=age, 
                                   symptoms=symptoms, 
                                   medicine=medicine, 
                                   medicine_image=medicine_image,
                                   internet_available=internet_available))

        except ValueError:
            flash("Please enter valid data for age.")
            return redirect(url_for('main_page'))

    # Return the index page if GET request or no error
    return render_template('index.html', user=session.get('user'))

@app.route('/search_medicine', methods=['GET', 'POST'])
def search_medicine():
    symptoms = None
    medicine_name = None
    internet_available = check_internet_connection()

    if request.method == 'POST':
        if 'symptoms' in request.form:  # Symptom search form
            symptoms = request.form.get('symptoms', '').strip()
            if symptoms:
                return main_page()
        elif 'medicine' in request.form:  # Medicine search form
            medicine_name = request.form.get('medicine', '').strip()
            if medicine_name:
                if internet_available:
                    symptoms = get_medicine_symptoms(medicine_name)
                else:
                    symptoms = "Internet connection is required to fetch symptoms information."

    return render_template('index.html', 
                          medicine=medicine_name, 
                          symptoms=symptoms, 
                          internet_available=internet_available)

@app.after_request
def no_cache(response):
    response.cache_control.no_store = True  # Disable caching for form pages
    response.cache_control.no_cache = True
    response.cache_control.must_revalidate = True
    return response

@app.route('/result_page')
def result_page():
    return render_template('results.html', 
                           gender=request.args.get('gender'), 
                           age=request.args.get('age'), 
                           symptoms=request.args.get('symptoms'),
                           medicine=request.args.get('medicine'),
                           medicine_image=request.args.get('medicine_image'),
                           internet_available=request.args.get('internet_available'))

#Route for cpr as I am using url_for('guide1') insted of direct "cpr.html"
@app.route("/guide1")
def guide1():
    return render_template("first_aid/cpr.html")

#guide 2-snake_bite
@app.route("/guide2")
def guide2():
    return render_template("first_aid/snake_bites.html")
#guide3-fire_accidents
@app.route("/guide3")
def guide3():
    return render_template("first_aid/fire_accidents.html")
#guide4-electric_shocks
@app.route("/guide4")
def guide4():
    return render_template("first_aid/electric_shocks.html")

if __name__ == "__main__":
    app.run(debug=True)
