import sqlite3
from sqlite3 import Error
from typing import Optional, List, Tuple, Dict, Any
from nicegui import ui, run, events, app
from fastapi.responses import RedirectResponse
import re
from pathlib import Path
import os

# --- 1. CONFIGURATION (ABSOLUTE PATHS) ---

# Resolve the absolute path to the folder containing this script
BASE_DIR = Path(__file__).parent.resolve()
DATABASE_FILE = str(BASE_DIR / "visual_novel_engine.db")
ASSETS_DIR = BASE_DIR / 'assets'

# Ensure directories exist
ASSETS_DIR.mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / 'bgs').mkdir(parents=True, exist_ok=True)
(ASSETS_DIR / 'sprites').mkdir(parents=True, exist_ok=True)

# *** CRITICAL: Serve assets folder to browser ***
app.add_static_files('/assets', str(ASSETS_DIR))
print(f"--- SYSTEM READY ---")
print(f"Database: {DATABASE_FILE}")
print(f"Assets:   {ASSETS_DIR}")

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    except Error as e:
        print(f"Connection Error: {e}")
    return conn

# --- 2. DATABASE MANAGER (CRUD) ---

class CRUDManager:
    def __init__(self, db_file: str = DATABASE_FILE):
        self.db_file = db_file

    def _execute_query(self, query: str, params: Optional[Tuple] = None, 
                       fetch_one: bool = False, fetch_all: bool = False, commit: bool = False) -> Optional[Any]:
        conn = None
        result = None
        try:
            conn = create_connection()
            if not conn: return None
            
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if commit:
                conn.commit()
                if query.lstrip().upper().startswith("INSERT"):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount
            
            if fetch_one:
                row = cursor.fetchone()
                result = dict(row) if row else None
            elif fetch_all:
                result = [dict(row) for row in cursor.fetchall()]
        except Error as e:
            print(f"Query Error: {e}")
            result = None
        finally:
            if conn: conn.close()
        return result

    # --- Basic CRUD ---
    def create_character(self, char_name: str, text_color: str) -> Optional[int]:
        return self._execute_query("INSERT INTO Characters (char_name, text_color) VALUES (?, ?)", (char_name, text_color), commit=True)
    def update_character(self, char_id: int, char_name: str, text_color: str) -> bool:
        return bool(self._execute_query("UPDATE Characters SET char_name=?, text_color=? WHERE char_id=?", (char_name, text_color, char_id), commit=True))
    def get_all_characters(self) -> List[Dict]:
        return self._execute_query("SELECT * FROM Characters ORDER BY char_id DESC", fetch_all=True) or []
    def delete_character(self, char_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Characters WHERE char_id = ?", (char_id,), commit=True))

    def create_location(self, name: str, bg_path: str) -> Optional[int]:
        return self._execute_query("INSERT INTO Locations (name, bg_path) VALUES (?, ?)", (name, bg_path), commit=True)
    def update_location(self, loc_id: int, name: str, bg_path: str) -> bool:
        return bool(self._execute_query("UPDATE Locations SET name=?, bg_path=? WHERE location_id=?", (name, bg_path, loc_id), commit=True))
    def get_all_locations(self) -> List[Dict]:
        return self._execute_query("SELECT * FROM Locations ORDER BY location_id ASC", fetch_all=True) or []
    def delete_location(self, location_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Locations WHERE location_id = ?", (location_id,), commit=True))

    def create_scene(self, name: str, location_id: int) -> Optional[int]:
        return self._execute_query("INSERT INTO Scenes (name, location_id) VALUES (?, ?)", (name, location_id), commit=True)
    def update_scene(self, scene_id: int, name: str, location_id: int) -> bool:
        return bool(self._execute_query("UPDATE Scenes SET name=?, location_id=? WHERE scene_id=?", (name, location_id, scene_id), commit=True))
    def get_all_scenes_joined(self) -> List[Dict]:
        sql = """SELECT S.scene_id, S.name as scene_name, L.name as location_name, S.location_id 
                 FROM Scenes S LEFT JOIN Locations L ON S.location_id = L.location_id ORDER BY S.scene_id DESC"""
        return self._execute_query(sql, fetch_all=True) or []
    def get_scene_details(self, scene_id: int) -> Dict:
        sql = """SELECT S.scene_id, S.name, L.bg_path FROM Scenes S 
                 LEFT JOIN Locations L ON S.location_id = L.location_id WHERE S.scene_id = ?"""
        return self._execute_query(sql, (scene_id,), fetch_one=True)
    def delete_scene(self, scene_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Scenes WHERE scene_id = ?", (scene_id,), commit=True))

    def create_sprite(self, char_id: int, expression: str, path: str) -> Optional[int]:
        exp_map = {'neutral': 1, 'happy': 2, 'sad': 3, 'angry': 4}
        exp_id = exp_map.get(expression.lower(), 1)
        return self._execute_query("INSERT INTO Sprites (char_id, expression_id, expression, path) VALUES (?, ?, ?, ?)", (char_id, exp_id, expression, path), commit=True)
    def update_sprite(self, sprite_id: int, char_id: int, expression: str, path: str) -> bool:
        exp_map = {'neutral': 1, 'happy': 2, 'sad': 3, 'angry': 4}
        exp_id = exp_map.get(expression.lower(), 1)
        return bool(self._execute_query("UPDATE Sprites SET char_id=?, expression_id=?, expression=?, path=? WHERE sprite_id=?", (char_id, exp_id, expression, path, sprite_id), commit=True))
    def get_all_sprites_joined(self) -> List[Dict]:
        sql = """SELECT S.sprite_id, C.char_name, S.expression, S.path, S.char_id FROM Sprites S JOIN Characters C ON S.char_id = C.char_id ORDER BY C.char_name"""
        return self._execute_query(sql, fetch_all=True) or []
    def get_sprites_by_char(self, char_id: int) -> List[Dict]:
        return self._execute_query("SELECT * FROM Sprites WHERE char_id = ?", (char_id,), fetch_all=True) or []
    def delete_sprite(self, sprite_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Sprites WHERE sprite_id = ?", (sprite_id,), commit=True))

    # --- Events ---
    def create_event(self, name: str) -> Optional[int]:
        return self._execute_query("INSERT INTO Events (name, obtained_bool) VALUES (?, 0)", (name,), commit=True)
    def update_event_name(self, event_id: int, name: str) -> bool:
        return bool(self._execute_query("UPDATE Events SET name=? WHERE event_id=?", (name, event_id), commit=True))
    def get_all_events(self) -> List[Dict]:
        return self._execute_query("SELECT * FROM Events", fetch_all=True) or []
    def delete_event(self, event_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Events WHERE event_id = ?", (event_id,), commit=True))
    def update_event_status(self, event_id: int, status: bool) -> bool:
        return bool(self._execute_query("UPDATE Events SET obtained_bool = ? WHERE event_id = ?", (status, event_id), commit=True))

    # --- Event Logic ---
    def create_event_logic(self, start_scene: int, end_scene: int, event_id: int) -> Optional[int]:
        sql = "INSERT INTO EventLogic (start_scene, end_scene, event_id) VALUES (?, ?, ?)"
        return self._execute_query(sql, (start_scene, end_scene, event_id), commit=True)
    
    def update_event_logic(self, logic_id: int, start_scene: int, end_scene: int, event_id: int) -> bool:
        return bool(self._execute_query("UPDATE EventLogic SET start_scene=?, end_scene=?, event_id=? WHERE logic_id=?", (start_scene, end_scene, event_id, logic_id), commit=True))

    def get_event_logic_for_scene(self, start_scene: int) -> List[Dict]:
        sql = """SELECT EL.logic_id, EL.start_scene, EL.end_scene, EL.event_id, E.name AS event_name, E.obtained_bool
        FROM EventLogic EL JOIN Events E ON EL.event_id = E.event_id WHERE EL.start_scene = ?"""
        return self._execute_query(sql, (start_scene,), fetch_all=True) or []

    def delete_event_logic(self, logic_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM EventLogic WHERE logic_id = ?", (logic_id,), commit=True))
    
    def get_next_scene_default(self, scene_id: int) -> Optional[int]:
        row = self._execute_query("SELECT next_scene_default FROM Scenes WHERE scene_id = ?", (scene_id,), fetch_one=True)
        if row and row.get('next_scene_default') is not None: return row['next_scene_default']
        return None

    def get_next_scene_with_event_logic(self, scene_id: int) -> Optional[int]:
        logic_row = self._execute_query(
            """SELECT COUNT(*) AS total_rules, SUM(CASE WHEN E.obtained_bool = 1 THEN 1 ELSE 0 END) AS satisfied_rules, MAX(EL.end_scene) AS end_scene 
            FROM EventLogic EL JOIN Events E ON EL.event_id = E.event_id WHERE EL.start_scene = ?""", (scene_id,), fetch_one=True)
        if logic_row and logic_row['total_rules'] > 0:
            if (logic_row['satisfied_rules'] or 0) == logic_row['total_rules'] and logic_row['end_scene']:
                return logic_row['end_scene']
        return self.get_next_scene_default(scene_id)

    # --- Choices ---
    def get_next_choice_group_id(self) -> int:
        res = self._execute_query("SELECT MAX(choice_id) as max_id FROM Choices", fetch_one=True)
        return (res['max_id'] + 1) if res and res['max_id'] else 1
    
    def create_choice_option(self, choice_group_id: int, text: str, next_scene: int, event_id: Optional[int]) -> Optional[int]:
        sql = "INSERT INTO Choices (choice_id, decision_text, next_scene, event_id) VALUES (?, ?, ?, ?)"
        return self._execute_query(sql, (choice_group_id, text, next_scene, event_id), commit=True)
    
    def update_choice_option(self, decision_id: int, text: str, next_scene: int, event_id: Optional[int]) -> bool:
        return bool(self._execute_query("UPDATE Choices SET decision_text=?, next_scene=?, event_id=? WHERE decision_id=?", (text, next_scene, event_id, decision_id), commit=True))

    def get_all_choices_grouped(self) -> List[Dict]:
        sql = """SELECT C.choice_id, C.decision_id, C.decision_text, C.next_scene, C.event_id, S.name as next_scene_name, E.name as event_name 
                 FROM Choices C LEFT JOIN Scenes S ON C.next_scene = S.scene_id LEFT JOIN Events E ON C.event_id = E.event_id ORDER BY C.choice_id"""
        return self._execute_query(sql, fetch_all=True) or []
    
    def get_choices_by_group(self, group_id: int) -> List[Dict]:
        sql = """SELECT C.*, E.name as event_name FROM Choices C LEFT JOIN Events E ON C.event_id = E.event_id WHERE C.choice_id = ?"""
        return self._execute_query(sql, (group_id,), fetch_all=True) or []

    def delete_choice_option(self, decision_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Choices WHERE decision_id = ?", (decision_id,), commit=True))

    # --- Script / Lines ---
    def get_lines_for_scene(self, scene_id: int) -> List[Dict]:
        sql = """
        SELECT L.line_id, L.sequence, L.speaker_id, L.sprite_id, C.char_name, C.text_color, L.content, S.expression, S.path as sprite_path, L.choice_id
        FROM Lines L
        JOIN Characters C ON L.speaker_id = C.char_id
        LEFT JOIN Sprites S ON L.sprite_id = S.sprite_id
        WHERE L.scene_id = ?
        ORDER BY L.sequence ASC
        """
        return self._execute_query(sql, (scene_id,), fetch_all=True) or []

    def create_line(self, scene_id: int, speaker_id: int, content: str, sprite_id: Optional[int], choice_id: Optional[int]) -> Optional[int]:
        seq = self._execute_query("SELECT MAX(sequence) as m FROM Lines WHERE scene_id=?", (scene_id,), fetch_one=True)['m']
        seq = (seq + 1) if seq else 1
        exp_id = None
        if sprite_id:
            s = self._execute_query("SELECT expression_id FROM Sprites WHERE sprite_id=?", (sprite_id,), fetch_one=True)
            if s: exp_id = s['expression_id']
        sql = """INSERT INTO Lines (scene_id, speaker_id, sequence, content, sprite_id, expression_id, choice_id) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        return self._execute_query(sql, (scene_id, speaker_id, seq, content, sprite_id, exp_id, choice_id), commit=True)
    
    def update_line(self, line_id: int, speaker_id: int, content: str, sprite_id: Optional[int]) -> bool:
        exp_id = None
        if sprite_id:
            s = self._execute_query("SELECT expression_id FROM Sprites WHERE sprite_id=?", (sprite_id,), fetch_one=True)
            if s: exp_id = s['expression_id']
        return bool(self._execute_query("UPDATE Lines SET speaker_id=?, content=?, sprite_id=?, expression_id=? WHERE line_id=?", (speaker_id, content, sprite_id, exp_id, line_id), commit=True))

    def delete_line(self, line_id: int) -> bool:
        return bool(self._execute_query("DELETE FROM Lines WHERE line_id = ?", (line_id,), commit=True))

CRUD_MANAGER = CRUDManager()

# --- 3. UI CONTENT FUNCTIONS ---

def characters_content():
    table = None
    
    def refresh(): table.rows = CRUD_MANAGER.get_all_characters()
    def add(name, color):
        if name: CRUD_MANAGER.create_character(name, color.strip().lstrip('#')); refresh()
    def delete(row): CRUD_MANAGER.delete_character(row['char_id']); refresh()
    
    def edit(row):
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Edit {row['char_name']}").classes("text-lg font-bold")
            n = ui.input("Name", value=row['char_name'])
            c = ui.color_input("Color", value=f"#{row['text_color']}")
            def save():
                CRUD_MANAGER.update_character(row['char_id'], n.value, c.value.strip().lstrip('#'))
                dialog.close(); refresh(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.row().classes("w-full gap-8"):
        with ui.card().classes("w-1/3"):
            ui.label("Add Character").classes("text-xl font-bold")
            n = ui.input("Name"); c = ui.color_input("Color", value="#FFFFFF")
            ui.button("Add", on_click=lambda: add(n.value, c.value))
        with ui.card().classes("w-2/3"):
            table = ui.table(columns=[{'name':'char_name','label':'Name','field':'char_name'}, {'name':'text_color','label':'Color','field':'text_color'}, {'name':'actions','label':'','field':'actions'}], rows=[], row_key='char_id').classes('w-full')
            table.add_slot('body-cell-actions', r'''
                <q-td :props="props">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)" />
                </q-td>''')
            table.on('del', lambda e: delete(e.args))
            table.on('edit', lambda e: edit(e.args))
    refresh()

def locations_content():
    uploaded_bytes, uploaded_ext = None, None
    table = None
    
    def refresh(): table.rows = CRUD_MANAGER.get_all_locations()
    async def handle_upload(e): nonlocal uploaded_bytes, uploaded_ext; uploaded_bytes = await e.file.read(); uploaded_ext = Path(e.file.name).suffix; ui.notify("Staged")
    def add(name):
        nonlocal uploaded_bytes
        if name and uploaded_bytes:
            fname = f"{re.sub(r'[^a-z0-9]','_',name.lower())}{uploaded_ext}"
            (ASSETS_DIR / 'bgs' / fname).write_bytes(uploaded_bytes)
            CRUD_MANAGER.create_location(name, f"assets/bgs/{fname}")
            uploaded_bytes=None; refresh()
    def delete(row): CRUD_MANAGER.delete_location(row['location_id']); refresh()
    
    def edit(row):
        nonlocal uploaded_bytes
        uploaded_bytes = None # Reset
        with ui.dialog() as dialog, ui.card():
            ui.label(f"Edit {row['name']}").classes("text-lg font-bold")
            n = ui.input("Name", value=row['name'])
            ui.label("Upload new BG to replace (optional)").classes("text-sm text-gray-500")
            ui.upload(auto_upload=True, on_upload=handle_upload).props('accept="image/*" style="max-width: 200px"')
            def save():
                path = row['bg_path']
                if uploaded_bytes:
                    fname = f"{re.sub(r'[^a-z0-9]','_',n.value.lower())}_upd{uploaded_ext}"
                    (ASSETS_DIR / 'bgs' / fname).write_bytes(uploaded_bytes)
                    path = f"assets/bgs/{fname}"
                CRUD_MANAGER.update_location(row['location_id'], n.value, path)
                dialog.close(); refresh(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.row().classes("w-full gap-8"):
        with ui.card().classes("w-1/3"):
            ui.label("Add Location").classes("text-xl font-bold")
            n = ui.input("Name")
            ui.upload(label="BG Image", auto_upload=True, on_upload=handle_upload).props('accept="image/*"')
            ui.button("Save", on_click=lambda: add(n.value)).classes("mt-4")
        with ui.card().classes("w-2/3"):
            table = ui.table(columns=[{'name':'name','label':'Name','field':'name'}, {'name':'bg_path','label':'Path','field':'bg_path'}, {'name':'actions','label':'','field':'actions'}], rows=[], row_key='location_id').classes('w-full')
            table.add_slot('body-cell-actions', r'''
                <q-td :props="props">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)" />
                </q-td>''')
            table.on('del', lambda e: delete(e.args))
            table.on('edit', lambda e: edit(e.args))
    refresh()

def sprites_content():
    uploaded_bytes, uploaded_ext = None, None
    table, char_select, expr_input = None, None, None

    def refresh(): 
        table.rows = CRUD_MANAGER.get_all_sprites_joined()
        char_select.set_options({c['char_id']: c['char_name'] for c in CRUD_MANAGER.get_all_characters()})

    async def handle_upload(e): nonlocal uploaded_bytes, uploaded_ext; uploaded_bytes = await e.file.read(); uploaded_ext = Path(e.file.name).suffix; ui.notify("Staged")
    def add():
        nonlocal uploaded_bytes
        if char_select.value and expr_input.value and uploaded_bytes:
            fname = f"{char_select.options[char_select.value]}_{expr_input.value}{uploaded_ext}".lower().replace(' ','_')
            (ASSETS_DIR / 'sprites' / fname).write_bytes(uploaded_bytes)
            CRUD_MANAGER.create_sprite(char_select.value, expr_input.value, f"assets/sprites/{fname}")
            uploaded_bytes=None; refresh()
    def delete(row): CRUD_MANAGER.delete_sprite(row['sprite_id']); refresh()

    def edit(row):
        nonlocal uploaded_bytes; uploaded_bytes = None
        chars = CRUD_MANAGER.get_all_characters()
        c_opts = {c['char_id']: c['char_name'] for c in chars}
        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Sprite").classes("text-lg font-bold")
            c_sel = ui.select(c_opts, label="Character", value=row['char_id'])
            e_inp = ui.input("Expression", value=row['expression'])
            ui.label("Upload new image (optional)")
            ui.upload(auto_upload=True, on_upload=handle_upload).props('accept="image/*" style="max-width:200px"')
            def save():
                path = row['path']
                if uploaded_bytes:
                    fname = f"upd_{c_sel.options[c_sel.value]}_{e_inp.value}{uploaded_ext}".lower().replace(' ','_')
                    (ASSETS_DIR / 'sprites' / fname).write_bytes(uploaded_bytes)
                    path = f"assets/sprites/{fname}"
                CRUD_MANAGER.update_sprite(row['sprite_id'], c_sel.value, e_inp.value, path)
                dialog.close(); refresh(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.row().classes("w-full gap-8"):
        with ui.card().classes("w-1/3"):
            ui.label("Add Sprite").classes("text-xl font-bold")
            char_select = ui.select({}, label="Character").classes("w-full")
            expr_input = ui.input("Expression").classes("w-full")
            ui.upload(label="Image", auto_upload=True, on_upload=handle_upload).props('accept="image/*"').classes("mt-2")
            ui.button("Save", on_click=add).classes("mt-4 w-full")
        with ui.card().classes("w-2/3"):
            table = ui.table(columns=[{'name':'char_name','label':'Char','field':'char_name'}, {'name':'expression','label':'Expr','field':'expression'}, {'name':'actions','label':'','field':'actions'}], rows=[], row_key='sprite_id').classes('w-full')
            table.add_slot('body-cell-actions', r'''
                <q-td :props="props">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)" />
                </q-td>''')
            table.on('del', lambda e: delete(e.args))
            table.on('edit', lambda e: edit(e.args))
    refresh()

def events_content():
    events_table = None
    logic_table = None
    start_scene_select = None
    end_scene_select = None
    logic_event_select = None

    def refresh_events(): events_table.rows = CRUD_MANAGER.get_all_events()
    def add_event(name):
        if name: CRUD_MANAGER.create_event(name); refresh_events(); refresh_logic()
    def delete_event(row): CRUD_MANAGER.delete_event(row['event_id']); refresh_events(); refresh_logic()
    
    def edit_event(row):
        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Event").classes("text-lg font-bold")
            n = ui.input("Name", value=row['name'])
            def save():
                CRUD_MANAGER.update_event_name(row['event_id'], n.value)
                dialog.close(); refresh_events(); refresh_logic(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    def refresh_logic():
        scenes = CRUD_MANAGER.get_all_scenes_joined()
        scene_opts = {s['scene_id']: s['scene_name'] for s in scenes}
        start_scene_select.set_options(scene_opts)
        end_scene_select.set_options(scene_opts)
        events = CRUD_MANAGER.get_all_events()
        event_opts = {e['event_id']: e['name'] for e in events}
        logic_event_select.set_options(event_opts)
        if start_scene_select.value:
            logic_table.rows = CRUD_MANAGER.get_event_logic_for_scene(start_scene_select.value)
        else: logic_table.rows = []

    def on_start_scene_change(e):
        if e.value: logic_table.rows = CRUD_MANAGER.get_event_logic_for_scene(e.value)
        else: logic_table.rows = []

    def add_logic_rule():
        if not start_scene_select.value or not end_scene_select.value or not logic_event_select.value: return ui.notify("Missing info", color='red')
        CRUD_MANAGER.create_event_logic(int(start_scene_select.value), int(end_scene_select.value), int(logic_event_select.value))
        refresh_logic()

    def delete_logic_rule(row): CRUD_MANAGER.delete_event_logic(row['logic_id']); refresh_logic()
    
    def edit_logic_rule(row):
        scenes = CRUD_MANAGER.get_all_scenes_joined()
        s_opts = {s['scene_id']: s['scene_name'] for s in scenes}
        events = CRUD_MANAGER.get_all_events()
        e_opts = {e['event_id']: e['name'] for e in events}
        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Logic Rule").classes("text-lg font-bold")
            ss = ui.select(s_opts, label="Start", value=row['start_scene'])
            es = ui.select(s_opts, label="End", value=row['end_scene'])
            ev = ui.select(e_opts, label="Event", value=row['event_id'])
            def save():
                CRUD_MANAGER.update_event_logic(row['logic_id'], ss.value, es.value, ev.value)
                dialog.close(); refresh_logic(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.column().classes("w-full gap-8"):
        with ui.row().classes("w-full gap-8"):
            with ui.card().classes("w-1/3"):
                ui.label("Add Event Flag").classes("text-xl font-bold")
                n = ui.input("Name").classes("w-full")
                ui.button("Add", on_click=lambda: add_event(n.value)).classes("mt-4 w-full")
            with ui.card().classes("w-2/3"):
                events_table = ui.table(
                    columns=[{'name':'name','label':'Name','field':'name'}, {'name':'obtained_bool','label':'Active?','field':'obtained_bool'}, {'name':'actions','label':'','field':'actions'}],
                    rows=[], row_key='event_id').classes('w-full')
                events_table.add_slot('body-cell-actions', r'''
                    <q-td :props="props">
                        <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)" />
                        <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)" />
                    </q-td>''')
                events_table.on('del', lambda e: delete_event(e.args))
                events_table.on('edit', lambda e: edit_event(e.args))

        with ui.row().classes("w-full gap-8"):
            with ui.card().classes("w-1/3"):
                ui.label("Event Logic (Many-to-Many)").classes("text-xl font-bold mb-2")
                start_scene_select = ui.select({}, label="Start Scene", on_change=on_start_scene_change).classes("w-full mb-2")
                end_scene_select = ui.select({}, label="End Scene (if events true)").classes("w-full mb-2")
                logic_event_select = ui.select({}, label="Required Event").classes("w-full mb-4")
                ui.button("Add Logic Rule", on_click=add_logic_rule).classes("w-full bg-indigo-600 text-white")
            with ui.card().classes("w-2/3"):
                logic_table = ui.table(
                    columns=[
                        {'name': 'logic_id',    'label': 'ID',        'field': 'logic_id'},
                        {'name': 'start_scene', 'label': 'Start ID',  'field': 'start_scene'},
                        {'name': 'end_scene',   'label': 'End ID',    'field': 'end_scene'},
                        {'name': 'event_id',    'label': 'Event ID',  'field': 'event_id'},
                        {'name': 'event_name',  'label': 'Event',     'field': 'event_name'},
                        {'name': 'obtained_bool','label':'Obtained?','field':'obtained_bool'},
                        {'name': 'actions',     'label': '',         'field': 'actions'},
                    ],
                    rows=[],
                    row_key='logic_id',
                ).classes("w-full")
                logic_table.add_slot('body-cell-actions', r'''
                    <q-td :props="props">
                        <q-btn icon="edit" color="primary" flat dense size="sm" @click="$parent.$emit('edit', props.row)" />
                        <q-btn icon="delete" color="negative" flat dense size="sm" @click="$parent.$emit('del', props.row)" />
                    </q-td>''')
                logic_table.on('del', lambda e: delete_logic_rule(e.args))
                logic_table.on('edit', lambda e: edit_logic_rule(e.args))

    refresh_events(); refresh_logic()

def choices_content():
    table = None
    group_input, text_input, scene_select, event_select = None, None, None, None

    def refresh():
        table.rows = CRUD_MANAGER.get_all_choices_grouped()
        scenes = CRUD_MANAGER.get_all_scenes_joined()
        scene_select.set_options({s['scene_id']: s['scene_name'] for s in scenes})
        events = CRUD_MANAGER.get_all_events()
        evt_opts = {0: 'No Event'}
        evt_opts.update({e['event_id']: e['name'] for e in events})
        event_select.set_options(evt_opts)
        if not event_select.value: event_select.value = 0

    def generate_id(): group_input.value = CRUD_MANAGER.get_next_choice_group_id()
    def add():
        if not group_input.value or not text_input.value or not scene_select.value: return ui.notify("Missing data", color='red')
        evt = event_select.value if event_select.value != 0 else None
        CRUD_MANAGER.create_choice_option(int(group_input.value), text_input.value, scene_select.value, evt)
        refresh()
    def delete(row): CRUD_MANAGER.delete_choice_option(row['decision_id']); refresh()

    def edit(row):
        scenes = CRUD_MANAGER.get_all_scenes_joined()
        s_opts = {s['scene_id']: s['scene_name'] for s in scenes}
        events = CRUD_MANAGER.get_all_events()
        e_opts = {0: 'No Event'}; e_opts.update({e['event_id']: e['name'] for e in events})
        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Option").classes("text-lg font-bold")
            t = ui.input("Text", value=row['decision_text'])
            ns = ui.select(s_opts, label="Next Scene", value=row['next_scene'])
            ev = ui.select(e_opts, label="Event", value=row['event_id'] or 0)
            def save():
                new_evt = ev.value if ev.value != 0 else None
                CRUD_MANAGER.update_choice_option(row['decision_id'], t.value, ns.value, new_evt)
                dialog.close(); refresh(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.row().classes("w-full gap-8"):
        with ui.card().classes("w-1/3"):
            ui.label("Choice Builder").classes("text-xl font-bold")
            with ui.row().classes("items-end w-full"):
                group_input = ui.number(label="Group ID", value=1).classes("flex-grow")
                ui.button("New ID", on_click=generate_id).classes("mb-2 ml-2")
            text_input = ui.input("Text").classes("w-full")
            scene_select = ui.select({}, label="Next Scene").classes("w-full")
            event_select = ui.select({}, label="Trigger Event").classes("w-full")
            ui.button("Add Option", on_click=add).classes("mt-4 w-full bg-indigo-600 text-white")
        with ui.card().classes("w-2/3"):
            table = ui.table(columns=[{'name':'choice_id','label':'Group','field':'choice_id'},{'name':'decision_text','label':'Text','field':'decision_text'},{'name':'next_scene_name','label':'Leads To','field':'next_scene_name'},{'name':'actions','label':'','field':'actions'}], rows=[], row_key='decision_id').classes('w-full')
            table.add_slot('body-cell-actions', r'''
                <q-td :props="props">
                    <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)" />
                    <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)" />
                </q-td>''')
            table.on('del', lambda e: delete(e.args))
            table.on('edit', lambda e: edit(e.args))
    refresh()

def editor_content():
    scene_select, lines_table = None, None
    speaker_select, sprite_select, dialogue_input, choice_group_input = None, None, None, None

    def refresh_data():
        scenes = CRUD_MANAGER.get_all_scenes_joined()
        scene_select.set_options({s['scene_id']: s['scene_name'] for s in scenes})
        chars = CRUD_MANAGER.get_all_characters()
        speaker_select.set_options({c['char_id']: c['char_name'] for c in chars})
    
    def load_lines():
        if not scene_select.value: return
        lines_table.rows = CRUD_MANAGER.get_lines_for_scene(scene_select.value)
    
    def on_speaker_change(e):
        if not e.value: sprite_select.set_options({}); return
        sprites = CRUD_MANAGER.get_sprites_by_char(e.value)
        opts = {0: 'No Sprite'}; opts.update({s['sprite_id']: s['expression'] for s in sprites})
        sprite_select.set_options(opts); sprite_select.value = 0

    def add_line():
        if not scene_select.value or not speaker_select.value or not dialogue_input.value: return ui.notify("Missing Fields", color='red')
        sprite = sprite_select.value if sprite_select.value != 0 else None
        choice = int(choice_group_input.value) if choice_group_input.value else None
        CRUD_MANAGER.create_line(scene_select.value, speaker_select.value, dialogue_input.value, sprite, choice)
        dialogue_input.value = ""; load_lines()

    def delete_line(row): CRUD_MANAGER.delete_line(row['line_id']); load_lines()

    def edit_line(row):
        chars = CRUD_MANAGER.get_all_characters()
        c_opts = {c['char_id']: c['char_name'] for c in chars}
        
        # Get sprites for current speaker
        sprites = CRUD_MANAGER.get_sprites_by_char(row['speaker_id'])
        s_opts = {0: 'No Sprite'}
        s_opts.update({s['sprite_id']: s['expression'] for s in sprites})

        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Line").classes("text-lg font-bold")
            # Note: Changing speaker resets sprite selection logic usually, simplistic here
            s_sel = ui.select(c_opts, label="Speaker", value=row['speaker_id'])
            
            # Simple reactive sprite update inside dialog
            sp_sel = ui.select(s_opts, label="Sprite", value=row['sprite_id'] or 0)
            
            def update_sprites_diag(e):
                new_sprites = CRUD_MANAGER.get_sprites_by_char(e.value)
                new_opts = {0: 'No Sprite'}
                new_opts.update({s['sprite_id']: s['expression'] for s in new_sprites})
                sp_sel.set_options(new_opts)
                sp_sel.value = 0
            s_sel.on_value_change(update_sprites_diag)

            txt = ui.textarea("Text", value=row['content'])
            
            def save():
                sp = sp_sel.value if sp_sel.value != 0 else None
                CRUD_MANAGER.update_line(row['line_id'], s_sel.value, txt.value, sp)
                dialog.close(); load_lines(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.column().classes("w-full"):
        scene_select = ui.select({}, label="Select Scene", on_change=load_lines).classes("w-1/2 mb-4")
        with ui.row().classes("w-full gap-8"):
            with ui.card().classes("w-1/3"):
                ui.label("Add Line").classes("text-xl font-bold")
                speaker_select = ui.select({}, label="Speaker", on_change=on_speaker_change).classes("w-full")
                sprite_select = ui.select({}, label="Sprite").classes("w-full")
                dialogue_input = ui.textarea(label="Dialogue").classes("w-full")
                choice_group_input = ui.number(label="Triggers Choice ID").classes("w-full")
                ui.button("Add", on_click=add_line).classes("w-full mt-4")
            with ui.card().classes("w-2/3"):
                lines_table = ui.table(columns=[{'name':'sequence','label':'#','field':'sequence'}, {'name':'char_name','label':'Speaker','field':'char_name'}, {'name':'content','label':'Text','field':'content','style':'white-space:normal'}, {'name':'choice_id','label':'Choice','field':'choice_id'}, {'name':'act','label':'','field':'act'}], rows=[], row_key='line_id').classes('w-full')
                lines_table.add_slot('body-cell-act', r'''<q-td :props="props">
                    <q-btn icon="edit" color="primary" flat dense size="sm" @click="$parent.$emit('edit', props.row)"/>
                    <q-btn icon="delete" color="negative" flat dense size="sm" @click="$parent.$emit('del', props.row)"/>
                </q-td>''')
                lines_table.on('del', lambda e: delete_line(e.args))
                lines_table.on('edit', lambda e: edit_line(e.args))
    refresh_data()

def scenes_page_content():
    table, name_input, loc_select = None, None, None
    def refresh():
        table.rows = CRUD_MANAGER.get_all_scenes_joined()
        locs = CRUD_MANAGER.get_all_locations()
        loc_select.set_options({l['location_id']: l['name'] for l in locs})
    def add():
        if name_input.value and loc_select.value: CRUD_MANAGER.create_scene(name_input.value, loc_select.value); refresh()
    def delete(row): CRUD_MANAGER.delete_scene(row['scene_id']); refresh()
    
    def edit(row):
        locs = CRUD_MANAGER.get_all_locations()
        l_opts = {l['location_id']: l['name'] for l in locs}
        with ui.dialog() as dialog, ui.card():
            ui.label("Edit Scene").classes("text-lg font-bold")
            t = ui.input("Title", value=row['scene_name'])
            l = ui.select(l_opts, label="Location", value=row['location_id'])
            def save():
                CRUD_MANAGER.update_scene(row['scene_id'], t.value, l.value)
                dialog.close(); refresh(); ui.notify("Updated")
            ui.button("Save", on_click=save)
        dialog.open()

    with ui.row().classes("w-full gap-8"):
        with ui.card().classes("w-1/3"):
            ui.label("Create Scene").classes("text-xl font-bold")
            name_input = ui.input("Title")
            loc_select = ui.select({}, label="Default BG").classes("w-full")
            ui.button("Create", on_click=add).classes("mt-4 w-full")
        with ui.card().classes("w-2/3"):
            table = ui.table(columns=[{'name':'scene_id','label':'ID','field':'scene_id'}, {'name':'scene_name','label':'Title','field':'scene_name'}, {'name':'location_name','label':'Loc','field':'location_name'}, {'name':'act','label':'','field':'act'}], rows=[], row_key='scene_id').classes('w-full')
            table.add_slot('body-cell-act', r'''<q-td :props="props">
                <q-btn icon="edit" color="primary" flat dense @click="$parent.$emit('edit', props.row)"/>
                <q-btn icon="delete" color="negative" flat dense @click="$parent.$emit('del', props.row)"/>
            </q-td>''')
            table.on('del', lambda e: delete(e.args))
            table.on('edit', lambda e: edit(e.args))
    refresh()

# --- 4. GAME PLAYER LOGIC (FIXED LAYERING & NESTING) ---

def player_content():
    class GameState:
        def __init__(self):
            self.scene_id = 1 
            self.lines = []
            self.line_idx = -1
            self.bg_path = ""

    state = GameState()
    
    # --- LAYER 1: BACKGROUND (Bottom) ---
    bg_image = ui.image().classes("absolute top-0 left-0 w-full h-full object-cover").style("z-index: 0;")
    
    # --- LAYER 2: SPRITE (Middle) ---
    sprite_container = ui.element('div').classes("absolute bottom-0 left-1/2 transform -translate-x-1/2 h-4/5 w-1/2 flex justify-center items-end pointer-events-none").style("z-index: 10;")
    with sprite_container:
        sprite_image = ui.image().classes("h-full object-contain").style("display: none;")
    
    # --- LAYER 3: UI / TEXT (Top) ---
    dialogue_card = ui.card().classes("absolute bottom-8 left-1/2 transform -translate-x-1/2 w-3/4 bg-gray-900/90 text-white p-6 border-2 border-gray-600 rounded-xl").style("z-index: 20;")
    
    with dialogue_card:
        name_label = ui.label("").classes("text-xl font-bold text-yellow-400 mb-2")
        text_label = ui.label("").classes("text-lg leading-relaxed")
    
    next_btn = ui.button("Next >", on_click=lambda: advance()).classes("absolute bottom-8 right-16").style("z-index: 30;")
    choice_container = ui.column().classes("absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 gap-4").style("z-index: 40;")

    def load_scene(scene_id):
        details = CRUD_MANAGER.get_scene_details(scene_id)
        if not details: return ui.notify("Scene not found / End of Game", color='red')
        state.scene_id = scene_id
        db_path = details['bg_path']
        if db_path:
            clean_path = db_path.replace('\\', '/')
            if not clean_path.startswith('/'): clean_path = '/' + clean_path
            print(f"LOADING BG: {clean_path}") 
            state.bg_path = clean_path
            bg_image.source = state.bg_path
        else: bg_image.source = None
        state.lines = CRUD_MANAGER.get_lines_for_scene(scene_id)
        state.line_idx = -1
        advance()

    def handle_choice(choice):
        if choice['event_id']:
            CRUD_MANAGER.update_event_status(choice['event_id'], True)
            ui.notify(f"Event Triggered: {choice['event_name']}")
        if choice['next_scene']:
            choice_container.clear(); dialogue_card.visible = True; load_scene(choice['next_scene'])

    def show_choices(group_id):
        next_btn.visible = False
        choices = CRUD_MANAGER.get_choices_by_group(group_id)
        choice_container.clear()
        for c in choices:
            def make_handler(clicked_choice): return lambda: handle_choice(clicked_choice)
            ui.button(c['decision_text'], on_click=make_handler(c)).classes("w-64 h-12 text-lg bg-indigo-600 hover:bg-indigo-500 border border-white shadow-xl")

    def advance():
        state.line_idx += 1
        if state.line_idx >= len(state.lines):
            next_scene = CRUD_MANAGER.get_next_scene_with_event_logic(state.scene_id)
            if next_scene:
                ui.notify(f"Jumping to scene {next_scene}", color='green')
                choice_container.clear(); load_scene(next_scene)
            else: ui.notify("Scene Finished (no next scene).", color='orange')
            return

        line = state.lines[state.line_idx]
        name_label.text = line['char_name']; name_label.style(f"color: #{line['text_color']}")
        text_label.text = line['content']; dialogue_card.visible = True

        if line['sprite_path']:
            s_path = line['sprite_path']; clean_path = s_path.replace('\\', '/')
            if not clean_path.startswith('/'): clean_path = '/' + clean_path
            print(f"LOADING SPRITE: {clean_path}") 
            sprite_image.source = clean_path; sprite_image.style("display: block")
        else: sprite_image.style("display: none")

        if line['choice_id']: next_btn.visible = False; show_choices(line['choice_id'])
        else: next_btn.visible = True

    load_scene(1)

# --- 5. NAVIGATION & APP SHELL ---

async def nav_menu():
    ui.label('VN Engine Admin').classes('text-xl font-bold p-4 text-indigo-800')
    ui.separator()
    def link(name, target): ui.link(name, target).classes('block p-3 hover:bg-indigo-50 text-gray-800 font-medium')
    link('1. Locations', locations_page)
    link('2. Characters', characters_page)
    link('3. Sprites', sprites_page)
    link('4. Events', events_page)
    link('5. Choices', choices_page)
    link('6. Scenes', scenes_page)
    link('7. Script Editor', editor_page)
    ui.separator().classes('my-2')
    link('▶ PLAY GAME', player_page)

async def admin_layout(content_func):
    with ui.header().classes('bg-indigo-700 text-white'):
        ui.label('VN Engine').classes('text-2xl font-bold')
        ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat round dense')
    with ui.left_drawer(value=True) as drawer: await nav_menu()
    with ui.column().classes('w-full min-h-screen bg-gray-50 p-8 max-w-7xl mx-auto'): content_func()

@ui.page('/locations')
async def locations_page(): await admin_layout(locations_content)
@ui.page('/characters')
async def characters_page(): await admin_layout(characters_content)
@ui.page('/sprites')
async def sprites_page(): await admin_layout(sprites_content)
@ui.page('/events')
async def events_page(): await admin_layout(events_content)
@ui.page('/choices')
async def choices_page(): await admin_layout(choices_content)
@ui.page('/scenes')
async def scenes_page(): await admin_layout(scenes_page_content)
@ui.page('/editor')
async def editor_page(): await admin_layout(editor_content)

@ui.page('/play')
async def player_page():
    with ui.column().classes('w-full h-screen relative overflow-hidden'):
        ui.button(icon='close', on_click=lambda: ui.run_javascript('window.location.href="/editor"')).classes('absolute top-4 right-4 z-50 bg-red-600 text-white rounded-full')
        player_content()

# --- 6. INITIALIZATION & ENTRY POINT ---

def init_db():
    conn = create_connection()
    if conn:
        table_sqls = [
            "CREATE TABLE IF NOT EXISTS Locations (location_id INTEGER PRIMARY KEY, name TEXT NOT NULL, bg_path TEXT NOT NULL);",
            "CREATE TABLE IF NOT EXISTS Characters (char_id INTEGER PRIMARY KEY, char_name TEXT NOT NULL, text_color TEXT NOT NULL DEFAULT 'FFFFFF');",
            "CREATE TABLE IF NOT EXISTS Events (event_id INTEGER PRIMARY KEY, name TEXT NOT NULL, obtained_bool BOOLEAN NOT NULL DEFAULT 0);",
            "CREATE TABLE IF NOT EXISTS Scenes (scene_id INTEGER PRIMARY KEY, name TEXT NOT NULL, location_id INTEGER, next_scene_default INTEGER, FOREIGN KEY (location_id) REFERENCES Locations (location_id) ON DELETE SET NULL, FOREIGN KEY (next_scene_default) REFERENCES Scenes (scene_id) ON DELETE SET NULL);",
            "CREATE TABLE IF NOT EXISTS Sprites (sprite_id INTEGER PRIMARY KEY, char_id INTEGER NOT NULL, expression_id INTEGER NOT NULL, expression TEXT NOT NULL, path TEXT NOT NULL, FOREIGN KEY (char_id) REFERENCES Characters (char_id) ON DELETE CASCADE);",
            "CREATE TABLE IF NOT EXISTS Choices (decision_id INTEGER PRIMARY KEY, choice_id INTEGER NOT NULL, decision_text TEXT NOT NULL, next_scene INTEGER, event_id INTEGER, FOREIGN KEY (next_scene) REFERENCES Scenes (scene_id) ON DELETE SET NULL, FOREIGN KEY (event_id) REFERENCES Events (event_id) ON DELETE SET NULL);",
            "CREATE TABLE IF NOT EXISTS Lines (line_id INTEGER PRIMARY KEY, scene_id INTEGER NOT NULL, speaker_id INTEGER NOT NULL, sequence INTEGER NOT NULL, content TEXT NOT NULL, sprite_id INTEGER, expression_id INTEGER, choice_id INTEGER, FOREIGN KEY (scene_id) REFERENCES Scenes (scene_id) ON DELETE CASCADE, FOREIGN KEY (speaker_id) REFERENCES Characters (char_id) ON DELETE CASCADE, FOREIGN KEY (sprite_id) REFERENCES Sprites (sprite_id) ON DELETE SET NULL);",
            """CREATE TABLE IF NOT EXISTS EventLogic (
                logic_id     INTEGER PRIMARY KEY,
                start_scene  INTEGER NOT NULL,
                end_scene    INTEGER NOT NULL,
                event_id     INTEGER NOT NULL,
                FOREIGN KEY (start_scene) REFERENCES Scenes(scene_id) ON DELETE CASCADE,
                FOREIGN KEY (end_scene)   REFERENCES Scenes(scene_id) ON DELETE CASCADE,
                FOREIGN KEY (event_id)    REFERENCES Events(event_id) ON DELETE CASCADE
            );"""
        ]
        try:
            cursor = conn.cursor()
            for sql in table_sqls: cursor.execute(sql)
            conn.commit()
            print("DB Initialized.")
        except Error as e: print(f"Init Error: {e}")
        finally: conn.close()

@ui.page('/')
async def home(): return RedirectResponse('/locations')

if __name__ in {"__main__", "__mp_main__"}:
    init_db()
    ui.run(title="VN Engine", port=8080, reload=False)