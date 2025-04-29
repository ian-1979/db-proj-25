-- Adds sample data that is up to data with the dbdatabase1.sql schema

-- Additional Notecards
INSERT INTO notecard (name, type, text, campaign_id, public, note_image_path) VALUES
('Sir Gareth the Bold', 'character', 'A knight famed for his dragon-slaying.', 1, 1, NULL),
('Whispering Woods', 'location', 'A dense, misty forest filled with strange magic.', 1, 1, NULL),
('Zara the Silent', 'npc', 'A rogue information broker working the shadows.', 1, 1, NULL),
('The Crimson Maw', 'monster', 'A feral vampire lord that haunts ancient ruins.', 1, 1, NULL),
('Temple of the Sun', 'location', 'An ancient abandoned temple devoted to the Sun God.', 2, 1, NULL),
('Storm Serpent', 'monster', 'A gigantic snake that channels storms through its scales.', 2, 1, NULL),
('High Priestess Lyra', 'npc', 'A leader of the Sun Temple cult, keeper of forbidden secrets.', 2, 1, NULL);

-- Additional Entities
INSERT INTO entity (note_id, entity_type, level, class, race, strength, dexterity, constitution, intelligence, wisdom, charisma) VALUES
(7, 'character', 6, 'Fighter', 'Human', 18, 11, 16, 10, 12, 13),
(8, 'location', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(9, 'npc', 5, 'Rogue', 'Halfling', 8, 18, 10, 14, 12, 16),
(10, 'monster', 8, NULL, 'Vampire', 20, 18, 16, 14, 16, 18),
(11, 'location', NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL),
(12, 'monster', 7, NULL, 'Dragon', 22, 16, 20, 12, 14, 10),
(13, 'npc', 9, 'Cleric', 'Elf', 8, 12, 14, 16, 18, 12);

-- Additional Features
INSERT INTO feature (note_id, modifier_text) VALUES
(7, 'Dragon Slayer: +5 bonus when fighting dragons.'),
(9, 'Sneak Attack: +3d6 bonus damage when attacking unaware enemies.'),
(10, 'Life Drain: Victims must save or lose max HP permanently.'),
(13, 'Blessing of Light: Allies within 30 feet gain +2 AC.');

-- More Entity-Feature Relationships
INSERT INTO entity_feature (entity_id, feature_id) VALUES
(7, 4),
(9, 5),
(10, 6),
(13, 7);

-- Additional Spells
INSERT INTO spells (note_id, level, school, spell_text, damage_type, damage, save) VALUES
(13, 3, 'Divination', 'Reveals hidden traps and invisible creatures.', 'Radiant', 0, 0),
(12, 4, 'Evocation', 'Unleashes a cone of storm energy dealing 8d6 lightning damage.', 'Lightning', 8, 1);

-- Spell Relationships
INSERT INTO entity_spell (entity_id, spell_id) VALUES
(13, 3),
(12, 4);

-- More Tags
INSERT INTO tag (name) VALUES
('vampire'), ('temple'), ('forest'), ('rogue'), ('storm');

-- More Notecard-Tag Relationships
INSERT INTO notecard_tag (note_id, tag_id) VALUES
(8, 3), -- Whispering Woods → forest
(9, 4), -- Zara → rogue
(10, 1), -- Crimson Maw → vampire
(11, 2), -- Temple of the Sun → temple
(12, 5); -- Storm Serpent → storm

-- Additional Users
INSERT INTO user (username, password, profile_image_path) VALUES
('player3', 'hashedpass3', NULL),
('player4', 'hashedpass4', NULL);

-- User-Campaign Relationships
INSERT INTO user_campaign (user_id, campaign_id, role) VALUES
(3, 1, 'player'),
(4, 2, 'player');

-- User-Note Relationships
INSERT INTO user_note (user_id, note_id, note_text) VALUES
(3, 7, 'Dragon-slaying knight.'),
(3, 8, 'Mysterious forest.'),
(3, 9, 'Stealthy informant.'),
(4, 10, 'Vampire boss.'),
(4, 11, 'Ancient sun temple.'),
(4, 12, 'Massive storm snake.');
