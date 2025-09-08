# app.py
import os
import datetime
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from io import BytesIO
from pdfminer.high_level import extract_text
import ollama
from pymongo import MongoClient

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev_secret')
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# ✅ MongoDB setup
client = MongoClient("mongodb://localhost:27017/")
db = client['rbac_chatbot']
users_col = db['users']
pdfs_col = db['pdfs']
qa_col = db['interactions']

# ✅ RBAC: Only manager & employee
ROLE_HIERARCHY = {"manager": 2, "employee": 1}

@app.route('/')
def index():
    return redirect(url_for('login')) if 'username' not in session else render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # If no one is logged in -> create Manager
    if 'username' not in session:
        if request.method == 'POST':
            u = request.form['username']
            p = request.form['password']
            existing_user = users_col.find_one({'username': u})

            if existing_user:
                return render_template('signup.html', message="Username already exists!")

            users_col.insert_one({
                'username': u,
                'password': p,
                'role': 'manager'
            })

            return redirect(url_for('login'))  # ✅ redirect to login after manager signup

        return render_template('signup.html')

    # If a manager is logged in -> create Employee
    elif session['role'] == 'manager':
        if request.method == 'POST':
            u = request.form['username']
            p = request.form['password']
            existing_user = users_col.find_one({'username': u})

            if existing_user:
                return render_template('signup.html', message="Username already exists!")

            users_col.insert_one({
                'username': u,
                'password': p,
                'role': 'employee',
                'manager': session['username']
            })

            return redirect(url_for('login'))  # ✅ employee also goes to login

        return render_template('signup.html')

    # Employees cannot access signup
    else:
        return redirect(url_for('index'))




@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        u, p = request.form['username'], request.form['password']
        user = users_col.find_one({'username': u, 'password': p})
        if user:
            session['username'] = u
            session['role'] = user['role']
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'username' not in session or session['role'] != 'manager':
        return jsonify(message="Only managers can upload PDFs."), 403

    file = request.files.get('pdfFile')
    if not file or not file.filename.endswith('.pdf'):
        return jsonify(message="Invalid file"), 400

    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        file.seek(0)
        file.save(filepath)

        with open(filepath, 'rb') as f:
            text = extract_text(f)

        pdfs_col.insert_one({
            'filename': filename,
            'owner': session['username'],
            'owner_role': session['role'],
            'text': text
        })

        return jsonify(message="File uploaded and saved successfully.")

    except Exception as e:
        print("Upload error:", e)
        return jsonify(message="Failed to process PDF."), 500

@app.route('/ask', methods=['POST'])
def ask():
    if 'username' not in session:
        return jsonify(answer="Unauthorized"), 401

    question = request.json.get('question')
    username = session['username']
    role = session['role']

    # 🔹 Step 1: Check if the same Q&A already exists in DB for this user
    existing = qa_col.find_one({
        'username': username,
        'question': question.lower().strip()
    })
    if existing:
        return jsonify(answer=existing['answer'], source="db")

    # 🔹 Step 2: Collect accessible documents
    accessible_docs = list(pdfs_col.find())
    accessible_text = []
    used_filenames = []

    for doc in accessible_docs:
        doc_owner = doc.get('owner')
        doc_role = doc.get('owner_role')
        if not doc_owner or not doc_role:
            continue

        if role == 'manager' and doc_owner == username:
            accessible_text.append(f"From {doc['filename']}:\n{doc['text']}")
            used_filenames.append(doc['filename'])

        elif role == 'employee':
            user = users_col.find_one({'username': username})
            manager = user.get('manager') if user else None
            if manager and doc_owner == manager:
                accessible_text.append(f"From {doc['filename']}:\n{doc['text']}")
                used_filenames.append(doc['filename'])

    if not accessible_text:
        return jsonify(answer="No accessible documents available.")

    # 🔹 Step 3: Build prompt
    prompt = (
    "You are a document assistant chatbot. Use ONLY the content from these documents to answer.\n"
    "If the answer is not found word-for-word or clearly from the documents, reply exactly:\n"
    "'No relevant answer found in your accessible documents.'\n\n"
    "Give the answer in 2–4 short bullet points only.\n\n"
    f"Question: {question}\n\nDocuments:\n" + "\n\n".join(accessible_text)
)


    try:
        # 🔹 Step 4: Call Ollama
        response = ollama.chat(
            model='gemma:2b',
            messages=[
                {"role": "system", "content": "You are a helpful PDF assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        answer = response['message']['content'].strip()

        # 🔹 Step 5: Store Q&A in DB for caching
        qa_col.insert_one({
            'username': username,
            'question': question.lower().strip(),
            'answer': answer,
            'pdfs_used': used_filenames,
            'timestamp': datetime.datetime.now()
        })

        return jsonify(answer=answer, source="llm")

    except Exception as e:
        print("Ollama error:", e)
        return jsonify(answer="Error processing your request using Ollama."), 500

@app.route('/history')
def history():
    if 'username' not in session:
        return redirect(url_for('login'))

    logs = qa_col.find({'username': session['username']}).sort('timestamp', -1)
    return render_template('history.html', logs=logs)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
    
