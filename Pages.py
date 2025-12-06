import sqlite3
from sqlite3 import Error
from typing import Optional, List, Tuple, Dict, Any
from nicegui import ui, run, events
import re
from pathlib import Path

# --- 1. Database Configuration and Schema Setup (From User Prompt) ---

DATABASE_FILE = "visual_novel_engine.db"
UPLOAD_DIR = Path('assets')


def create_connection():
    """Create a database connection to the SQLite database specified by DATABASE_FILE."""
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
    """Create a table from the create_table_sql statement."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_all_tables(conn):
    """Creates all tables for the Visual Novel Engine database."""

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

    table_sqls = [
        sql_create_locations_table,
        sql_create_characters_table,
        # Other tables (for later expansion)
        """CREATE TABLE IF NOT EXISTS Events (
            event_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            obtained_bool BOOLEAN NOT NULL DEFAULT 0
        );""",
        """CREATE TABLE IF NOT EXISTS Scenes (
            scene_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            location_id INTEGER,
            next_scene_default INTEGER,
            FOREIGN KEY (location_id) REFERENCES Locations (location_id) ON DELETE SET NULL,
            FOREIGN KEY (next_scene_default) REFERENCES Scenes (scene_id) ON DELETE SET NULL
        );""",
        """CREATE TABLE IF NOT EXISTS Sprites (
            sprite_id INTEGER PRIMARY KEY,
            char_id INTEGER NOT NULL,
            expression_id INTEGER NOT NULL,
            expression TEXT NOT NULL,
            path TEXT NOT NULL,
            FOREIGN KEY (char_id) REFERENCES Characters (char_id) ON DELETE CASCADE
        );""",
        """CREATE TABLE IF NOT EXISTS Choices (
            decision_id INTEGER PRIMARY KEY,
            choice_id INTEGER NOT NULL,
            decision_text TEXT NOT NULL,
            next_scene INTEGER,
            event_id INTEGER,
            FOREIGN KEY (next_scene) REFERENCES Scenes (scene_id) ON DELETE SET NULL,
            FOREIGN KEY (event_id) REFERENCES Events (event_id) ON DELETE SET NULL
        );""",
        """CREATE TABLE IF NOT EXISTS Lines (
            line_id INTEGER PRIMARY KEY,
            scene_id INTEGER NOT NULL,
            speaker_id INTEGER NOT NULL,
            sequence INTEGER NOT NULL,
            content TEXT NOT NULL,
            sprite_id INTEGER,
            expression_id INTEGER,
            choice_id INTEGER,
            FOREIGN KEY (scene_id) REFERENCES Scenes (scene_id) ON DELETE CASCADE,
            FOREIGN KEY (speaker_id) REFERENCES Characters (char_id) ON DELETE CASCADE,
            FOREIGN KEY (sprite_id) REFERENCES Sprites (sprite_id) ON DELETE SET NULL
        );""",
    ]

    if conn is not None:
        for sql in table_sqls:
            create_table(conn, sql)
        print("All tables created successfully.")
    else:
        print("Error! cannot create the database connection.")


# --- 2. CRUDManager Class (Expanded) ---

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


# Initialize DB and Manager
conn = create_connection()
if conn:
    create_all_tables(conn)
    conn.close()
CRUD_MANAGER = CRUDManager()


# --- 3. NiceGUI Page Content Functions ---

def characters_content():
    """Content function for the Characters page."""
    # Ensure variables are accessible within this function's scope
    character_table = None
    name_input = None
    color_input = None
    color_preview_label = None
    
    CHAR_COLUMNS = [
        {"name": "char_id", "label": "ID", "field": "char_id", "sortable": True},
        {"name": "char_name", "label": "Name", "field": "char_name", "sortable": True, "align": "left"},
        {"name": "text_color", "label": "Color (Hex)", "field": "text_color", "sortable": True, "align": "center"},
        {"name": "actions", "label": "Actions", "field": "actions", "align": "right"},
    ]

    # --- Handlers & Helpers ---

    def refresh_characters():
        data = CRUD_MANAGER.get_all_characters()
        character_table.rows = data
        ui.notify(f"Refreshed: {len(data)} characters loaded.", color="primary")

    def delete_character_worker(char_id: int, char_name: str):
        if CRUD_MANAGER.delete_character(char_id):
            # FIX: Explicitly enter context for robustness
            with character_table:
                ui.notify(f'Character "{char_name}" (ID: {char_id}) deleted.', color="warning")
            refresh_characters()
        else:
            with character_table:
                ui.notify(f"Failed to delete character {char_id}.", color="negative")

    def on_edit_character(e):
        row = e.args  # props.row from template
        # FIX: Explicitly enter context for robustness
        with character_table:
            ui.notify(
                f"Edit action triggered for Character ID: {row['char_id']} ({row['char_name']}). (Not implemented)",
                color="info",
            )

    def on_delete_character(e):
        row = e.args  # props.row from template
        # Run deletion asynchronously to avoid blocking the UI, but the handler is sync
        run.io_bound(delete_character_worker, row["char_id"], row["char_name"]) 

    def add_character():
        if not name_input.value:
            ui.notify("Character Name cannot be empty!", color="red")
            return

        color = color_input.value.strip().lstrip("#").upper()
        if len(color) not in [3, 6]:
            ui.notify(
                "Invalid color format. Use RRGGBB or RGB hex codes (e.g., FF00CC).",
                color="orange",
            )
            return

        new_id = CRUD_MANAGER.create_character(name_input.value, color)

        if new_id:
            ui.notify(
                f'Character "{name_input.value}" added with ID: {new_id}',
                color="green",
            )
            name_input.value = ""
            color_input.value = "FFFFFF"
            color_preview_label.style("color: #FFFFFF")
            refresh_characters()
        else:
            ui.notify("Failed to add character.", color="negative")

    def update_color_preview():
        color = color_input.value.strip().lstrip("#")
        color_preview_label.style(f"color: #{color if color else 'FFFFFF'}")

    # --- Layout ---
    with ui.row().classes("w-full max-w-7xl mx-auto p-4 gap-8"):

        # --- Character Creation Card ---
        with ui.card().classes("w-full lg:w-1/3 shadow-xl"):
            ui.label("Add New Character").classes("text-xl font-semibold text-indigo-700")
            ui.separator()

            name_input = ui.input(
                label="Character Name", placeholder="e.g., Kaito"
            ).classes("w-full")

            with ui.row().classes("w-full items-center"):
                color_input = ui.input(
                    label="Text Color (Hex)",
                    value="FFFFFF",
                    placeholder="FFFFFF",
                    validation={
                        "Invalid Hex": lambda v: len(v.strip().lstrip("#")) in [3, 6]
                    },
                ).classes("flex-grow")

                color_preview_label = (
                    ui.label("Color Preview")
                    .classes("px-3 py-1 text-sm rounded-lg font-bold shadow-md")
                    .style("background-color: #222; color: #FFFFFF")
                )

                color_input.on("input", update_color_preview, throttle=0.2)

            ui.button(
                "Create Character",
                on_click=add_character,
                icon="person_add",
            ).classes("bg-green-600 hover:bg-green-700 w-full mt-4")

        # --- Character Display Table ---
        with ui.card().classes("w-full lg:w-2/3 shadow-xl"):
            ui.label("Character List").classes("text-xl font-semibold text-indigo-700")
            ui.separator()

            character_table = ui.table(
                columns=CHAR_COLUMNS,
                rows=[],
                row_key="char_id",
                pagination=20,
            ).classes("w-full")

            # Slot for action column using the Quasar template string
            character_table.add_slot(
                "body-cell-actions",
                r"""
                <q-td :props="props">
                    <q-btn
                        flat dense round icon="edit" color="blue-6"
                        @click="$parent.$emit('edit-character', props.row)"
                    />
                    <q-btn
                        flat dense round icon="delete" color="negative"
                        @click="$parent.$emit('delete-character', props.row)"
                    />
                </q-td>
            """,
            )

            character_table.on("edit-character", on_edit_character)
            character_table.on("delete-character", on_delete_character)

            # Initial data load
            refresh_characters()


def scenes_content():
    """Content function for the Scenes page."""
    
    scene_table = None
    location_dropdown = None
    scene_name_input = None

    SCENE_COLUMNS = [
        {"name": "scene_id", "label": "ID", "field": "scene_id", "sortable": True},
        {"name": "scene_name", "label": "Scene Name", "field": "scene_name", "sortable": True, "align": "left"},
        {"name": "location_name", "label": "Location", "field": "location_name", "sortable": True, "align": "left"},
        {"name": "actions", "label": "Actions", "field": "actions", "align": "right"},
    ]
    
    # --- Handlers & Helpers ---
    
    def get_location_options():
        """Fetches locations for the dropdown."""
        locations = CRUD_MANAGER.get_all_locations()
        # NiceGUI dropdown requires value: label format
        return {loc['location_id']: loc['name'] for loc in locations}
        
    def refresh_scenes():
        data = CRUD_MANAGER.get_all_scenes_with_location_names()
        scene_table.rows = data
        ui.notify(f"Refreshed: {len(data)} scenes loaded.", color="primary")
        
    def delete_scene_worker(scene_id: int, scene_name: str):
        if CRUD_MANAGER.delete_scene(scene_id):
            with scene_table:
                ui.notify(f'Scene "{scene_name}" (ID: {scene_id}) deleted.', color="warning")
            refresh_scenes()
        else:
            with scene_table:
                ui.notify(f"Failed to delete scene {scene_id}. Check related lines/choices.", color="negative")

    def on_delete_scene(e):
        row = e.args
        run.io_bound(delete_scene_worker, row["scene_id"], row["scene_name"]) 
        
    def add_scene():
        if not scene_name_input.value or not location_dropdown.value:
            ui.notify("Scene Name and Location must be selected!", color="red")
            return
            
        scene_name = scene_name_input.value
        location_id = location_dropdown.value
        
        new_id = CRUD_MANAGER.create_scene(scene_name, location_id)
        
        if new_id:
            ui.notify(f'Scene "{scene_name}" added with ID: {new_id}', color="green")
            scene_name_input.value = ""
            location_dropdown.value = None
            refresh_scenes()
        else:
            ui.notify("Failed to add scene.", color="negative")
            
    # --- Layout ---
    with ui.row().classes("w-full max-w-7xl mx-auto p-4 gap-8"):
        
        # --- Scene Creation Card ---
        with ui.card().classes("w-full lg:w-1/3 shadow-xl"):
            ui.label("Add New Scene").classes("text-xl font-semibold text-indigo-700")
            ui.separator()
            
            scene_name_input = ui.input(
                label="Scene Name", placeholder="e.g., Opening Monologue"
            ).classes("w-full")
            
            location_dropdown = ui.select(
                get_location_options(),
                label='Location (Background)'
            ).classes('w-full')
            
            ui.button(
                "Create Scene",
                on_click=add_scene,
                icon="add_circle",
            ).classes("bg-green-600 hover:bg-green-700 w-full mt-4")

        # --- Scene Display Table ---
        with ui.card().classes("w-full lg:w-2/3 shadow-xl"):
            ui.label("Scene List").classes("text-xl font-semibold text-indigo-700")
            ui.separator()

            scene_table = ui.table(
                columns=SCENE_COLUMNS,
                rows=[],
                row_key="scene_id",
                pagination=20,
            ).classes("w-full")

            # Slot for action column using the Quasar template string
            scene_table.add_slot(
                "body-cell-actions",
                r"""
                <q-td :props="props">
                    <q-btn
                        flat dense round icon="edit" color="blue-6"
                        @click="$parent.$emit('edit-scene', props.row)"
                    />
                    <q-btn
                        flat dense round icon="delete" color="negative"
                        @click="$parent.$emit('delete-scene', props.row)"
                    />
                </q-td>
            """,
            )

            # Note: Edit handler is just a placeholder for now
            scene_table.on("edit-scene", lambda e: run.io_bound(lambda: (
                ui.notify(f"Edit scene {e.args['scene_name']} (Not implemented)", color='info')
            )))
            scene_table.on("delete-scene", on_delete_scene)

            # Initial data load
            refresh_scenes()


def locations_content():
    """Content function for the Locations page."""

    # --- config / state ---
    BG_DIR = Path('assets/bgs')
    BG_DIR.mkdir(parents=True, exist_ok=True)

    location_table = None
    name_input = None
    upload_component = None

    # state for this page instance
    uploaded_bytes: bytes | None = None
    uploaded_ext: str | None = None

    LOC_COLUMNS = [
        {"name": "location_id", "label": "ID", "field": "location_id", "sortable": True},
        {"name": "name", "label": "Name", "field": "name", "sortable": True, "align": "left"},
        {"name": "bg_path", "label": "Background Path", "field": "bg_path", "align": "left"},
        {"name": "actions", "label": "Actions", "field": "actions", "align": "right"},
    ]

    # --- helpers ---

    def refresh_locations() -> None:
        data = CRUD_MANAGER.get_all_locations()
        location_table.rows = data

    async def handle_upload(e: events.UploadEventArguments) -> None:
        nonlocal uploaded_bytes, uploaded_ext

        if not e.file:
            ui.notify('No file uploaded.', color='negative')
            return

        # read file bytes
        uploaded_bytes = await e.file.read()

        # figure out extension
        original_name = e.file.name or ''
        ext = Path(original_name).suffix.lower()
        if ext not in {'.png', '.jpg', '.jpeg', '.webp'}:
            ext = '.png'  # default fallback

        uploaded_ext = ext
        ui.notify(f'File "{original_name}" uploaded (will be saved when you create the location).',
                  color='positive')

    def add_location() -> None:
        nonlocal uploaded_bytes, uploaded_ext

        name = (name_input.value or '').strip()

        if not name:
            ui.notify('Please enter a location name.', color='negative')
            return
        if uploaded_bytes is None or uploaded_ext is None:
            ui.notify('Please upload a background image first.', color='negative')
            return

        # sanitize name for filename
        safe_name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
        filename = f'{safe_name}{uploaded_ext}'
        target_path = BG_DIR / filename

        # avoid overwriting existing file
        counter = 1
        while target_path.exists():
            filename = f'{safe_name}_{counter}{uploaded_ext}'
            target_path = BG_DIR / filename
            counter += 1
            target_path = BG_DIR / filename

        # save file
        try:
            target_path.write_bytes(uploaded_bytes)
        except Exception as err:
            ui.notify(f'Error saving file: {err}', color='negative')
            return

        # store in DB
        db_path = str(target_path)  # you can make this relative if you prefer
        new_id = CRUD_MANAGER.create_location(name, db_path)

        if new_id:
            ui.notify(f'Location "{name}" created (ID: {new_id}).', color='positive')
            # reset form state
            name_input.value = ''
            upload_component.reset()
            uploaded_bytes = None
            uploaded_ext = None
            refresh_locations()
        else:
            ui.notify('Failed to create location in database.', color='negative')

    def on_delete_location(e) -> None:
        row = e.args
        loc_id = row['location_id']
        loc_name = row['name']
        bg_path = row['bg_path']

        if CRUD_MANAGER.delete_location(loc_id):
            # try to delete the file too
            try:
                if bg_path:
                    p = Path(bg_path)
                    if p.exists():
                        p.unlink()
            except Exception as err:
                print(f'Warning: could not delete background file "{bg_path}": {err}')

            ui.notify(f'Location "{loc_name}" deleted.', color='warning')
            refresh_locations()
        else:
            ui.notify('Failed to delete location (maybe used by scenes).', color='negative')

    # --- layout ---

    with ui.row().classes('w-full max-w-7xl mx-auto p-4 gap-8'):

        # --- creation card ---
        with ui.card().classes('w-full lg:w-1/3 shadow-xl'):
            ui.label('Add New Location').classes('text-xl font-semibold text-indigo-700')
            ui.separator()

            name_input = ui.input(
                label='Location Name',
                placeholder='e.g., School Rooftop',
            ).classes('w-full')

            upload_component = ui.upload(
                label='Upload Background Image',
                auto_upload=True,
                max_files=1,
                on_upload=handle_upload,
            ).props('accept=".png,.jpg,.jpeg,.webp"').classes('w-full mt-2')

            ui.button(
                'Create Location',
                on_click=add_location,
                icon='add_location_alt',
            ).classes('bg-green-600 hover:bg-green-700 w-full mt-4')

        # --- table card ---
        with ui.card().classes('w-full lg:w-2/3 shadow-xl'):
            ui.label('Location List').classes('text-xl font-semibold text-indigo-700')
            ui.separator()

            location_table = ui.table(
                columns=LOC_COLUMNS,
                rows=[],
                row_key='location_id',
                pagination=20,
            ).classes('w-full')

            location_table.add_slot(
                'body-cell-actions',
                r"""
                <q-td :props="props">
                    <q-btn
                        flat dense round icon="delete" color="negative"
                        @click="$parent.$emit('delete-location', props.row)"
                    />
                </q-td>
                """,
            )

            location_table.on('delete-location', on_delete_location)

            refresh_locations()


# --- 4. Main Page & Navigation Setup ---

@ui.page('/')
@ui.page('/characters')
async def characters_page():
    ui.add_head_html('<title>VN Database Admin - Characters</title>')
    with ui.header().classes("items-center justify-between text-white bg-indigo-700"):
        ui.label("Visual Novel Engine Database Admin").classes("text-2xl font-bold")
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat round dense')
    
    with ui.left_drawer() as left_drawer:
        ui.label('Menu').classes('text-lg font-bold p-4')
        ui.separator()
        ui.link('Characters', characters_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Scenes', scenes_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Locations', locations_page).classes('p-2 w-full hover:bg-indigo-100') # NEW LINK
        ui.separator()
        ui.label('Note: Add Locations first!').classes('text-xs text-gray-500 p-2')
        
    characters_content()
    

@ui.page('/scenes')
async def scenes_page():
    ui.add_head_html('<title>VN Database Admin - Scenes</title>')
    with ui.header().classes("items-center justify-between text-white bg-indigo-700"):
        ui.label("Visual Novel Engine Database Admin").classes("text-2xl font-bold")
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat round dense')
    
    with ui.left_drawer() as left_drawer:
        ui.label('Menu').classes('text-lg font-bold p-4')
        ui.separator()
        ui.link('Characters', characters_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Scenes', scenes_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Locations', locations_page).classes('p-2 w-full hover:bg-indigo-100') # NEW LINK
        ui.separator()
        ui.label('Note: Add Locations first!').classes('text-xs text-gray-500 p-2')

    scenes_content()
    
@ui.page('/locations') # NEW PAGE
async def locations_page():
    ui.add_head_html('<title>VN Database Admin - Locations</title>')
    with ui.header().classes("items-center justify-between text-white bg-indigo-700"):
        ui.label("Visual Novel Engine Database Admin").classes("text-2xl font-bold")
        ui.button(icon='menu', on_click=lambda: left_drawer.toggle()).props('flat round dense')
    
    with ui.left_drawer() as left_drawer:
        ui.label('Menu').classes('text-lg font-bold p-4')
        ui.separator()
        ui.link('Characters', characters_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Scenes', scenes_page).classes('p-2 w-full hover:bg-indigo-100')
        ui.link('Locations', locations_page).classes('p-2 w-full hover:bg-indigo-100') # NEW LINK
        ui.separator()
        ui.label('Note: Add Locations first!').classes('text-xs text-gray-500 p-2')

    locations_content()

# Run the NiceGUI app
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(title="VN Database Admin", reload=False, port=8080)