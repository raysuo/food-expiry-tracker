from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
import sqlite3

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('food.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS foods
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 name TEXT NOT NULL,
                 expiry_date DATE NOT NULL,
                 added_date DATE NOT NULL,
                 place TEXT NOT NULL)''')
    conn.commit()
    conn.close()

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
            'place': food[4],
            'expiry_date': food[2],
            'added_date': food[3],
            'status': status,
            'days_left': days_left
        })
    
    return render_template('index.html', foods=food_list, current_filter=filter_type)

@app.route('/add', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        name = request.form['name']
        expiry_date = request.form['expiry_date']
        added_date = datetime.now().strftime('%Y-%m-%d')
        place = request.form['place']
        
        conn = sqlite3.connect('food.db')
        c = conn.cursor()
        c.execute("INSERT INTO foods (name, expiry_date, added_date, place) VALUES (?, ?, ?, ?)",
                  (name, expiry_date, added_date, place))
        conn.commit()
        conn.close()
        
        return redirect(url_for('index'))
    
    return render_template('add_food.html')

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
    #app.run(debug=True)