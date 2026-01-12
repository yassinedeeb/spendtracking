from flask import Flask, request, jsonify
import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image
import json
import io

load_dotenv()

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'

gemini_api_key = os.getenv("GEMINI_API_KEY")
if not gemini_api_key:
    raise ValueError("No GEMINI_API_KEY found in environment variables")
genai.configure(api_key=gemini_api_key)

GEMINI_PROMPT = """
Analyze the following receipt image and extract the following information in a valid JSON format:
- "date": The date of the transaction (YYYY-MM-DD).
- "store_name": The name of the store.
- "items": A list of objects, where each object has "description" and "price".
- "total": The total amount of the receipt.

If any information is not available, use null.
"""

@app.route('/upload', methods=['POST'])
def upload_receipt():
    if 'receipt' not in request.files:
        return jsonify({'error': 'No receipt image provided'}), 400
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        generation_config = genai.types.GenerationConfig(response_mime_type="application/json")
        model = genai.GenerativeModel('gemini-pro-vision', generation_config=generation_config)

        # Open the image and convert it to a supported format (PNG) in memory
        try:
            img = Image.open(filepath)
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='PNG')
        except IOError:
            return jsonify({'error': 'Invalid image file provided'}), 400
        img_byte_arr = img_byte_arr.getvalue()

        # Create the content parts for the Gemini API
        image_part = {
            "mime_type": "image/png",
            "data": img_byte_arr
        }
        prompt_part = {
            "text": GEMINI_PROMPT
        }

        response = model.generate_content([prompt_part, image_part])

        # Clean up the response to extract the JSON part, making it more robust
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')

        try:
            parsed_data = json.loads(cleaned_response)
            return jsonify(parsed_data), 200
        except json.JSONDecodeError:
            return jsonify({'error': 'Failed to parse receipt data from Gemini response', 'raw_response': response.text}), 500


@app.route('/save', methods=['POST'])
def save_receipt():
    data = request.get_json()
    store_name = data.get('store_name')
    date = data.get('date')
    total = float(data.get('total', 0))
    items = data.get('items')
    category_name = data.get('category')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    try:
        # Insert receipt
        cursor.execute("INSERT INTO receipts (store_name, date, total) VALUES (?, ?, ?)", (store_name, date, total))
        receipt_id = cursor.lastrowid

        # Insert items
        if items:
            for item in items:
                price = float(item.get('price', 0))
                cursor.execute("INSERT INTO items (receipt_id, description, price) VALUES (?, ?, ?)",
                               (receipt_id, item.get('description'), price))

        # Handle category
        if category_name:
            cursor.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category_name,))
            cursor.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
            category_id = cursor.fetchone()[0]
            cursor.execute("INSERT INTO receipt_categories (receipt_id, category_id) VALUES (?, ?)", (receipt_id, category_id))

        conn.commit()
        return jsonify({'message': 'Receipt saved successfully', 'receipt_id': receipt_id}), 201
    except sqlite3.Error as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


@app.route('/api/spending', methods=['GET'])
def get_spending():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT strftime('%Y-%m', date) as month, SUM(total) as total_spending
            FROM receipts
            GROUP BY month
            ORDER BY month
        """)
        rows = cursor.fetchall()

        spending_data = {row[0]: row[1] for row in rows}

        return jsonify(spending_data)
    except sqlite3.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()


def init_db():
    conn = sqlite3.connect('database.db')
    print("Opened database successfully")

    conn.execute('''
    CREATE TABLE IF NOT EXISTS receipts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        total REAL,
        store_name TEXT
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        receipt_id INTEGER,
        description TEXT,
        price REAL,
        FOREIGN KEY(receipt_id) REFERENCES receipts(id)
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE
    );
    ''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS receipt_categories (
        receipt_id INTEGER,
        category_id INTEGER,
        FOREIGN KEY(receipt_id) REFERENCES receipts(id),
        FOREIGN KEY(category_id) REFERENCES categories(id)
    );
    ''')

    print("Tables created successfully")
    conn.close()

if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    init_db()
    app.run(debug=True)
