
import sqlite3
from sqlite3 import Error
from typing import Optional, List, Tuple, Dict, Any
from nicegui import ui, run

DATABASE_FILE = "visual_novel_engine.db"
class CRUDManager:
    """
    Manages all Create, Read, Update, and Delete operations for the
    Visual Novel Engine's SQLite database.
    """

    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file

    def _execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None,
        fetch_one: bool = False,
        fetch_all: bool = False,
        commit: bool = False,
    ) -> Optional[Any]:
        """Internal method to safely connect, execute a query, and handle the connection."""
        conn = None
        result = None
        try:
            conn = sqlite3.connect(self.db_file)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()

            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if commit:
                conn.commit()
                # Return lastrowid for INSERTS, rowcount for others
                if query.lstrip().upper().startswith("INSERT"):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount

            if fetch_one:
                result = cursor.fetchone()
                if result:
                    result = dict(result)
            elif fetch_all:
                result = [dict(row) for row in cursor.fetchall()]

        except Error as e:
            print(f"Database Error: {e}")
            result = None
        finally:
            if conn:
                conn.close()
        return result

    # --- Character CRUD ---

    def create_character(self, char_name: str, text_color: str = "FFFFFF") -> Optional[int]:
        """Adds a new character."""
        sql = "INSERT INTO Characters (char_name, text_color) VALUES (?, ?)"
        return self._execute_query(sql, (char_name, text_color), commit=True)

    def get_all_characters(self) -> List[Dict[str, Any]]:
        """Retrieves all characters."""
        sql = "SELECT char_id, char_name, text_color FROM Characters ORDER BY char_id DESC"
        return self._execute_query(sql, fetch_all=True) or []

    def delete_character(self, char_id: int) -> bool:
        """Deletes a character by ID. Returns True if a row was deleted."""
        sql = "DELETE FROM Characters WHERE char_id = ?"
        affected = self._execute_query(sql, (char_id,), commit=True)
        return bool(affected)
    
    # --- Location CRUD (Needed for Scenes dropdown) ---

    def create_location(self, name: str, bg_path: str) -> Optional[int]:
        """Adds a new location."""
        sql = "INSERT INTO Locations (name, bg_path) VALUES (?, ?)"
        return self._execute_query(sql, (name, bg_path), commit=True)

    def get_all_locations(self) -> List[Dict[str, Any]]:
        """Retrieves all locations."""
        sql = "SELECT location_id, name, bg_path FROM Locations ORDER BY location_id ASC"
        return self._execute_query(sql, fetch_all=True) or []
    
    def delete_location(self, location_id: int) -> bool:
        """Deletes a location by ID."""
        sql = "DELETE FROM Locations WHERE location_id = ?"
        affected = self._execute_query(sql, (location_id,), commit=True)
        return bool(affected)

    # --- Scene CRUD ---

    def create_scene(self, name: str, location_id: int, next_scene_default: Optional[int] = None) -> Optional[int]:
        """Adds a new scene."""
        sql = "INSERT INTO Scenes (name, location_id, next_scene_default) VALUES (?, ?, ?)"
        params = (name, location_id, next_scene_default)
        return self._execute_query(sql, params, commit=True)
    
    def get_all_scenes_with_location_names(self) -> List[Dict[str, Any]]:
        """Retrieves all scenes, joining with location names."""
        sql = """
        SELECT
            S.scene_id, S.name AS scene_name, S.next_scene_default,
            L.location_id, L.name AS location_name, L.bg_path
        FROM Scenes S
        LEFT JOIN Locations L ON S.location_id = L.location_id
        ORDER BY S.scene_id DESC;
        """
        return self._execute_query(sql, fetch_all=True) or []
    
    def delete_scene(self, scene_id: int) -> bool:
        """Deletes a scene by ID."""
        sql = "DELETE FROM Scenes WHERE scene_id = ?"
        affected = self._execute_query(sql, (scene_id,), commit=True)
        return bool(affected)
