from db_manager import DatabaseManager
import json
import os

class GameEngine:
    """Handles player/frontend operations - game playback"""
    
    def __init__(self, db_manager):
        """Initialize with database manager"""
        self.db = db_manager
        self.current_scene_id = None
        self.current_line_index = 0
        self.save_file_path = 'saves/save_game.json'
    
    # ========== GAME INITIALIZATION ==========
    
    def start_new_game(self, starting_scene_id=1):
        """Start a new game from the beginning"""
        self.current_scene_id = starting_scene_id
        self.current_line_index = 0
        print(f"New game started at scene {starting_scene_id}")
        return self.load_scene(starting_scene_id)
    
    def load_scene(self, scene_id):
        """Load a scene and return all its data"""
        # Get scene info
        sql_scene = "SELECT * FROM Scenes WHERE scene_id = ?"
        scene = self.db.execute_query(sql_scene, (scene_id,))
        if not scene:
            print(f"Scene {scene_id} not found")
            return None
        scene = scene[0]
        
        # Get location/background
        sql_location = "SELECT * FROM Locations WHERE location_id = ?"
        location = self.db.execute_query(sql_location, (scene['location_id'],))
        location = location[0] if location else None
        
        # Get all lines for this scene
        sql_lines = """
            SELECT L.*, C.char_name, C.text_color, S.path as sprite_path, S.expression
            FROM Lines L
            JOIN Characters C ON L.speaker_id = C.char_id
            LEFT JOIN Sprites S ON L.speaker_id = S.char_id AND L.expression_id = S.expression_id
            WHERE L.scene_id = ?
            ORDER BY L.sequence
        """
        lines = self.db.execute_query(sql_lines, (scene_id,))
        
        self.current_scene_id = scene_id
        self.current_line_index = 0
        
        return {
            'scene': dict(scene),
            'location': dict(location) if location else None,
            'lines': [dict(line) for line in lines]
        }
    
    # ========== DIALOGUE OPERATIONS ==========
    
    def get_current_line(self):
        """Get the current line being displayed"""
        scene_data = self.load_scene(self.current_scene_id)
        if not scene_data or not scene_data['lines']:
            return None
        
        if self.current_line_index < len(scene_data['lines']):
            return scene_data['lines'][self.current_line_index]
        return None
    
    def advance_dialogue(self):
        """Advance to the next line in the scene"""
        scene_data = self.load_scene(self.current_scene_id)
        if not scene_data or not scene_data['lines']:
            return None
        
        self.current_line_index += 1
        
        # Check if we've reached the end of the scene
        if self.current_line_index >= len(scene_data['lines']):
            print("Scene completed")
            # Check for choice or next scene
            current_line = scene_data['lines'][self.current_line_index - 1]
            if current_line['choice_id']:
                return self.get_choices(current_line['choice_id'])
            else:
                # Move to next scene if available
                next_scene = scene_data['scene']['next_scene_default']
                if next_scene:
                    return self.load_scene(next_scene)
                else:
                    print("Game completed!")
                    return None
        
        return scene_data['lines'][self.current_line_index]
    
    # ========== CHOICE OPERATIONS ==========
    
    def get_choices(self, choice_id):
        """Get all available choices for a choice point"""
        sql = "SELECT * FROM Choices WHERE choice_id = ?"
        choices = self.db.execute_query(sql, (choice_id,))
        return [dict(choice) for choice in choices] if choices else []
    
    def make_choice(self, decision_id):
        """Player makes a choice, load the next scene"""
        sql = "SELECT next_scene, event_id FROM Choices WHERE decision_id = ?"
        result = self.db.execute_query(sql, (decision_id,))
        
        if not result:
            print(f"Choice {decision_id} not found")
            return None
        
        choice = result[0]
        
        # Trigger event if associated
        if choice['event_id']:
            self.trigger_event(choice['event_id'])
        
        # Load next scene
        next_scene_id = choice['next_scene']
        if next_scene_id:
            return self.load_scene(next_scene_id)
        
        return None
    
    # ========== EVENT OPERATIONS ==========
    
    def trigger_event(self, event_id):
        """Trigger an event (set obtained_bool to 1)"""
        sql = "UPDATE Events SET obtained_bool = 1 WHERE event_id = ?"
        self.db.execute_update(sql, (event_id,))
        print(f"Event {event_id} triggered")
    
    def check_event(self, event_id):
        """Check if an event has been triggered"""
        sql = "SELECT obtained_bool FROM Events WHERE event_id = ?"
        result = self.db.execute_query(sql, (event_id,))
        if result:
            return result[0]['obtained_bool'] == 1
        return False
    
    # ========== SAVE/LOAD GAME ==========
    
    def save_game(self):
        """Save current game state to file"""
        save_data = {
            'current_scene_id': self.current_scene_id,
            'current_line_index': self.current_line_index
        }
        
        # Create saves directory if it doesn't exist
        os.makedirs('saves', exist_ok=True)
        
        try:
            with open(self.save_file_path, 'w') as f:
                json.dump(save_data, f, indent=4)
            print(f"Game saved to {self.save_file_path}")
            return True
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self):
        """Load game state from save file"""
        try:
            with open(self.save_file_path, 'r') as f:
                save_data = json.load(f)
            
            self.current_scene_id = save_data['current_scene_id']
            self.current_line_index = save_data['current_line_index']
            
            print(f"Game loaded from {self.save_file_path}")
            return self.load_scene(self.current_scene_id)
        except FileNotFoundError:
            print("No save file found")
            return None
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    # ========== UTILITY OPERATIONS ==========
    
    def get_scene_info(self):
        """Get information about the current scene"""
        sql = """
            SELECT S.scene_id, S.name as scene_name, L.name as location_name, L.bg_path
            FROM Scenes S
            JOIN Locations L ON S.location_id = L.location_id
            WHERE S.scene_id = ?
        """
        result = self.db.execute_query(sql, (self.current_scene_id,))
        return dict(result[0]) if result else None
