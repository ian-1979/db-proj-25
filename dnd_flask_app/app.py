# Note: right now functions are NOT implemented how we wrote them for our second
#       deliverable in the SQL queries part. Need to change.

import os
#! /usr/bin/python3
from flask import Flask, render_template, request, redirect, session, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')

app.secret_key = 'your_secret_key_here'  # Make this a random string in production

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Update if your phpMyAdmin user is different
app.config['MYSQL_PASSWORD'] = ''  # Enter your MySQL/phpMyAdmin password here
app.config['MYSQL_DB'] = 'dbdatabase1'  # Change if you named it differently

mysql = MySQL(app)

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# View all notecards
@app.route('/notecards')
def show_notecards():
    if 'campaign_id' not in session:
        return redirect('/selectcampaign')

    cursor = mysql.connection.cursor()
    if session.get('campaign_role') == 'dm':
        cursor.execute("""
            SELECT id, name, type, text, note_image_path
            FROM notecard
            WHERE campaign_id = %s
        """, (session['campaign_id'],))
    else:
        cursor.execute("""
            SELECT id, name, type, text, note_image_path
            FROM notecard
            WHERE campaign_id = %s AND public = 1
        """, (session['campaign_id'],))

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


#edit notecard route
@app.route('/editnotecard/<int:notecard_id>', methods=['GET', 'POST'])
def edit_notecard(notecard_id):
    if 'campaign_id' not in session:
        return redirect('/selectcampaign')
    if session.get('campaign_role') != 'dm':
        return "Only DMs can edit notecards.", 403

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, name, type, text, note_image_path
        FROM notecard
        WHERE id = %s AND campaign_id = %s
    """, (notecard_id, session['campaign_id']))
    card = cursor.fetchone()
    cursor.close()

    if not card:
        return "Notecard not found.", 404

    if request.method == 'POST':
        # Handle form updates (I'll expand this in next message if you want)

        pass  # Placeholder: form handling will go here!

    return render_template('editnotecard.html', card=card, extra=extra)



@app.route('/deletenotecard/<int:notecard_id>')
def delete_notecard(notecard_id):
    if 'campaign_id' not in session:
        return redirect('/selectcampaign')
    if session.get('campaign_role') != 'dm':
        return "Only DMs can delete notecards.", 403

    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM notecard WHERE id = %s AND campaign_id = %s", (notecard_id, session['campaign_id']))
    mysql.connection.commit()
    cursor.close()

    return redirect('/notecards')

    return render_template('editnotecard.html', card=card)



#login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, username, password, profile_image_path FROM user WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()

        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['profile_image_path'] = user[3]
            # Later: add role field here when it's in the table
            return redirect(url_for('index'))
        else:
            return "Invalid username or password", 401

    return render_template('login.html')

#register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)

        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password_hash))
        mysql.connection.commit()
        cursor.close()

        return redirect('/login')

    return render_template('register.html')




#select campaign route
@app.route('/selectcampaign', methods=['GET', 'POST'])
def selectcampaign():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT c.id, c.name, c.description
        FROM campaign c
        JOIN user_campaign uc ON c.id = uc.campaign_id
        WHERE uc.user_id = %s
    """, (session['user_id'],))
    campaigns = cursor.fetchall()
    cursor.close()

    if request.method == 'POST':
        selected_campaign = request.form['campaign_id']
        # Make sure user has access
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT role FROM user_campaign 
            WHERE user_id = %s AND campaign_id = %s
        """, (session['user_id'], selected_campaign))
        access = cursor.fetchone()
        cursor.close()
        if access:
            session['campaign_id'] = selected_campaign
            session['campaign_role'] = access[0]
            return redirect('/notecards')
        else:
            return "Access denied", 403

    return render_template('selectcampaign.html', campaigns=campaigns)

    
@app.route('/campaigns', methods=['GET', 'POST'])
def campaigns():
    if 'user_id' not in session:
        return redirect('/login')

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        cursor.execute("INSERT INTO campaign (name, description) VALUES (%s, %s)", (name, description))
        campaign_id = cursor.lastrowid
        cursor.execute("INSERT INTO user_campaign (user_id, campaign_id, role) VALUES (%s, %s, 'dm')", (session['user_id'], campaign_id))
        mysql.connection.commit()
        cursor.close()
        return redirect('/campaigns')

    cursor.execute("""
        SELECT c.id, c.name, c.description
        FROM campaign c
        JOIN user_campaign uc ON c.id = uc.campaign_id
        WHERE uc.user_id = %s
    """, (session['user_id'],))
    campaigns = cursor.fetchall()
    cursor.close()

    return render_template('campaigns.html', campaigns=campaigns)




#logout route
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/newnotecard', methods=['GET', 'POST'])
def new_notecard():
    if 'campaign_id' not in session:
        return redirect('/selectcampaign')
    if session.get('campaign_role') != 'dm':
        return "Only DMs can create notecards.", 403

    if request.method == 'GET':
        return render_template('newnotecard.html')

    if request.method == 'POST':
        name = request.form['name']
        note_type = request.form['type']
        text = request.form['text']
        campaign_id = session['campaign_id']
        public = int(request.form.get('public', 0))

        # Handle image upload
        image = request.files.get('image')
        note_image_path = None
        if image and image.filename != '':
            filename = secure_filename(image.filename)
            upload_folder = app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
            image_path = os.path.join(upload_folder, filename)
            image.save(image_path)
            note_image_path = f"/static/uploads/{filename}"

        cursor = mysql.connection.cursor()

        try:
            # Insert into notecard
            cursor.execute("""
                INSERT INTO notecard (name, type, text, campaign_id, public, note_image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, note_type, text, campaign_id, public, note_image_path))

            mysql.connection.commit()  # 🔥 Commit to get valid lastrowid

            note_id = cursor.lastrowid
            if not note_id:
                raise Exception("Failed to retrieve inserted notecard ID!")

            # Insert into related tables if needed
            if note_type.lower() in ['character', 'monster', 'npc']:
                race = request.form.get('race')
                level = request.form.get('level') or request.form.get('cr')
                char_class = request.form.get('class')
                strength = request.form.get('strength')
                dexterity = request.form.get('dexterity')
                constitution = request.form.get('constitution')
                intelligence = request.form.get('intelligence')
                wisdom = request.form.get('wisdom')
                charisma = request.form.get('charisma')

                if race and level:
                    cursor.execute("""
                        INSERT INTO entity (note_id, race, level, class, strength, dexterity, constitution, intelligence, wisdom, charisma)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (note_id, race, level, char_class, strength, dexterity, constitution, intelligence, wisdom, charisma))

            elif note_type.lower() == 'spell':
                spell_level = request.form.get('spell_level')
                school = request.form.get('school')
                spell_description = request.form.get('spell_description')
                damage_type = request.form.get('damage_type')
                damage = request.form.get('damage')
                save = request.form.get('save')

                if spell_level and school:
                    cursor.execute("""
                        INSERT INTO spells (note_id, level, school, spell_text, damage_type, damage, save)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (note_id, spell_level, school, spell_description, damage_type, damage, save))

            elif note_type.lower() == 'location':
                location_type = request.form.get('location_type')

                if location_type:
                    cursor.execute("""
                        INSERT INTO location (note_id, location_type)
                        VALUES (%s)
                    """, (note_id, location_type))

            mysql.connection.commit()  # 🔥 Final commit after all inserts

        except Exception as e:
            print("Error during notecard creation:", e)
            mysql.connection.rollback()

            # Optional: clean up uploaded image if insert failed
            if note_image_path:
                try:
                    os.remove(image_path)
                except Exception as remove_error:
                    print("Error cleaning up image file:", remove_error)

            cursor.close()
            return "Database error creating notecard.", 500

        cursor.close()
        return redirect('/notecards')





#select campaign directly
@app.route('/selectcampaigndirect/<int:campaign_id>')
def selectcampaigndirect(campaign_id):
    if 'user_id' not in session:
        return redirect('/login')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT role FROM user_campaign
        WHERE user_id = %s AND campaign_id = %s
    """, (session['user_id'], campaign_id))
    access = cursor.fetchone()
    cursor.close()

    if access:
        session['campaign_id'] = campaign_id
        session['campaign_role'] = access[0]
        return redirect('/notecards')
    else:
        return "Access denied", 403


#add notecard to campaign
@app.route('/addplayer/<int:campaign_id>', methods=['GET', 'POST'])
def add_player(campaign_id):
    if 'user_id' not in session:
        return redirect('/login')
    if session.get('campaign_role') != 'dm':
        return "Only DMs can add players.", 403
    if session.get('campaign_id') != str(campaign_id):
        return "Access denied to this campaign.", 403

    if request.method == 'POST':
        username = request.form['username']
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id FROM user WHERE LOWER(username) = LOWER(%s)", (username,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            return "User not found.", 404
        user_id = user[0]

        # Check if already in campaign
        cursor.execute("SELECT * FROM user_campaign WHERE user_id = %s AND campaign_id = %s", (user_id, campaign_id))
        if cursor.fetchone():
            cursor.close()
            return "User already in campaign.", 400

        # Add to campaign
        cursor.execute("INSERT INTO user_campaign (user_id, campaign_id, role) VALUES (%s, %s, 'player')", (user_id, campaign_id))
        mysql.connection.commit()
        cursor.close()
        return redirect('/campaigns')

    return render_template('addplayer.html', campaign_id=campaign_id)

if __name__ == '__main__':
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=True)
