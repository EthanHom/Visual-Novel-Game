import os
from db_manager import DatabaseManager
from backend_operations import BackendOperations
from game_engine import GameEngine

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def initialize_database():
    """Initialize database with schema and sample data"""
    print("=== Initializing Database ===")
    db = DatabaseManager()
    conn = db.connect()

    if conn is None:
        print("Failed to connect to database; aborting initialization.")
        return

    schema_path = os.path.join(BASE_DIR, "database", "schema.sql")
    sample_path = os.path.join(BASE_DIR, "database", "sample_data.sql")

    print("Creating tables...")
    db.execute_script(schema_path)

    print("Loading sample data...")
    db.execute_script(sample_path)

    db.disconnect()
    print("Database initialized successfully!\n")


def demo_backend_operations():
    """Demonstrate backend/designer operations"""
    print("=== Backend Operations Demo ===")
    db = DatabaseManager()
    db.connect()
    backend = BackendOperations(db)
    
    # Create operations
    print("\n--- Creating New Character ---")
    new_char_id = backend.create_character('Phoenix', 'FF00FF')
    
    print("\n--- Reading All Characters ---")
    characters = backend.read_all_characters()
    for char in characters:
        print(f"ID: {char['char_id']}, Name: {char['char_name']}, Color: {char['text_color']}")
    
    print("\n--- Updating Character ---")
    backend.update_character(new_char_id, text_color='00FF00')
    
    print("\n--- Reading Updated Character ---")
    updated_char = backend.read_character(new_char_id)
    print(f"Updated - ID: {updated_char['char_id']}, Name: {updated_char['char_name']}, Color: {updated_char['text_color']}")
    
    print("\n--- Creating New Scene ---")
    new_scene_id = backend.create_scene('New Investigation', 2, None)
    
    print("\n--- Reading All Scenes ---")
    scenes = backend.read_all_scenes()
    for scene in scenes:
        print(f"ID: {scene['scene_id']}, Name: {scene['name']}, Location: {scene['location_id']}")
    
    db.disconnect()
    print("\nBackend operations completed!\n")

def demo_game_engine():
    """Demonstrate game engine/player operations"""
    print("=== Game Engine Demo ===")
    db = DatabaseManager()
    db.connect()
    engine = GameEngine(db)
    
    print("\n--- Starting New Game ---")
    scene_data = engine.start_new_game(1)
    
    if scene_data:
        print(f"Scene: {scene_data['scene']['name']}")
        print(f"Location: {scene_data['location']['name']}")
        print(f"Background: {scene_data['location']['bg_path']}")
        print(f"Number of lines: {len(scene_data['lines'])}")
        
        print("\n--- Displaying Dialogue ---")
        for i, line in enumerate(scene_data['lines']):
            print(f"\n[Line {i+1}]")
            print(f"Speaker: {line['char_name']} (Expression: {line['expression']})")
            print(f"Content: {line['content']}")
            
            # Check for choices
            if line['choice_id']:
                choices = engine.get_choices(line['choice_id'])
                print("\nChoices available:")
                for choice in choices:
                    print(f"  {choice['decision_id']}: {choice['choice_text']}")
        
        print("\n--- Advancing Dialogue ---")
        next_line = engine.advance_dialogue()
        if next_line:
            print(f"Next line: {next_line['content']}")
        
        print("\n--- Saving Game ---")
        engine.save_game()
        
        print("\n--- Loading Game ---")
        loaded_scene = engine.load_game()
        if loaded_scene:
            print(f"Loaded scene: {loaded_scene['scene']['name']}")
    
    db.disconnect()
    print("\nGame engine demo completed!\n")

def interactive_game_demo():
    """Interactive game playthrough"""
    print("=== Interactive Game Demo ===")
    db = DatabaseManager()
    db.connect()
    engine = GameEngine(db)
    
    # Start game
    scene_data = engine.start_new_game(1)
    
    while scene_data:
        print(f"\n{'='*60}")
        print(f"Scene: {scene_data['scene']['name']}")
        print(f"Location: {scene_data['location']['name']}")
        print(f"{'='*60}\n")
        
        # Display all lines in scene
        for line in scene_data['lines']:
            print(f"\n[{line['char_name']}] ({line['expression']})")
            print(f"{line['content']}")
            input("\nPress Enter to continue...")
            
            # Check for choices at this line
            if line['choice_id']:
                choices = engine.get_choices(line['choice_id'])
                print("\n--- Make a choice ---")
                for choice in choices:
                    print(f"{choice['decision_id']}: {choice['choice_text']}")
                
                while True:
                    try:
                        choice_input = int(input("\nEnter choice number: "))
                        scene_data = engine.make_choice(choice_input)
                        break
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                    except:
                        print("Invalid choice. Try again.")
                break
        else:
            # No choices, move to next scene
            next_scene_id = scene_data['scene']['next_scene_default']
            if next_scene_id:
                scene_data = engine.load_scene(next_scene_id)
            else:
                print("\n=== Game Complete! ===")
                break
    
    db.disconnect()

def main():
    """Main program"""
    print("Visual Novel Game")
    print("=" * 60)
    
    while True:
        print("\nSelect an option:")
        print("1. Initialize Database")
        print("2. Demo Backend Operations (Designer)")
        print("3. Demo Game Engine (Player)")
        print("4. Interactive Game Demo")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ")
        
        if choice == '1':
            initialize_database()
        elif choice == '2':
            demo_backend_operations()
        elif choice == '3':
            demo_game_engine()
        elif choice == '4':
            interactive_game_demo()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
