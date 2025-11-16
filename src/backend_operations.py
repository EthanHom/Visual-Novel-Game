from db_manager import DatabaseManager

class BackendOperations:
    """Handles backend/designer operations - CRUD for all tables"""
    
    def __init__(self, db_manager):
        """Initialize with database manager"""
        self.db = db_manager
    
    # ========== CHARACTER OPERATIONS ==========
    
    def create_character(self, char_name, text_color):
        """Create a new character"""
        sql = "INSERT INTO Characters (char_name, text_color) VALUES (?, ?)"
        char_id = self.db.execute_update(sql, (char_name, text_color))
        if char_id:
            print(f"Character created: {char_name} (ID: {char_id})")
        return char_id
    
    def read_character(self, char_id):
        """Read character by ID"""
        sql = "SELECT * FROM Characters WHERE char_id = ?"
        result = self.db.execute_query(sql, (char_id,))
        return result[0] if result else None
    
    def read_all_characters(self):
        """Read all characters"""
        sql = "SELECT * FROM Characters"
        return self.db.execute_query(sql)
    
    def update_character(self, char_id, char_name=None, text_color=None):
        """Update character information"""
        if char_name:
            sql = "UPDATE Characters SET char_name = ? WHERE char_id = ?"
            self.db.execute_update(sql, (char_name, char_id))
        if text_color:
            sql = "UPDATE Characters SET text_color = ? WHERE char_id = ?"
            self.db.execute_update(sql, (text_color, char_id))
        print(f"Character updated: ID {char_id}")
    
    def delete_character(self, char_id):
        """Delete a character"""
        sql = "DELETE FROM Characters WHERE char_id = ?"
        self.db.execute_update(sql, (char_id,))
        print(f"Character deleted: ID {char_id}")
    
    # ========== LOCATION OPERATIONS ==========
    
    def create_location(self, name, bg_path):
        """Create a new location"""
        sql = "INSERT INTO Locations (name, bg_path) VALUES (?, ?)"
        loc_id = self.db.execute_update(sql, (name, bg_path))
        if loc_id:
            print(f"Location created: {name} (ID: {loc_id})")
        return loc_id
    
    def read_location(self, location_id):
        """Read location by ID"""
        sql = "SELECT * FROM Locations WHERE location_id = ?"
        result = self.db.execute_query(sql, (location_id,))
        return result[0] if result else None
    
    def read_all_locations(self):
        """Read all locations"""
        sql = "SELECT * FROM Locations"
        return self.db.execute_query(sql)
    
    def update_location(self, location_id, name=None, bg_path=None):
        """Update location information"""
        if name:
            sql = "UPDATE Locations SET name = ? WHERE location_id = ?"
            self.db.execute_update(sql, (name, location_id))
        if bg_path:
            sql = "UPDATE Locations SET bg_path = ? WHERE location_id = ?"
            self.db.execute_update(sql, (bg_path, location_id))
        print(f"Location updated: ID {location_id}")
    
    def delete_location(self, location_id):
        """Delete a location"""
        sql = "DELETE FROM Locations WHERE location_id = ?"
        self.db.execute_update(sql, (location_id,))
        print(f"Location deleted: ID {location_id}")
    
    # ========== SCENE OPERATIONS ==========
    
    def create_scene(self, name, location_id, next_scene_default=None):
        """Create a new scene"""
        sql = "INSERT INTO Scenes (name, location_id, next_scene_default) VALUES (?, ?, ?)"
        scene_id = self.db.execute_update(sql, (name, location_id, next_scene_default))
        if scene_id:
            print(f"Scene created: {name} (ID: {scene_id})")
        return scene_id
    
    def read_scene(self, scene_id):
        """Read scene by ID"""
        sql = "SELECT * FROM Scenes WHERE scene_id = ?"
        result = self.db.execute_query(sql, (scene_id,))
        return result[0] if result else None
    
    def read_all_scenes(self):
        """Read all scenes"""
        sql = "SELECT * FROM Scenes"
        return self.db.execute_query(sql)
    
    def update_scene(self, scene_id, name=None, location_id=None, next_scene_default=None):
        """Update scene information"""
        if name:
            sql = "UPDATE Scenes SET name = ? WHERE scene_id = ?"
            self.db.execute_update(sql, (name, scene_id))
        if location_id:
            sql = "UPDATE Scenes SET location_id = ? WHERE location_id = ?"
            self.db.execute_update(sql, (location_id, scene_id))
        if next_scene_default is not None:
            sql = "UPDATE Scenes SET next_scene_default = ? WHERE scene_id = ?"
            self.db.execute_update(sql, (next_scene_default, scene_id))
        print(f"Scene updated: ID {scene_id}")
    
    def delete_scene(self, scene_id):
        """Delete a scene"""
        sql = "DELETE FROM Scenes WHERE scene_id = ?"
        self.db.execute_update(sql, (scene_id,))
        print(f"Scene deleted: ID {scene_id}")
    
    # ========== SPRITE OPERATIONS ==========
    
    def create_sprite(self, char_id, path, expression_id, expression):
        """Create a new sprite"""
        sql = "INSERT INTO Sprites (char_id, path, expression_id, expression) VALUES (?, ?, ?, ?)"
        sprite_id = self.db.execute_update(sql, (char_id, path, expression_id, expression))
        if sprite_id:
            print(f"Sprite created for char_id {char_id} (ID: {sprite_id})")
        return sprite_id
    
    def read_sprite(self, sprite_id):
        """Read sprite by ID"""
        sql = "SELECT * FROM Sprites WHERE sprite_id = ?"
        result = self.db.execute_query(sql, (sprite_id,))
        return result[0] if result else None
    
    def read_sprites_by_character(self, char_id):
        """Read all sprites for a character"""
        sql = "SELECT * FROM Sprites WHERE char_id = ?"
        return self.db.execute_query(sql, (char_id,))
    
    def update_sprite(self, sprite_id, path=None, expression=None):
        """Update sprite information"""
        if path:
            sql = "UPDATE Sprites SET path = ? WHERE sprite_id = ?"
            self.db.execute_update(sql, (path, sprite_id))
        if expression:
            sql = "UPDATE Sprites SET expression = ? WHERE sprite_id = ?"
            self.db.execute_update(sql, (expression, sprite_id))
        print(f"Sprite updated: ID {sprite_id}")
    
    def delete_sprite(self, sprite_id):
        """Delete a sprite"""
        sql = "DELETE FROM Sprites WHERE sprite_id = ?"
        self.db.execute_update(sql, (sprite_id,))
        print(f"Sprite deleted: ID {sprite_id}")
    
    # ========== LINE/DIALOGUE OPERATIONS ==========
    
    def create_line(self, content, scene_id, speaker_id, expression_id, sequence, choice_id=None):
        """Create a new dialogue line"""
        sql = """INSERT INTO Lines (content, scene_id, speaker_id, expression_id, sequence, choice_id) 
                 VALUES (?, ?, ?, ?, ?, ?)"""
        line_id = self.db.execute_update(sql, (content, scene_id, speaker_id, expression_id, sequence, choice_id))
        if line_id:
            print(f"Line created for scene {scene_id} (ID: {line_id})")
        return line_id
    
    def read_line(self, line_id):
        """Read line by ID"""
        sql = "SELECT * FROM Lines WHERE line_id = ?"
        result = self.db.execute_query(sql, (line_id,))
        return result[0] if result else None
    
    def read_lines_by_scene(self, scene_id):
        """Read all lines for a scene, ordered by sequence"""
        sql = "SELECT * FROM Lines WHERE scene_id = ? ORDER BY sequence"
        return self.db.execute_query(sql, (scene_id,))
    
    def update_line(self, line_id, content=None, sequence=None):
        """Update line information"""
        if content:
            sql = "UPDATE Lines SET content = ? WHERE line_id = ?"
            self.db.execute_update(sql, (content, line_id))
        if sequence is not None:
            sql = "UPDATE Lines SET sequence = ? WHERE line_id = ?"
            self.db.execute_update(sql, (sequence, line_id))
        print(f"Line updated: ID {line_id}")
    
    def delete_line(self, line_id):
        """Delete a line"""
        sql = "DELETE FROM Lines WHERE line_id = ?"
        self.db.execute_update(sql, (line_id,))
        print(f"Line deleted: ID {line_id}")
    
    # ========== CHOICE OPERATIONS ==========
    
    def create_choice(self, choice_id, next_scene, choice_text, event_id=None):
        """Create a new choice"""
        sql = """INSERT INTO Choices (choice_id, next_scene, event_id, choice_text) 
                 VALUES (?, ?, ?, ?)"""
        decision_id = self.db.execute_update(sql, (choice_id, next_scene, event_id, choice_text))
        if decision_id:
            print(f"Choice created (ID: {decision_id})")
        return decision_id
    
    def read_choice(self, decision_id):
        """Read choice by decision ID"""
        sql = "SELECT * FROM Choices WHERE decision_id = ?"
        result = self.db.execute_query(sql, (decision_id,))
        return result[0] if result else None
    
    def read_choices_by_choice_id(self, choice_id):
        """Read all choices with the same choice_id (multiple options)"""
        sql = "SELECT * FROM Choices WHERE choice_id = ?"
        return self.db.execute_query(sql, (choice_id,))
    
    def update_choice(self, decision_id, next_scene=None, choice_text=None):
        """Update choice information"""
        if next_scene is not None:
            sql = "UPDATE Choices SET next_scene = ? WHERE decision_id = ?"
            self.db.execute_update(sql, (next_scene, decision_id))
        if choice_text:
            sql = "UPDATE Choices SET choice_text = ? WHERE decision_id = ?"
            self.db.execute_update(sql, (choice_text, decision_id))
        print(f"Choice updated: ID {decision_id}")
    
    def delete_choice(self, decision_id):
        """Delete a choice"""
        sql = "DELETE FROM Choices WHERE decision_id = ?"
        self.db.execute_update(sql, (decision_id,))
        print(f"Choice deleted: ID {decision_id}")
    
    # ========== EVENT OPERATIONS ==========
    
    def create_event(self, name, obtained_bool=0):
        """Create a new event"""
        sql = "INSERT INTO Events (name, obtained_bool) VALUES (?, ?)"
        event_id = self.db.execute_update(sql, (name, obtained_bool))
        if event_id:
            print(f"Event created: {name} (ID: {event_id})")
        return event_id
    
    def read_event(self, event_id):
        """Read event by ID"""
        sql = "SELECT * FROM Events WHERE event_id = ?"
        result = self.db.execute_query(sql, (event_id,))
        return result[0] if result else None
    
    def update_event(self, event_id, obtained_bool=None, name=None):
        """Update event information"""
        if obtained_bool is not None:
            sql = "UPDATE Events SET obtained_bool = ? WHERE event_id = ?"
            self.db.execute_update(sql, (obtained_bool, event_id))
        if name:
            sql = "UPDATE Events SET name = ? WHERE event_id = ?"
            self.db.execute_update(sql, (name, event_id))
        print(f"Event updated: ID {event_id}")
    
    def delete_event(self, event_id):
        """Delete an event"""
        sql = "DELETE FROM Events WHERE event_id = ?"
        self.db.execute_update(sql, (event_id,))
        print(f"Event deleted: ID {event_id}")
