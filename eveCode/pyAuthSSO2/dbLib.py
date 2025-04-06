def init_db(DATA_FOLDER='.gitignore/data/', DB_FILE='eve.db'):
    """Initialize the SQLite database."""
    #print('init_db func')
    import sqlite3
    conn = sqlite3.connect(DATA_FOLDER + DB_FILE)
    cursor = conn.cursor()
    # Applications table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS applications (
            app_index INTEGER PRIMARY KEY AUTOINCREMENT,
            appName TEXT,
            client_id TEXT UNIQUE NOT NULL,
            client_secret TEXT UNIQUE NOT NULL,
            scopes TEXT NOT NULL
        )
    """)
    # User table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_index INTEGER PRIMARY KEY AUTOINCREMENT,
            characterownerhash TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Character table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS characters (
            character_index INTEGER PRIMARY KEY AUTOINCREMENT, -- Internal sequence-based primary key
            character_id INTEGER UNIQUE NOT NULL, -- EVE-specific character ID
            name TEXT,
            user_index INTEGER NOT NULL, -- Reference to the Users table
            FOREIGN KEY(user_index) REFERENCES users(user_index) ON DELETE CASCADE
        )
    """)
    # Token table
    cursor.execute(""" 
        CREATE TABLE IF NOT EXISTS tokens (
            token_index INTEGER PRIMARY KEY AUTOINCREMENT,
            access_token TEXT NOT NULL,
            refresh_token TEXT NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            character_index INTEGER NOT NULL, -- Reference to the Character table
            FOREIGN KEY(character_index) REFERENCES characters(character_index) ON DELETE CASCADE
        )
    """)
    # Scope table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scopes (
            scope_index INTEGER PRIMARY KEY AUTOINCREMENT,
            scope TEXT NOT NULL,
            token_index INTEGER NOT NULL, -- Reference to the Token table
            FOREIGN KEY(token_index) REFERENCES tokens(token_index) ON DELETE CASCADE
        )
    """)
    # Structures table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS structures (
            structure_id INTEGER PRIMARY KEY,
            name TEXT,
            solar_system_id INTEGER,
            region_id INTEGER
        )
    """)
    # indexes
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_characterownerhash ON users(characterownerhash);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_characters_character_id ON characters(character_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_characters_user_index ON characters(user_index);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_character_index ON tokens(character_index);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_tokens_expires_at ON tokens(expires_at);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_scopes_token_index ON scopes(token_index);")
    conn.commit()
    print("Database initialized.")
    return conn

def connDB(DB_FILEPATH):
    import sqlite3
    from os import path
    if path.exists(DB_FILEPATH):
        conn = sqlite3.connect(DB_FILEPATH)
        return conn
    else:
        init_db()

def addEntry(table, data, db_conn):
    """
    Adds an entry to a specified table in the database.
    
    Parameters:
    - table (str): The name of the table where the entry should be added.
    - data (dict): A dictionary where the keys are column names, and the values are the values to be inserted.
    - db_conn (sqlite3.Connection): The active database connection.
    """
    import sqlite3
    try:
        # Extract keys and values from the data dictionary
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data.values()])
        values = tuple(data.values())

        # Create SQL command for inserting data into the specified table
        sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        # Execute the command
        cursor = db_conn.cursor()
        cursor.execute(sql, values)
        db_conn.commit()

        print(f"Entry added to {table} successfully.")
    except sqlite3.IntegrityError as e:
        print(f"Error: Integrity constraint violated - {e}")
    except sqlite3.OperationalError as e:
        print(f"Error: Operational error - {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    dbPathName = '.gitignore/data/eve.db'
    init_db()
