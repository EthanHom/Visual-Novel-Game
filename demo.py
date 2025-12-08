import sqlite3
import os
# Import your existing modules
from create_schema import create_connection, create_all_tables, DATABASE_FILE
from insert_data import insert_data
import queries as q

def run_full_demo():
    print("=== INITIALIZING DATABASE ===")
    # 1. Reset Database
    if os.path.exists(DATABASE_FILE):
        os.remove(DATABASE_FILE)
    
    conn = create_connection()
    if conn is None:
        return

    create_all_tables(conn)
    insert_data(conn)
    print("Database ready.\n")

    print("=== TESTING ALL 25 QUERIES ===\n")

    # --- BACKEND USE CASES (1-20) ---

    print("--- 1. INSERT: Add new character ---")
    new_char_id = q.add_character(conn, 'Test Character', '123456')
    print(f"Result: Created Character ID {new_char_id}")

    print("\n--- 2. READ: Get all characters ---")
    chars = q.get_all_characters(conn)
    for c in chars: print(c)

    print("\n--- 3. UPDATE: Update character name ---")
    q.update_character_name(conn, new_char_id, 'Updated Name')
    print(f"Result: Character {new_char_id} name changed to 'Updated Name'")
    # Verify
    print(f"Verify: {q.fetch_all(conn, 'SELECT char_name FROM Characters WHERE char_id=?', (new_char_id,))}")

    print("\n--- 4. DELETE: Delete character ---")
    q.delete_character(conn, new_char_id)
    print(f"Result: Deleted Character ID {new_char_id}")

    print("\n--- 5. INSERT: Add new sprite ---")
    # Adding a sprite for Maya (ID 2)
    new_sprite_id = q.add_sprite(conn, 2, 3, 'sad', '/img/maya_sad.png')
    print(f"Result: Created Sprite ID {new_sprite_id} for Char ID 2")

    print("\n--- 6. READ: Get sprites for character ---")
    sprites = q.get_sprites_for_character(conn, 2)
    for s in sprites: print(s)

    print("\n--- 7. INSERT: Add new location ---")
    new_loc_id = q.add_location(conn, 'Secret Lab', '/img/lab.png')
    print(f"Result: Created Location ID {new_loc_id}")

    print("\n--- 8. READ: Get all locations ---")
    locs = q.get_all_locations(conn)
    for l in locs: print(l)

    print("\n--- 9. INSERT: Add new scene ---")
    new_scene_id = q.add_scene(conn, 'Chapter 2: The Lab', new_loc_id)
    print(f"Result: Created Scene ID {new_scene_id}")

    print("\n--- 10. UPDATE: Assign location to scene ---")
    # Move scene to Library (ID 1)
    q.update_scene_location(conn, new_scene_id, 1)
    print(f"Result: Moved Scene {new_scene_id} to Location ID 1")

    print("\n--- 11. INSERT: Add new line of dialogue ---")
    # Add line to new scene, speaker Detective (ID 3)
    new_line_id = q.add_dialogue_line(conn, new_scene_id, 3, 1, "This is a test line.")
    print(f"Result: Created Line ID {new_line_id}")

    print("\n--- 12. DELETE: Delete a line of dialogue ---")
    q.delete_dialogue_line(conn, new_line_id)
    print(f"Result: Deleted Line ID {new_line_id}")

    print("\n--- 13. INSERT: Add new choice option ---")
    # Choice Group 99, links to Scene 1
    new_decision_id = q.add_choice(conn, 99, "Test Choice", 1) 
    print(f"Result: Created Decision ID {new_decision_id}")

    print("\n--- 14. INSERT: Add new event ---")
    new_event_id = q.add_event(conn, "Game Over")
    print(f"Result: Created Event ID {new_event_id}")

    print("\n--- 15. UPDATE: Update event status ---")
    q.update_event_obtained(conn, new_event_id, True)
    print(f"Result: Event {new_event_id} set to True")

    print("\n--- 16. READ: Get scenes at location ---")
    # Check scenes at Location 1 (The Library)
    scenes = q.get_scenes_at_location(conn, 1)
    print(f"Scenes at Library: {scenes}")

    print("\n--- 17. DELETE: Delete all lines from a scene ---")
    q.delete_lines_from_scene(conn, new_scene_id)
    print(f"Result: Cleared lines from Scene {new_scene_id}")

    print("\n--- 18. READ (AGGREGATE): Count lines for each character ---")
    counts = q.count_lines_by_character(conn)
    for count in counts: print(count)

    print("\n--- 19. READ (JOIN): Get all characters and their sprites ---")
    char_sprites = q.get_all_character_sprites(conn)
    for cs in char_sprites: print(cs)

    print("\n--- 20. READ (SUBQUERY): Find scenes with no dialogue ---")
    # Scene 3 was created in insert_data but has lines.
    # Our new_scene_id (Chapter 2) had its lines deleted in step 17.
    empty = q.get_empty_scenes(conn)
    print(f"Empty Scenes: {empty}")


    # --- FRONTEND USE CASES (21-25) ---

    print("\n\n--- 21. READ (JOIN): Get scene and location ---")
    # Checking Scene 1
    data = q.get_scene_and_location(conn, 1)
    print(f"Scene 1 Data: {data}")

    print("\n--- 22. READ (COMPLEX UNION): Get dialogue for scene ---")
    # Checking Scene 1 (contains mix of sprites and no sprites)
    dialogue = q.get_dialogue_for_scene(conn, 1)
    print("Scene 1 Dialogue:")
    for line in dialogue:
        print(f"  {line}")

    print("\n--- 23. READ: Get choices for a choice group ---")
    # Checking Choice Group 1 (created in insert_data)
    choices = q.get_choices(conn, 1)
    print(f"Choices for Group 1: {choices}")

    print("\n--- 24. READ: Get info from a selected decision ---")
    # Checking Decision 1 (Investigate Library)
    result = q.get_decision_result(conn, 1)
    print(f"Result of Decision 1: {result}")

    print("\n--- 25. READ: Check if an event has been obtained ---")
    # Checking Event 2 (Found Clue)
    status = q.check_event_status(conn, 2)
    print(f"Event 2 Status: {status}")

    conn.close()
    print("\n=== DEMO COMPLETE ===")

if __name__ == '__main__':
    run_full_demo()