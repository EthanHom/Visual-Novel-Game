import sqlite3
from sqlite3 import Error

DATABASE_FILE = "visual_novel_engine.db"

def create_connection():
    """ create a database connection to the SQLite database
        specified by DATABASE_FILE
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        print(f"Connected to SQLite database (version {sqlite3.version})")
        # Enable foreign key support
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Error as e:
        print(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)

def create_all_tables(conn):
    """ Creates all tables for the Visual Novel Engine database """
    
    sql_create_locations_table = """
    CREATE TABLE IF NOT EXISTS Locations (
        location_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        bg_path TEXT NOT NULL
    );
    """

    sql_create_characters_table = """
    CREATE TABLE IF NOT EXISTS Characters (
        char_id INTEGER PRIMARY KEY,
        char_name TEXT NOT NULL,
        text_color TEXT NOT NULL DEFAULT 'FFFFFF'
    );
    """

    sql_create_events_table = """
    CREATE TABLE IF NOT EXISTS Events (
        event_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        obtained_bool BOOLEAN NOT NULL DEFAULT 0
    );
    """

    sql_create_scenes_table = """
    CREATE TABLE IF NOT EXISTS Scenes (
        scene_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        location_id INTEGER NOT NULL,
        next_scene_default INTEGER,
        FOREIGN KEY (location_id) REFERENCES Locations (location_id)
            ON DELETE SET NULL,
        FOREIGN KEY (next_scene_default) REFERENCES Scenes (scene_id)
            ON DELETE SET NULL
    );
    """

    sql_create_sprites_table = """
    CREATE TABLE IF NOT EXISTS Sprites (
        sprite_id INTEGER PRIMARY KEY,
        char_id INTEGER NOT NULL,
        expression_id INTEGER NOT NULL,
        expression TEXT NOT NULL,
        path TEXT NOT NULL,
        FOREIGN KEY (char_id) REFERENCES Characters (char_id)
            ON DELETE CASCADE
    );
    """
    
    # Note: Added 'decision_text' as it's implied by the use case (Page 8)
    # but missing from the schema diagram (Page 5).
    sql_create_choices_table = """
    CREATE TABLE IF NOT EXISTS Choices (
        decision_id INTEGER PRIMARY KEY,
        choice_id INTEGER NOT NULL,
        decision_text TEXT NOT NULL,
        next_scene INTEGER,
        event_id INTEGER,
        FOREIGN KEY (next_scene) REFERENCES Scenes (scene_id)
            ON DELETE SET NULL,
        FOREIGN KEY (event_id) REFERENCES Events (event_id)
            ON DELETE SET NULL
    );
    """

    sql_create_lines_table = """
    CREATE TABLE IF NOT EXISTS Lines (
        line_id INTEGER PRIMARY KEY,
        scene_id INTEGER NOT NULL,
        speaker_id INTEGER NOT NULL,
        sequence INTEGER NOT NULL,
        content TEXT NOT NULL,
        sprite_id INTEGER,
        expression_id INTEGER,
        choice_id INTEGER,
        FOREIGN KEY (scene_id) REFERENCES Scenes (scene_id)
            ON DELETE CASCADE,
        FOREIGN KEY (speaker_id) REFERENCES Characters (char_id)
            ON DELETE CASCADE,
        FOREIGN KEY (sprite_id) REFERENCES Sprites (sprite_id)
            ON DELETE SET NULL
    );
    """

    # Create tables
    if conn is not None:
        create_table(conn, sql_create_locations_table)
        create_table(conn, sql_create_characters_table)
        create_table(conn, sql_create_events_table)
        create_table(conn, sql_create_scenes_table)
        create_table(conn, sql_create_sprites_table)
        create_table(conn, sql_create_choices_table)
        create_table(conn, sql_create_lines_table)
        print("All tables created successfully.")
    else:
        print("Error! cannot create the database connection.")

if __name__ == '__main__':
    conn = create_connection()
    if conn:
        create_all_tables(conn)
        conn.close()