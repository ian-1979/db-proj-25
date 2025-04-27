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

    cards = cursor.fetchall()

    # NEW: Build extra info mapping separately
    extras = {}

    for card in cards:
        card_id, name, type_, text, image = card
        extra = {}

        if type_.lower() in ['character', 'monster', 'npc']:
            cursor.execute("SELECT race, level, class FROM entity WHERE note_id = %s", (card_id,))
            entity = cursor.fetchone()
            if entity:
                extra = {
                    'Race': entity[0],
                    'Level': entity[1],
                    'Class': entity[2]
                }
        elif type_.lower() == 'spell':
            cursor.execute("SELECT level, school, spell_text FROM spells WHERE note_id = %s", (card_id,))
            spell = cursor.fetchone()
            if spell:
                extra = {
                    'Spell Level': spell[0],
                    'School': spell[1],
                    'Spell Text': spell[2]
                }
        elif type_.lower() == 'location':
            cursor.execute("SELECT location_type FROM location WHERE note_id = %s", (card_id,))
            location = cursor.fetchone()
            if location:
                extra = {'Location Type': location[0]}

        if extra:
            extras[card_id] = extra

    cursor.close()
    return render_template('notecards.html', data=cards, extras=extras)





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
        SELECT id, name, type, text, note_image_path, public
        FROM notecard
        WHERE id = %s AND campaign_id = %s
    """, (notecard_id, session['campaign_id']))
    card_data = cursor.fetchone()

    if not card_data:
        cursor.close()
        return "Notecard not found.", 404

    card = {
        'id': card_data[0],
        'name': card_data[1],
        'type': card_data[2],
        'text': card_data[3],
        'note_image_path': card_data[4],
        'public': bool(card_data[5])
    }

    # Now: Load Extra fields depending on Type
    extra = {}

    if card['type'] in ['character', 'monster', 'npc']:
        cursor.execute("""
            SELECT race, level, class, strength, dexterity, constitution, intelligence, wisdom, charisma
            FROM entity
            WHERE note_id = %s
        """, (notecard_id,))
        entity = cursor.fetchone()
        if entity:
            extra = {
                'race': entity[0],
                'level': entity[1],
                'class': entity[2],
                'strength': entity[3],
                'dexterity': entity[4],
                'constitution': entity[5],
                'intelligence': entity[6],
                'wisdom': entity[7],
                'charisma': entity[8],
            }

    elif card['type'] == 'spell':
        cursor.execute("""
            SELECT level, school, spell_text, damage_type, damage, save
            FROM spells
            WHERE note_id = %s
        """, (notecard_id,))
        spell = cursor.fetchone()
        if spell:
            extra = {
                'spell_level': spell[0],
                'school': spell[1],
                'spell_text': spell[2],
                'damage_type': spell[3],
                'damage': spell[4],
                'save': spell[5]
            }

    elif card['type'] == 'location':
        cursor.execute("""
            SELECT location_type
            FROM location
            WHERE note_id = %s
        """, (notecard_id,))
        location = cursor.fetchone()
        if location:
            extra = {
                'location_type': location[0]
            }

    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        note_type = request.form['type']
        text = request.form['text']
        public = int(request.form.get('public', 0))

        # Handle image upload
        image = request.files.get('image')
        note_image_path = card['note_image_path']  # Default to existing
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
            # Update notecard table
            cursor.execute("""
                UPDATE notecard
                SET name = %s, type = %s, text = %s, note_image_path = %s, public = %s
                WHERE id = %s AND campaign_id = %s
            """, (name, note_type, text, note_image_path, public, notecard_id, session['campaign_id']))

            # Delete old type-specific records (simpler and safer)
            cursor.execute("DELETE FROM entity WHERE note_id = %s", (notecard_id,))
            cursor.execute("DELETE FROM spells WHERE note_id = %s", (notecard_id,))
            cursor.execute("DELETE FROM location WHERE note_id = %s", (notecard_id,))

            # Re-insert new type-specific data
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
                    """, (notecard_id, race, level, char_class, strength, dexterity, constitution, intelligence, wisdom, charisma))

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
                    """, (notecard_id, spell_level, school, spell_description, damage_type, damage, save))

            elif note_type.lower() == 'location':
                location_type = request.form.get('location_type')

                if location_type:
                    cursor.execute("""
                        INSERT INTO location (note_id, location_type)
                        VALUES (%s)
                    """, (notecard_id, location_type))

            mysql.connection.commit()
            cursor.close()

        except Exception as e:
            print("Error during notecard update:", e)
            mysql.connection.rollback()
            cursor.close()
            return "Database error updating notecard.", 500

        return redirect('/notecards')


    return render_template('editnotecard.html', card=card, extra=extra)



@app.route('/viewnotecard/<int:notecard_id>')
def view_notecard(notecard_id):
    if 'campaign_id' not in session:
        return redirect('/selectcampaign')

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT id, name, type, text, note_image_path
        FROM notecard
        WHERE id = %s AND campaign_id = %s
    """, (notecard_id, session['campaign_id']))
    card = cursor.fetchone()

    if not card:
        cursor.close()
        return "Notecard not found.", 404

    # Load Extra Fields
    extra = {}
    cursor.execute("""
        SELECT race, level, class, strength, dexterity, constitution, intelligence, wisdom, charisma
        FROM entity WHERE note_id = %s
    """, (notecard_id,))
    entity = cursor.fetchone()
    if entity:
        extra.update({
            'Race': entity[0],
            'Level': entity[1],
            'Class': entity[2],
            'Strength': entity[3],
            'Dexterity': entity[4],
            'Constitution': entity[5],
            'Intelligence': entity[6],
            'Wisdom': entity[7],
            'Charisma': entity[8],
        })

    cursor.execute("""
        SELECT level, school, spell_text, damage_type, damage, save
        FROM spells WHERE note_id = %s
    """, (notecard_id,))
    spell = cursor.fetchone()
    if spell:
        extra.update({
            'Spell Level': spell[0],
            'School': spell[1],
            'Spell Text': spell[2],
            'Damage Type': spell[3],
            'Damage': spell[4],
            'Save': spell[5],
        })

    cursor.execute("""
        SELECT location_type
        FROM location WHERE note_id = %s
    """, (notecard_id,))
    location = cursor.fetchone()
    if location:
        extra.update({
            'Location Type': location[0],
        })

    # Tags system (later attach real tags)
    cursor.execute("""
        SELECT t.name
        FROM tag t
        JOIN notecard_tag nt ON t.id = nt.tag_id
        WHERE nt.note_id = %s
    """, (notecard_id,))
    tag = [row[0] for row in cursor.fetchall()]

    # Notes system
    cursor.execute("""
        SELECT u.username, n.note_text
        FROM user_note n
        JOIN user u ON n.user_id = u.id
        WHERE n.note_id = %s
    """, (notecard_id,))
    notes = cursor.fetchall()

    cursor.close()

    return render_template('viewnotecard.html', card=card, extra=extra, tag=tag, notes=notes)

@app.route('/addnotecardnote/<int:notecard_id>', methods=['POST'])
def add_notecard_note(notecard_id):
    if 'user_id' not in session:
        return redirect('/login')

    note_text = request.form['note_text']
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO user_note (note_id, user_id, note_text)
        VALUES (%s, %s, %s)
    """, (notecard_id, session['user_id'], note_text))
    mysql.connection.commit()
    cursor.close()

    return redirect(f'/viewnotecard/{notecard_id}')



@app.route('/tagsearch/<string:tag>')
def tag_search(tag):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT n.id, n.name, n.type, n.text, n.note_image_path
        FROM notecard n
        JOIN notecard_tag t ON n.id = t.note_id
        WHERE t.tag = %s
    """, (tag,))
    cards = cursor.fetchall()

    # No extras for now in search
    extras = {}
    return render_template('notecards.html', data=cards, extras=extras)



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
