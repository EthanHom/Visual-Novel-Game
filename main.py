import sqlite3
import os
from create_schema import create_connection, create_all_tables, DATABASE_FILE
from insert_data import insert_data
import queries as q

def run():
    """ Running: create, populate, and query """
    
    # Delete old database file if it exists
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
        print(f"Removed old database file: {DATABASE_FILE}")

    # Create connection and tables
    conn = create_connection()
    if conn is None:
        return

    create_all_tables(conn)
    
    # Populate with data
    insert_data(conn)

    print("\n--- DATABASE CREATED AND POPULATED ---")

    # --- SIMULATE BACKEND USE ---
    print("\n--- BACKEND QUERIES ---")
    
    # 1. Add a new character
    print("\nAdding new character 'Apollo'...")
    new_char_id = q.add_character(conn, 'Apollo', 'FFD700')
    print(f"New character ID: {new_char_id}")

    # 2. Get all characters
    print("\nCurrent Characters:")
    all_chars = q.get_all_characters(conn)
    for char in all_chars:
        print(f"  ID: {char[0]}, Name: {char[1]}, Color: {char[2]}")
        
    # 3. Update character
    print(f"\nUpdating character {new_char_id} to 'Yuki (Revised)'...")
    q.update_character_name(conn, new_char_id, 'Yuki (Revised)')
    
    # 4. Get all characters again
    print("\nUpdated Characters:")
    all_chars = q.get_all_characters(conn)
    for char in all_chars:
        print(f"  ID: {char[0]}, Name: {char[1]}, Color: {char[2]}")

    # 5. Get line counts
    print("\nLine Counts per Character:")
    counts = q.count_lines_by_character(conn)
    for count in counts:
        print(f"  {count[0]}: {count[1]} lines")

    # 6. Delete character
    print(f"\nDeleting 'Yuki (Revised)'...")
    q.delete_character(conn, new_char_id)
    print("Characters after deletion:")
    all_chars = q.get_all_characters(conn)
    for char in all_chars:
        print(f"  ID: {char[0]}, Name: {char[1]}")


    # --- GAMEPLAY ---
    print("\n--- GAMEPLAY QUERIES ---")
    
    current_scene_id = 1
    
    # 1. Start game, get scene 1
    print(f"\nLoading Scene {current_scene_id}...")
    scene_info = q.get_scene_and_location(conn, current_scene_id)
    print(f"Scene: {scene_info[0][0]}, Background: {scene_info[0][1]}")

    # 2. Get dialogue for scene 1
    dialogue_lines = q.get_dialogue_for_scene(conn, current_scene_id)
    
    print("\nDialogue:")
    choice_to_make = None
    for line in dialogue_lines:
        (line_id, content, seq, choice_id, char_name, color, sprite) = line
        print(f'  {char_name} (color: {color}): "{content}"')
        if sprite:
            print(f'  [Sprite: {sprite}]')
        if choice_id:
            choice_to_make = choice_id
            print(f"  [--- TRIGGER CHOICE {choice_to_make} ---]")

    # 3. Get choices
    if choice_to_make:
        print(f"\nLoading Choices for group {choice_to_make}:")
        choices = q.get_choices(conn, choice_to_make)
        for choice in choices:
            print(f"  Decision ID {choice[0]}: {choice[1]}")
        
        # 4. Make a decision (just pick the first one)
        made_decision_id = choices[0][0]
        print(f"\nPlayer chose: '{choices[0][1]}' (ID: {made_decision_id})")

        decision_result = q.get_decision_result(conn, made_decision_id)
        next_scene = decision_result[0][0]
        event_triggered = decision_result[0][1]
        
        print(f"  > This leads to Scene {next_scene}.")
        if event_triggered:
            print(f"  > This triggers Event {event_triggered}.")
            # 5. Update and check event
            q.update_event_obtained(conn, event_triggered, True)
            status = q.check_event_status(conn, event_triggered)
            print(f"  > Event {event_triggered} status is now: {status[0][0]}")

    conn.close()
    print("\nCompleted. Connection closed.")

if __name__ == '__main__':
    run()