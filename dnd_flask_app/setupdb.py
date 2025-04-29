import os
from flask_mysqldb import MySQL
import MySQLdb

def run_sql_files(app, directory):
    # Initialize MySQL connection
    mysql = MySQL(app)
    with app.app_context():  # Push the application context
        conn = mysql.connection
        cursor = conn.cursor()

        queries = ["dbdatabase1.sql", "sample_data.sql"] #add quries here

        try:
            # Iterate through all SQL files in the specified directory
            for file in queries:
                file_path = os.path.join(directory, file)
                with open(file_path, 'r') as sql_file:
                    sql_script = sql_file.read()
                    print(f"Running {file}...")
                    for statement in sql_script.split(';'):
                        if statement.strip():
                            cursor.execute(statement)
                    print(f"{file} executed successfully.")
            
            # Commit changes to the database
            conn.commit()
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Close the database connection
            cursor.close()

if __name__ == "__main__":
    from flask import Flask

    app = Flask(__name__)

    # MySQL configuration
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'  # Update if your phpMyAdmin user is different
    app.config['MYSQL_PASSWORD'] = ''  # Enter your MySQL/phpMyAdmin password here
    app.config['MYSQL_DB'] = 'dbdatabase1'  # Change if you named it differently

    sql_directory = "./sql/"  # Path to the directory containing SQL files

    if not os.path.exists(sql_directory):
        print(f"SQL directory '{sql_directory}' does not exist.")
    else:
        run_sql_files(app, sql_directory)