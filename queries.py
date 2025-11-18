import sqlite3
from sqlite3 import Error

def fetch_all(conn, sql, params=()):
    # run a SELECT query and return all results
    try:
        c = conn.cursor()
        c.execute(sql, params)
        return c.fetchall()
    except Error as e:
        print(e)
        return []

def execute_sql(conn, sql, params=()):
    # run an INSERT, UPDATE, DELETE query
    try:
        c = conn.cursor()
        c.execute(sql, params)
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(f"Error: {e}")
        return None


# 1. (INSERT) Add new character
def add_character(conn, name, color):
    sql = """
        INSERT INTO Characters(char_name, text_color) 
        VALUES(?,?)
    """
    return execute_sql(conn, sql, (name, color))

# 2. (READ) Get all characters
def get_all_characters(conn):
    sql = """
        SELECT char_id, char_name, text_color 
        FROM Characters
    """
    return fetch_all(conn, sql)

# 3. (UPDATE) Update character name
def update_character_name(conn, char_id, new_name):
    sql = """
        UPDATE Characters 
        SET char_name = ? 
        WHERE char_id = ?
    """
    return execute_sql(conn, sql, (new_name, char_id))

# 4. (DELETE) Delete character
def delete_character(conn, char_id):
    sql = """
        DELETE FROM Characters 
        WHERE char_id = ?
    """
    return execute_sql(conn, sql, (char_id,))

# 5. (INSERT) Add new sprite
def add_sprite(conn, char_id, exp_id, expression, path):
    sql = """
        INSERT INTO Sprites(char_id, expression_id, expression, path) 
        VALUES(?,?,?,?)
    """
    return execute_sql(conn, sql, (char_id, exp_id, expression, path))

# 6. (READ) Get all sprites for a character
def get_sprites_for_character(conn, char_id):
    sql = """
        SELECT sprite_id, expression, path 
        FROM Sprites 
        WHERE char_id = ?
    """
    return fetch_all(conn, sql, (char_id,))

# 7. (INSERT) Add new location
def add_location(conn, name, bg_path):
    sql = """
        INSERT INTO Locations(name, bg_path) 
        VALUES(?,?)
    """
    return execute_sql(conn, sql, (name, bg_path))

# 8. (READ) Get all locations
def get_all_locations(conn):
    sql = """
        SELECT location_id, name, bg_path 
        FROM Locations
    """
    return fetch_all(conn, sql)

# 9. (INSERT) Add new scene
def add_scene(conn, name, location_id, next_scene_default=None):
    sql = """
        INSERT INTO Scenes(name, location_id, next_scene_default) 
        VALUES(?,?,?)
    """
    return execute_sql(conn, sql, (name, location_id, next_scene_default))

# 10. (UPDATE) Assign location to scene
def update_scene_location(conn, scene_id, new_location_id):
    sql = """
        UPDATE Scenes 
        SET location_id = ? 
        WHERE scene_id = ?
    """
    return execute_sql(conn, sql, (new_location_id, scene_id))

# 11. (INSERT) Add new line of dialogue
def add_dialogue_line(conn, scene_id, speaker_id, seq, content, exp_id=None, choice_id=None):
    sql = """
        INSERT INTO Lines(scene_id, speaker_id, sequence, content, expression_id, choice_id)
        VALUES(?,?,?,?,?,?)
    """
    return execute_sql(conn, sql, (scene_id, speaker_id, seq, content, exp_id, choice_id))

# 12. (DELETE) Delete a line of dialogue
def delete_dialogue_line(conn, line_id):
    sql = """
        DELETE FROM Lines 
        WHERE line_id = ?
    """
    return execute_sql(conn, sql, (line_id,))

# 13. (INSERT) Add new choice option
def add_choice(conn, choice_group_id, text, next_scene_id, event_id=None):
    sql = """
        INSERT INTO Choices(choice_id, decision_text, next_scene, event_id) 
        VALUES(?,?,?,?)
    """
    return execute_sql(conn, sql, (choice_group_id, text, next_scene_id, event_id))

# 14. (INSERT) Add new event
def add_event(conn, name, obtained=False):
    sql = """
        INSERT INTO Events(name, obtained_bool) 
        VALUES(?,?)
    """
    return execute_sql(conn, sql, (name, obtained))

# 15. (UPDATE) Update event status
def update_event_obtained(conn, event_id, obtained_bool):
    sql = """
        UPDATE Events 
        SET obtained_bool = ? 
        WHERE event_id = ?
    """
    return execute_sql(conn, sql, (obtained_bool, event_id))

# 16. (READ) Get all scenes at a location
def get_scenes_at_location(conn, location_id):
    sql = """
        SELECT scene_id, name 
        FROM Scenes 
        WHERE location_id = ?
    """
    return fetch_all(conn, sql, (location_id,))

# 17. (DELETE) Delete all lines from a scene
def delete_lines_from_scene(conn, scene_id):
    sql = """
        DELETE FROM Lines 
        WHERE scene_id = ?
    """
    return execute_sql(conn, sql, (scene_id,))

# 18. (READ - AGGREGATE) Count lines for each character
def count_lines_by_character(conn):
    sql = """
    SELECT c.char_name, COUNT(l.line_id)
    FROM Characters c, Lines l
    WHERE c.char_id = l.speaker_id
    GROUP BY c.char_name
    ORDER BY COUNT(l.line_id) DESC
    """
    return fetch_all(conn, sql)

# 19. (READ - JOIN) Get all characters and their sprites
def get_all_character_sprites(conn):
    sql = """
    SELECT c.char_name, s.expression, s.path
    FROM Characters c, Sprites s
    WHERE c.char_id = s.char_id
    """
    return fetch_all(conn, sql)

# 20. (READ - SUBQUERY) Find scenes with no dialogue
def get_empty_scenes(conn):
    sql = """
    SELECT scene_id, name
    FROM Scenes
    WHERE scene_id NOT IN (
                            SELECT DISTINCT scene_id 
                            FROM Lines
                            )
    """
    return fetch_all(conn, sql)


# === USE CASE: PLAYER/FRONTEND (5+ Statements) ===

# 21. (READ - JOIN) Get scene and its location background
def get_scene_and_location(conn, scene_id):
    sql = """
    SELECT s.name, l.bg_path
    FROM Scenes s,  Locations l
    WHERE s.location_id = l.location_id
    AND s.scene_id = ?
    """
    return fetch_all(conn, sql, (scene_id,))

# 22. (READ - JOIN) Get all dialogue lines for a scene
def get_dialogue_for_scene(conn, scene_id):
    sql = """
    SELECT l.line_id, l.content, l.sequence, l.choice_id, c.char_name, c.text_color, s.path
    FROM Lines l, Characters c, Sprites s
    WHERE l.speaker_id = c.char_id
    AND l.speaker_id = s.char_id 
    AND l.expression_id = s.expression_id
    AND l.scene_id = ?

    UNION

    SELECT l.line_id, l.content, l.sequence, l.choice_id, c.char_name, c.text_color, NULL
    FROM Lines l, Characters c
    WHERE l.speaker_id = c.char_id
    AND l.expression_id IS NULL
    AND l.scene_id = ?

    ORDER BY sequence ASC
    """
    return fetch_all(conn, sql, (scene_id, scene_id))

# 23. (READ) Get choices for a choice group
def get_choices(conn, choice_id):
    sql = """
        SELECT decision_id, decision_text 
        FROM Choices 
        WHERE choice_id = ?
    """
    return fetch_all(conn, sql, (choice_id,))

# 24. (READ) Get info from a selected decision
def get_decision_result(conn, decision_id):
    sql = """
        SELECT next_scene, event_id 
        FROM Choices 
        WHERE decision_id = ?
    """
    return fetch_all(conn, sql, (decision_id,))

# 25. (READ) Check if an event has been obtained
def check_event_status(conn, event_id):
    sql = """
        SELECT obtained_bool 
        FROM Events 
        WHERE event_id = ?
    """
    return fetch_all(conn, sql, (event_id,))