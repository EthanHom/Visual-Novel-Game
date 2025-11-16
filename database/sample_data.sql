-- Insert sample characters
INSERT INTO Characters (char_id, char_name, text_color) VALUES 
(1, 'Apollo', 'FF0000'),
(2, 'Maya', '0000FF'),
(3, 'Narrator', '000000');

-- Insert sample locations
INSERT INTO Locations (location_id, bg_path, name) VALUES 
(1, 'assets/backgrounds/courtroom.png', 'Courtroom'),
(2, 'assets/backgrounds/office.png', 'Law Office'),
(3, 'assets/backgrounds/library.png', 'Library');

-- Insert sample events
INSERT INTO Events (event_id, obtained_bool, name) VALUES 
(1, 0, 'evidence_found'),
(2, 0, 'first_trial_complete');

-- Insert sample scenes
INSERT INTO Scenes (scene_id, location_id, name, next_scene_default) VALUES 
(1, 1, 'Opening Scene', 2),
(2, 2, 'Investigation Start', 3),
(3, 1, 'Trial Begins', NULL);

-- Insert sample sprites
INSERT INTO Sprites (sprite_id, char_id, path, expression_id, expression) VALUES 
(1, 1, 'assets/sprites/apollo_neutral.png', 1, 'NEUTRAL'),
(2, 1, 'assets/sprites/apollo_happy.png', 2, 'HAPPY'),
(3, 1, 'assets/sprites/apollo_stressed.png', 3, 'STRESSED'),
(4, 2, 'assets/sprites/maya_neutral.png', 1, 'NEUTRAL'),
(5, 2, 'assets/sprites/maya_happy.png', 2, 'HAPPY');

-- Insert sample choices
INSERT INTO Choices (decision_id, choice_id, next_scene, event_id, choice_text) VALUES 
(1, 1, 2, NULL, 'Investigate the office'),
(2, 1, 3, 1, 'Go straight to trial');

-- Insert sample lines
INSERT INTO Lines (line_id, content, scene_id, speaker_id, expression_id, sequence, choice_id) VALUES 
(1, 'Court is now in session for the trial!', 1, 3, 1, 1, NULL),
(2, 'Uh, the defense is, uh, fine! I mean ready, Your Honor!', 1, 1, 3, 2, NULL),
(3, 'What should we do next?', 1, 1, 1, 3, 1),
(4, 'Welcome to the office. Time to investigate!', 2, 2, 2, 1, NULL),
(5, 'Let us begin the trial proceedings.', 3, 3, 1, 1, NULL);
