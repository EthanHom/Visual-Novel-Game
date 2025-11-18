import sqlite3
from sqlite3 import Error
from create_schema import create_connection

def insert_location(conn, location):
    sql = ''' INSERT INTO Locations(name, bg_path)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, location)
    return cur.lastrowid

def insert_character(conn, character):
    sql = ''' INSERT INTO Characters(char_id, char_name, text_color)
              VALUES(?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, character)
    return cur.lastrowid

def insert_event(conn, event):
    sql = ''' INSERT INTO Events(name, obtained_bool)
              VALUES(?,?) '''
    cur = conn.cursor()
    cur.execute(sql, event)
    return cur.lastrowid

def insert_scene(conn, scene):
    sql = ''' INSERT INTO Scenes(scene_id, name, location_id, next_scene_default)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, scene)
    return cur.lastrowid

def insert_sprite(conn, sprite):
    sql = ''' INSERT INTO Sprites(char_id, expression_id, expression, path)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, sprite)
    return cur.lastrowid

def insert_choice(conn, choice):
    sql = ''' INSERT INTO Choices(choice_id, decision_text, next_scene, event_id)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, choice)
    return cur.lastrowid

def insert_line(conn, line):
    sql = ''' INSERT INTO Lines(scene_id, speaker_id, sequence, content, expression_id, choice_id)
              VALUES(?,?,?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, line)
    return cur.lastrowid

def insert_data(conn):
    """ Inserts a full set of data into the database """
    try:
        with conn:
            # Locations
            # example: loc1 = insert_location(conn, ('The Library', '/img/bg/library.png'))
            loc1 = insert_location(conn, ('The Library', ''))
            loc2 = insert_location(conn, ('Town Square', ''))

            # Characters
            # Using specific IDs to make foreign keys easier to track
            char1 = insert_character(conn, (1, 'Protagonist', 'FFFFFF'))
            char2 = insert_character(conn, (2, 'Maya', 'E0BBE4'))
            char3 = insert_character(conn, (3, 'Detective', 'A9A9A9'))
            
            # Events
            evt1 = insert_event(conn, ('Met Maya', False))
            evt2 = insert_event(conn, ('Found Clue', False))

            # Sprites
            # expression_id: 1=neutral, 2=happy, 3=sad, 4=angry
            # example: 
                # sprite1 = insert_sprite(conn, (2, 1, 'neutral', '/img/sprites/maya_neutral.png'))
                # sprite2 = insert_sprite(conn, (2, 2, 'happy', '/img/sprites/maya_happy.png'))
                # sprite3 = insert_sprite(conn, (3, 1, 'neutral', '/img/sprites/detective_neutral.png'))
            sprite1 = insert_sprite(conn, (2, 1, 'neutral', ''))
            sprite2 = insert_sprite(conn, (2, 2, 'happy', ''))
            sprite3 = insert_sprite(conn, (3, 1, 'neutral', ''))

            # Scenes
            # Using specific IDs for easy linking
            scene1 = insert_scene(conn, (1, 'Chapter 1: The Meetup', loc2, None))
            scene2 = insert_scene(conn, (2, 'Chapter 1: The Library', loc1, None))
            scene3 = insert_scene(conn, (3, 'Chapter 1: The Square', loc2, None))
            
            # Link scene 1 to choice
            conn.execute("UPDATE Scenes SET next_scene_default = ? WHERE scene_id = ?", (2, 1))


            # Lines (Dialogue)
            # Scene 1
            insert_line(conn, (1, 3, 1, 'You must be the new recruit.', 1, None))
            insert_line(conn, (1, 1, 2, 'That I am. You must be the Detective?', 1, None))
            insert_line(conn, (1, 3, 3, 'Just "Detective" is fine.', 1, None))
            insert_line(conn, (1, 3, 4, 'We were supposed to meet someone here... ah, there she is.', 1, None))
            insert_line(conn, (1, 2, 5, 'Sorry I\'m late! The traffic was terrible.', 2, None))
            insert_line(conn, (1, 1, 6, '(Wow, she seems friendly.)', 1, None))
            insert_line(conn, (1, 3, 7, 'Now that we\'re all here, where should we investigate first?', 1, 1)) # This line triggers choice_id 1

            # Scene 2
            insert_line(conn, (2, 1, 1, 'The library... just as dusty as I remember.', 1, None))

            # Scene 3
            insert_line(conn, (3, 2, 1, 'The square is so busy today.', 1, None))

            # Choices
            # choice_id 1 links to line 7 in scene 1
            insert_choice(conn, (1, 'Investigate the Library.', 2, evt2)) # Links to scene 2, triggers event 2
            insert_choice(conn, (1, 'Check the Town Square again.', 3, None)) # Links to scene 3

        print("Data inserted successfully.")
    except Error as e:
        print(e)

if __name__ == '__main__':
    conn = create_connection()
    if conn:
        insert_data(conn)
        conn.close()