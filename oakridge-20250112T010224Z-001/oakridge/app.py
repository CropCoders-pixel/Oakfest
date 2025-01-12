from flask import Flask, render_template, request, jsonify, session
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # To store session data

# Function to initialize the SQLite database
def init_db():
    with sqlite3.connect("waste_management.db") as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS waste_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        waste_type TEXT,
                        quantity REAL,
                        points REAL)''')
        conn.commit()

# Route to get the total data (quantity and points) and leaderboard
@app.route('/')
def index():
    # Fetch total quantity and points from the database
    total_quantity = 0
    total_points = 0
    leaderboard = []

    with sqlite3.connect("waste_management.db") as conn:
        c = conn.cursor()
        c.execute("SELECT quantity, points FROM waste_data")
        rows = c.fetchall()
        for row in rows:
            total_quantity += row[0]
            total_points += row[1]
        
        c.execute("SELECT waste_type, quantity, points FROM waste_data ORDER BY points DESC")
        leaderboard = c.fetchall()

    # Store total data in session
    session['total_quantity'] = total_quantity
    session['total_points'] = total_points

    return render_template("waste_management.html", total_quantity=total_quantity, total_points=total_points, leaderboard=leaderboard)

# Route to handle waste submission
@app.route('/submit_waste', methods=['POST'])
def submit_waste():
    waste_type = request.form['wasteType']
    quantity = float(request.form['quantity'])
    unit = request.form['unit']
    
    # Convert to kg
    if unit == 'g':
        quantity /= 1000
    elif unit == 'lb':
        quantity *= 0.453592

    # Points logic
    if waste_type == 'metal':
        points = quantity * 510
    elif waste_type == 'organic':
        points = quantity * 5
    elif waste_type == 'plastic':
        points = quantity * 15  # You can change it to 20 if needed
    else:
        points = 0

    # Save to database
    with sqlite3.connect("waste_management.db") as conn:
        c = conn.cursor()
        c.execute("INSERT INTO waste_data (waste_type, quantity, points) VALUES (?, ?, ?)", 
                  (waste_type, quantity, points))
        conn.commit()

    # Update total quantity and points in session
    session['total_quantity'] += quantity
    session['total_points'] += points

    # Fetch updated leaderboard
    leaderboard = []
    with sqlite3.connect("waste_management.db") as conn:
        c = conn.cursor()
        c.execute("SELECT waste_type, quantity, points FROM waste_data ORDER BY points DESC")
        leaderboard = c.fetchall()

    return jsonify({
        'type': waste_type,
        'quantity': quantity,
        'points': points,
        'total_quantity': session['total_quantity'],
        'total_points': session['total_points'],
        'leaderboard': leaderboard
    })

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
