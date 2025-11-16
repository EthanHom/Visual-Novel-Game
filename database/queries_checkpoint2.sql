-- Example SELECT queries (you can include comments that map to use-cases)

-- 1. List all characters
SELECT char_id, char_name, text_color
FROM Characters;

-- 2. List all locations with background paths
SELECT location_id, name, bg_path
FROM Locations;

-- 3. List all scenes with their locations
SELECT S.scene_id, S.name AS scene_name, L.name AS location_name
FROM Scenes S
JOIN Locations L ON S.location_id = L.location_id;

-- 4. Get all lines for a scene ordered by sequence
SELECT line_id, content, speaker_id, expression_id, sequence
FROM Lines
WHERE scene_id = 1
ORDER BY sequence;

-- 5. Get all sprites for a given character
SELECT sprite_id, path, expression_id, expression
FROM Sprites
WHERE char_id = 1;

-- 6. Show choices and next scenes for a given choice_id
SELECT decision_id, choice_text, next_scene
FROM Choices
WHERE choice_id = 1;

-- 7. Get events that have been obtained
SELECT event_id, name
FROM Events
WHERE obtained_bool = 1;

-- 8. Show lines with character names and sprite info (join)
SELECT L.sequence, C.char_name, L.content, S.path AS sprite_path, S.expression
FROM Lines L
JOIN Characters C ON L.speaker_id = C.char_id
LEFT JOIN Sprites S
  ON L.speaker_id = S.char_id AND L.expression_id = S.expression_id
WHERE L.scene_id = 1
ORDER BY L.sequence;

-- 9. Get scenes that lead to a specific next scene
SELECT scene_id, name
FROM Scenes
WHERE next_scene_default = 3;

-- 10. Count number of lines per scene
SELECT scene_id, COUNT(*) AS num_lines
FROM Lines
GROUP BY scene_id;

-- Example INSERT / UPDATE / DELETE statements

-- 11. Insert a new character
INSERT INTO Characters (char_name, text_color)
VALUES ('New Hero', '00FFAA');

-- 12. Insert a new location
INSERT INTO Locations (name, bg_path)
VALUES ('Rooftop', 'assets/backgrounds/rooftop.png');

-- 13. Insert a new scene
INSERT INTO Scenes (location_id, name, next_scene_default)
VALUES (1, 'Flashback Scene', 2);

-- 14. Insert a new event
INSERT INTO Events (obtained_bool, name)
VALUES (0, 'secret_file_found');

-- 15. Insert a new line into a scene
INSERT INTO Lines (content, scene_id, speaker_id, expression_id, sequence, choice_id)
VALUES ('We should not be here...', 1, 1, 1, 5, NULL);

-- 16. Update a character's text color
UPDATE Characters
SET text_color = 'FFAA00'
WHERE char_name = 'New Hero';

-- 17. Update a scene's default next scene
UPDATE Scenes
SET next_scene_default = 3
WHERE scene_id = 1;

-- 18. Mark an event as obtained
UPDATE Events
SET obtained_bool = 1
WHERE name = 'secret_file_found';

-- 19. Delete a test line
DELETE FROM Lines
WHERE content = 'We should not be here...';

-- 20. Delete a temporary character
DELETE FROM Characters
WHERE char_name = 'New Hero';
