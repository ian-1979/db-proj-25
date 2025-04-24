# Note: right now functions are NOT implemented how we wrote them for our second
#       deliverable in the SQL queries part. Need to change.


#! /usr/bin/python3
from flask import Flask, render_template, request, redirect
from flask_mysqldb import MySQL

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update if your phpMyAdmin user is different
app.config['MYSQL_PASSWORD'] = ''  # Enter your MySQL/phpMyAdmin password here
app.config['MYSQL_DB'] = 'dnd_database'  # Change if you named it differently

mysql = MySQL(app)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# View all notecards
@app.route('/notecards')
def show_notecards():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, name, type, text FROM notecard")
    data = cursor.fetchall()
    cursor.close()
    return render_template('notecards.html', data=data)

# Search notecards by name or type
@app.route('/notecardsearch', methods=['GET', 'POST'])
def notecard_search():
    if request.method == 'GET':
        return render_template('notecardsearch.html')
    if request.method == 'POST':
        name = request.form.get('name', '')
        note_type = request.form.get('type', '')
        cursor = mysql.connection.cursor()
        query = "SELECT id, name, type, text FROM notecard WHERE name LIKE %s OR type = %s"
        cursor.execute(query, [f"%{name}%", note_type])
        data = cursor.fetchall()
        cursor.close()
        return render_template('notecards.html', data=data)

# Create a new notecard
@app.route('/newnotecard', methods=['GET', 'POST'])
def new_notecard():
    if request.method == 'GET':
        return render_template('newnotecard.html')
    if request.method == 'POST':
        name = request.form['name']
        note_type = request.form['type']
        text = request.form['text']
        campaign_id = request.form['campaign_id']
        public = int(request.form.get('public', 0))
        note_image_path = None  # Optional: add support for image upload later
        cursor = mysql.connection.cursor()
        cursor.execute("""
            INSERT INTO notecard (name, type, text, campaign_id, public, note_image_path)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, note_type, text, campaign_id, public, note_image_path))
        mysql.connection.commit()
        cursor.close()
        return redirect('/notecards')

if __name__ == '__main__':
    app.run(debug=True)
