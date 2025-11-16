-- Drop existing tables if they exist
DROP TABLE IF EXISTS Lines;
DROP TABLE IF EXISTS Choices;
DROP TABLE IF EXISTS Sprites;
DROP TABLE IF EXISTS Scenes;
DROP TABLE IF EXISTS Characters;
DROP TABLE IF EXISTS Locations;
DROP TABLE IF EXISTS Events;

-- Characters table
CREATE TABLE Characters (
    char_id INTEGER PRIMARY KEY,
    char_name CHAR(50) NOT NULL,
    text_color CHAR(6) NOT NULL
);

-- Locations table
CREATE TABLE Locations (
    location_id INTEGER PRIMARY KEY,
    bg_path CHAR(100) NOT NULL,
    name CHAR(100) NOT NULL
);

-- Scenes table
CREATE TABLE Scenes (
    scene_id INTEGER PRIMARY KEY,
    location_id INTEGER NOT NULL,
    name CHAR(100) NOT NULL,
    next_scene_default INTEGER,
    FOREIGN KEY (location_id) REFERENCES Locations(location_id)
);

-- Sprites table
CREATE TABLE Sprites (
    sprite_id INTEGER PRIMARY KEY,
    char_id INTEGER NOT NULL,
    path CHAR(100) NOT NULL,
    expression_id INTEGER NOT NULL,
    expression CHAR(30) NOT NULL,
    FOREIGN KEY (char_id) REFERENCES Characters(char_id)
);

-- Events table
CREATE TABLE Events (
    event_id INTEGER PRIMARY KEY,
    obtained_bool INTEGER NOT NULL,
    name CHAR(100) NOT NULL
);

-- Choices table
CREATE TABLE Choices (
    decision_id INTEGER PRIMARY KEY,
    choice_id INTEGER NOT NULL,
    next_scene INTEGER,
    event_id INTEGER,
    choice_text CHAR(200),
    FOREIGN KEY (event_id) REFERENCES Events(event_id)
);

-- Lines table
CREATE TABLE Lines (
    line_id INTEGER PRIMARY KEY,
    content CHAR(800) NOT NULL,
    scene_id INTEGER NOT NULL,
    speaker_id INTEGER NOT NULL,
    expression_id INTEGER NOT NULL,
    sequence INTEGER NOT NULL,
    choice_id INTEGER,
    FOREIGN KEY (scene_id) REFERENCES Scenes(scene_id),
    FOREIGN KEY (speaker_id) REFERENCES Characters(char_id),
    FOREIGN KEY (choice_id) REFERENCES Choices(choice_id)
);
