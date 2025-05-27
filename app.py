from flask import Flask, render_template, request, redirect, url_for, abort
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Database initialization with quantity support
def init_db():
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    
    # Create table with new quantity fields
    c.execute('''
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            expiry_date DATE NOT NULL,
            added_date DATE NOT NULL,
            quantity REAL NOT NULL,
            quantity_unit TEXT NOT NULL CHECK(quantity_unit IN ('g', 'kg', 'ml', 'L', 'items')),
            place TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Migration for existing databases
def migrate_db():
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    
    try:
        # Check if columns exist
        c.execute("PRAGMA table_info(foods)")
        columns = [col[1] for col in c.fetchall()]
        
        if 'quantity' not in columns:
            # Add new columns with default values
            c.execute("ALTER TABLE foods ADD COLUMN quantity REAL DEFAULT 1.0")
            c.execute("ALTER TABLE foods ADD COLUMN quantity_unit TEXT DEFAULT 'items'")
            conn.commit()
    except sqlite3.Error as e:
        print(f"Migration error: {e}")
    finally:
        conn.close()

# Initialize database with migration
migrate_db()
init_db()

@app.route('/')
def index():
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    
    filter_type = request.args.get('filter', 'all')
    
    if filter_type == 'expired':
        c.execute("SELECT * FROM foods WHERE expiry_date < date('now') ORDER BY expiry_date")
    elif filter_type == 'expiring_soon':
        c.execute("SELECT * FROM foods WHERE expiry_date BETWEEN date('now') AND date('now', '+7 days') ORDER BY expiry_date")
    elif filter_type == 'safe':
        c.execute("SELECT * FROM foods WHERE expiry_date > date('now', '+7 days') ORDER BY expiry_date")
    else:
        c.execute("SELECT * FROM foods ORDER BY expiry_date")
    
    foods = c.fetchall()
    conn.close()
    
    food_list = []
    for food in foods:
        expiry_date = datetime.strptime(food[2], '%Y-%m-%d').date()
        days_left = (expiry_date - datetime.now().date()).days
        status = "safe"
        if days_left < 0:
            status = "expired"
        elif days_left <= 7:
            status = "expiring soon"
            
        food_list.append({
            'id': food[0],
            'name': food[1],
            'expiry_date': food[2],
            'added_date': food[3],
            'quantity': food[4],
            'quantity_unit': food[5],
            'status': status,
            'days_left': days_left,
            'place': food[6]
        })
    
    return render_template('index.html', 
                         foods=food_list, 
                         current_filter=filter_type)

@app.route('/add', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        name = request.form['name']
        expiry_date = request.form['expiry_date']
        quantity = float(request.form.get('quantity', 1))
        quantity_unit = request.form.get('quantity_unit', 'items')
        added_date = datetime.now().strftime('%Y-%m-%d')
        place = request.form['place']

        conn = sqlite3.connect('food.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO foods 
            (name, expiry_date, added_date, quantity, quantity_unit, place) 
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, expiry_date, added_date, quantity, quantity_unit, place))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    return render_template('add_food.html')

@app.route('/edit/<int:food_id>', methods=['GET', 'POST'])
def edit_food(food_id):
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    
    if request.method == 'POST':
        name = request.form['name']
        expiry_date = request.form['expiry_date']
        quantity = float(request.form['quantity'])
        quantity_unit = request.form['quantity_unit']
        place = request.form['place']
        
        c.execute('''
            UPDATE foods 
            SET name=?, expiry_date=?, quantity=?, quantity_unit=?, place=?
            WHERE id=?
        ''', (name, expiry_date, quantity, quantity_unit, place, food_id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    
    c.execute("SELECT * FROM foods WHERE id=?", (food_id,))
    food = c.fetchone()
    conn.close()
    
    if not food:
        abort(404)
        
    return render_template('edit_food.html', food={
        'id': food[0],
        'name': food[1],
        'expiry_date': food[2],
        'quantity': food[4],
        'quantity_unit': food[5],
        'place':food[6]
    })

@app.route('/delete/<int:food_id>')
def delete_food(food_id):
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    c.execute("DELETE FROM foods WHERE id = ?", (food_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
