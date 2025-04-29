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
    # if session.get('campain_role') == 'dm':
    #     return render_template('index.html', role='dm')
    # elif session.get('campaign_role') == 'player':
    #     return render_template('index.html', role='player')
    return render_template('index.html', role='noCampaign')

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
        tag = request.form.get('tag', '')

        cursor = mysql.connection.cursor()

        base_query = """
            SELECT DISTINCT n.id, n.name, n.type, n.text, n.note_image_path
            FROM notecard n
            LEFT JOIN notecard_tag nt ON n.id = nt.note_id
            LEFT JOIN tag t ON nt.tag_id = t.id
            WHERE n.campaign_id = %s
        """
        conditions = []
        params = [session['campaign_id']]

        if name:
            conditions.append("n.name LIKE %s")
            params.append(f"%{name}%")
        if note_type:
            conditions.append("n.type = %s")
            params.append(note_type)
        if tag:
            conditions.append("t.name LIKE %s")
            params.append(f"%{tag}%")

        if conditions:
            base_query += " AND " + " AND ".join(conditions)

        cursor.execute(base_query, params)
        cards = cursor.fetchall()

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

    extra = {}
    spells = [] 

    if card['type'] in ['character', 'monster', 'npc']:
        cursor.execute("""
            SELECT race, level, class, strength, dexterity, constitution, intelligence, wisdom, charisma, id
            FROM entity
            WHERE note_id = %s
        """, (notecard_id,))
        entity = cursor.fetchone()
        
        if entity:
            extra = dict(zip(
                ['race', 'level', 'class', 'strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma'],
                entity
            ))
        # Load all spells and known spells
        cursor.execute("SELECT id, name FROM notecard WHERE type = 'spell' AND campaign_id = %s", (session['campaign_id'],))
        all_spells = cursor.fetchall()
        cursor.execute("SELECT spell_id FROM entity_spell WHERE entity_id = %s", (notecard_id,))
        known_spells = [row[0] for row in cursor.fetchall()]
        all_spells = []
        known_spells = []
        # Fetch spell IDs associated with this entity
        cursor.execute("""
            SELECT spell_id
            FROM entity_spell
            WHERE entity_id = %s
        """, (entity[9],))
        associated_spell_ids = [row[0] for row in cursor.fetchall()]
        print("Associated spell IDs:", associated_spell_ids)

        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT s.id, n.name
            FROM spells s
            JOIN notecard n ON s.note_id = n.id
            where n.campaign_id = %s
        """, (session['campaign_id'],))
        spells = cursor.fetchall()
        cursor.close()
        # Format spells for dropdown
        spells = [{'id': spell[0], 'name': spell[1]} for spell in spells]

        extra['spells'] = [spell for spell in spells if spell['id'] in associated_spell_ids]
        

    elif card['type'] == 'spell':
        cursor.execute("""
            SELECT level, school, spell_text, damage_type, damage, save
            FROM spells WHERE note_id = %s
        """, (notecard_id,))
        spell = cursor.fetchone()
        if spell:
            extra = dict(zip(
                ['spell_level', 'school', 'spell_text', 'damage_type', 'damage', 'save'],
                spell
            ))

    if card['type'] == 'location':
        cursor.execute("""
            SELECT location_type
            FROM location
            WHERE note_id = %s
        """, (notecard_id,))
        location = cursor.fetchone()
        if location:
            extra = {'location_type': location[0]}

    cursor.close()

    if request.method == 'POST':
        name = request.form['name']
        note_type = request.form['type']
        text = request.form['text']
        public = int(request.form.get('public', 0))

        image = request.files.get('image')
        note_image_path = card['note_image_path']
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
            cursor.execute("""
                UPDATE notecard
                SET name = %s, type = %s, text = %s, note_image_path = %s, public = %s
                WHERE id = %s AND campaign_id = %s
            """, (name, note_type, text, note_image_path, public, notecard_id, session['campaign_id']))


            #this is objectively bad should alter records because thats what were doing. editing a notecard
            # # Delete old type-specific records (simpler and safer)
            # cursor.execute("DELETE FROM entity WHERE note_id = %s", (notecard_id,))
            # cursor.execute("DELETE FROM spells WHERE note_id = %s", (notecard_id,))
            # cursor.execute("DELETE FROM location WHERE note_id = %s", (notecard_id,))


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
                        UPDATE entity
                        SET race = %s, level = %s, class = %s, strength = %s, dexterity = %s, constitution = %s, intelligence = %s, wisdom = %s, charisma = %s
                        WHERE note_id = %s
                    """, (race, level, char_class, strength, dexterity, constitution, intelligence, wisdom, charisma, notecard_id))
                    # Get the ID of the last inserted entity
                    cursor.execute("SELECT id FROM entity WHERE note_id = %s", (notecard_id,))
                    entity_id = cursor.fetchone()[0]

                    print("Entity ID:", entity_id)
                    # Remove existing spell associations for the entity
                    cursor.execute("""
                        DELETE FROM entity_spell
                        WHERE entity_id = %s
                    """, (entity_id,))

                    spell_ids = request.form.getlist('spell_ids[]')
                    print("Selected spell IDs:", spell_ids)
                    for spell_id in spell_ids:
                        connectSpell(entity_id, spell_id)

                cursor.execute("DELETE FROM entity_spell WHERE entity_id = %s", (notecard_id,))
                selected_spells = request.form.getlist('spells')
                for spell_id in selected_spells:
                    cursor.execute("INSERT INTO entity_spell (entity_id, spell_id) VALUES (%s, %s)", (notecard_id, spell_id))

            elif note_type.lower() == 'spell':
                spell_level = request.form.get('spell_level')
                school = request.form.get('school')
                spell_description = request.form.get('spell_description')
                damage_type = request.form.get('damage_type')
                damage = request.form.get('damage')
                save = request.form.get('save')
                if spell_level and school:
                    cursor.execute("""
                        UPDATE spells
                        SET level = %s, school = %s, spell_text = %s, damage_type = %s, damage = %s, save = %s
                        WHERE note_id = %s
                    """, (spell_level, school, spell_description, damage_type, damage, save, notecard_id))

            elif note_type.lower() == 'location':
                location_type = request.form.get('location_type')
                if location_type:
                    cursor.execute("""
                        UPDATE location
                        SET location_type = %s
                        WHERE note_id = %s
                    """, (location_type, notecard_id))


            mysql.connection.commit()
            cursor.close()

        except Exception as e:
            print("Error during notecard update:", e)
            mysql.connection.rollback()
            cursor.close()
            return "Database error updating notecard.", e

        return redirect('/notecards')

    return render_template('editnotecard.html', card=card, extra=extra, spells=spells)



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


    linked_spells = []
    cursor.execute("""
        SELECT s.note_id, n.name
        FROM entity_spell es
        JOIN spells s ON es.spell_id = s.id
        JOIN notecard n ON s.note_id = n.id
        WHERE es.entity_id = (
            SELECT id FROM entity WHERE note_id = %s
        )
    """, (notecard_id,))
    linked_spells = cursor.fetchall()

    # Tags system (later attach real tags)
    cursor.execute("""
        SELECT t.name
        FROM tag t
        JOIN notecard_tag nt ON t.id = nt.tag_id
        WHERE nt.note_id = %s
    """, (notecard_id,))
    tags = [row[0] for row in cursor.fetchall()]

    # Notes system
    cursor.execute("""
        SELECT u.username, n.note_text
        FROM user_note n
        JOIN user u ON n.user_id = u.id
        WHERE n.note_id = %s
    """, (notecard_id,))
    notes = cursor.fetchall()

    cursor.close()

    return render_template('viewnotecard.html', card=card, extra=extra, tags=tags, notes=notes, linked_spells=linked_spells)


# @app.route('/addnotecardnote', methods=['GET'])
# def add_notecard_note_get():
#     print("add_notecard_note called with notecard_id:")

#     spells = []
#     cursor = mysql.connection.cursor()
#     cursor.execute("""
#         SELECT s.id, n.name
#         FROM spells s
#         JOIN notecard n ON s.note_id = n.id
#     """)
#     spells = cursor.fetchall()
#     cursor.close()
#     spells = [{'id': spell[0], 'name': spell[1]} for spell in spells]
#     print("Spells fetched:", spells)
#     # Format spells for dropdown
#     return render_template('addnotecardnote.html', spells=spells, extra=None)
    

# @app.route('/addnotecardnote/<int:notecard_id>', methods=['POST'])
# def add_notecard_note(notecard_id):
#     print("add_notecard_note called with notecard_id:", notecard_id)

#     if 'user_id' not in session:
#         return redirect('/login')

#     note_text = request.form['note_text']
#     cursor = mysql.connection.cursor()
#     cursor.execute("""
#         INSERT INTO user_note (note_id, user_id, note_text)
#         VALUES (%s, %s, %s)
#     """, (notecard_id, session['user_id'], note_text))
#     mysql.connection.commit()
#     cursor.close()

#     spell_ids = request.form.getlist('spell_ids[]')
#     cursor = mysql.connection.cursor()
#     cursor.execute("""
#         SELECT id
#         FROM entity
#         WHERE note_id = %s
#     """, (notecard_id,))
#     entity = cursor.fetchone()
#     cursor.close()

#     if entity:
#         entity_id = entity[0]
#     else:
#         entity_id = None
#     connectSpell(entity_id, spell_ids)

#     return redirect(f'/viewnotecard/{notecard_id}')



@app.route('/addtag/<int:notecard_id>', methods=['POST'])
def add_tag(notecard_id):
    if 'user_id' not in session:
        return redirect('/login')
    if session.get('campaign_role') != 'dm':
        return "Only DMs can add tags.", 403

    tag_name = request.form['tag_name'].strip()

    if not tag_name:
        print("No tag_name provided.")
        return redirect(f'/viewnotecard/{notecard_id}')

    cursor = mysql.connection.cursor()

    try:
        print(f"Checking if tag '{tag_name}' exists...")
        cursor.execute("SELECT id FROM tag WHERE name = %s", (tag_name,))
        tag = cursor.fetchone()

        if not tag:
            print(f"Tag '{tag_name}' does not exist. Inserting new tag...")
            cursor.execute("INSERT INTO tag (name) VALUES (%s)", (tag_name,))
            mysql.connection.commit()
            tag_id = cursor.lastrowid
            print(f"Inserted new tag with id {tag_id}")
        else:
            tag_id = tag[0]
            print(f"Found existing tag id {tag_id}")

        # Now link it
        cursor.execute("SELECT * FROM notecard_tag WHERE note_id = %s AND tag_id = %s", (notecard_id, tag_id))
        existing_link = cursor.fetchone()

        if not existing_link:
            print(f"Linking tag id {tag_id} to notecard id {notecard_id}...")
            cursor.execute("INSERT INTO notecard_tag (note_id, tag_id) VALUES (%s, %s)", (notecard_id, tag_id))
            mysql.connection.commit()
        else:
            print(f"Link already exists between notecard id {notecard_id} and tag id {tag_id}")

    except Exception as e:
        print("Error during tag creation/linking:", e)
        mysql.connection.rollback()

    cursor.close()

    return redirect(f'/viewnotecard/{notecard_id}')


    return render_template('editnotecard.html', card=card)




@app.route('/tagsearch/<string:tag>')
def tag_search(tag):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT n.id, n.name, n.type, n.text, n.note_image_path
        FROM notecard n
        JOIN notecard_tag nt ON n.id = nt.note_id
        JOIN tag t ON t.id = nt.tag_id
        WHERE t.name = %s
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
            #return "Invalid username or password", 401
            return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')

#register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        password_hash = generate_password_hash(password)
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO user (username, password) VALUES (%s, %s)", (username, password_hash))
            mysql.connection.commit()

            # Fetch the newly created user ID
            cursor.execute("SELECT id FROM user WHERE username = %s", (username,))
            user = cursor.fetchone()
        except Exception as e:
            print("Error during user registration:", e)
            mysql.connection.rollback()
            user = None
            return render_template('register.html', error="User already exists.")
        finally:
            cursor.close()

        if user:
            # Log the user in by setting session variables
            session['user_id'] = user[0]
            session['username'] = username

            return redirect(url_for('index'))

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
            return redirect(url_for('index'))
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
    print("Session info at /campaigns:", session)

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

    cursor = mysql.connection.cursor()

    if request.method == 'GET':
        # Fetch available spells for the dropdown
        cursor.execute("""
            SELECT s.id, n.name
            FROM spells s
            JOIN notecard n ON s.note_id = n.id
            WHERE n.campaign_id = %s
        """, (session['campaign_id'],))
        spells = [{'id': spell[0], 'name': spell[1]} for spell in cursor.fetchall()]


        # Initialize `extra.spells` as an empty list for new notecards
        extra = {'spells': []}

        print("Spells fetched for new notecard:", spells)

        cursor.close()
        return render_template('newnotecard.html', spells=spells, extra=extra)

    if request.method == 'POST':
        # Handle form submission
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

        try:
            # Insert into notecard
            cursor.execute("""
                INSERT INTO notecard (name, type, text, campaign_id, public, note_image_path)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (name, note_type, text, campaign_id, public, note_image_path))

            mysql.connection.commit()  

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
                
                        # Get the list of selected spell IDs
                spell_ids = request.form.getlist('spell_ids[]')
                print("Selected spell IDs:", spell_ids)
                entity_id = cursor.lastrowid  # Get the ID of the last inserted entity
                # Connect the entity to spells if any are selected
                for spell_id in spell_ids:
                    connectSpell(entity_id, spell_id)

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
                        VALUES (%s, %s)
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

    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT role FROM user_campaign
        WHERE user_id = %s AND campaign_id = %s
    """, (session['user_id'], campaign_id))
    access = cursor.fetchone()
    cursor.close()

    if not access or access[0] != 'dm':
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

def connectSpell(entity_id, spell_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO entity_spell (entity_id, spell_id)
        VALUES (%s, %s)
    """, (entity_id, spell_id))
    mysql.connection.commit()
    cursor.close()

if __name__ == '__main__':
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.run(debug=True)
