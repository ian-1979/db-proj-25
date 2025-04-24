-- you should import this into your XAMPP


-- Sample Campaigns
INSERT INTO campaign (name, description, campaign_image_path) VALUES
('Curse of the Underdark', 'A campaign of ancient ruins, lurking monsters, and lost magic.', NULL),
('Rise of the Storm Queen', 'An elemental upheaval threatens the world. Heroes must rise.', NULL);

-- Sample Notecards
INSERT INTO notecard (name, type, text, campaign_id, public, note_image_path) VALUES
('Alaric the Brave', 'character', 'A noble paladin from the northern provinces.', 1, 1, NULL),
('Cave of Echoes', 'location', 'A mysterious cavern rumored to be cursed.', 1, 1, NULL),
('Grimfang', 'monster', 'A fearsome orc chieftain wielding a cursed axe.', 1, 1, NULL),
('Elandra the Stormcaller', 'character', 'A tempest sorceress of unmatched fury.', 2, 1, NULL),
('Skyspire', 'location', 'A floating citadel among the storm clouds.', 2, 1, NULL),
('Thunderbeast', 'monster', 'A massive elemental beast with lightning breath.', 2, 1, NULL);

-- Sample Entities
INSERT INTO entity (note_id, entity_type, level, class, race, strength, dexterity, constitution, intelligence, wisdom, charisma) VALUES
(1, 'character', 5, 1, 'Human', 16, 12, 14, 10, 13, 15),
(3, 'monster', 3, NULL, 'Orc', 18, 10, 16, 8, 9, 6),
(4, 'character', 7, 2, 'Elf', 10, 14, 12, 18, 11, 17),
(6, 'monster', 6, NULL, 'Elemental', 20, 12, 18, 8, 10, 5);

-- Sample Features
INSERT INTO feature (note_id, modifier_text) VALUES
(1, 'Lay on Hands: Restore 25 HP per day.'),
(4, 'Storm Aura: Deal 1d6 lightning damage to nearby enemies each turn.'),
(6, 'Thunder Roar: Enemies within 30ft must pass CON save or be stunned.');

-- Feature Relationships
INSERT INTO entity_feature (entity_id, feature_id) VALUES
(1, 1),
(3, 2),
(4, 2),
(6, 3);

-- Sample Spells
INSERT INTO spells (note_id, level, school, spell_text, damage_type, damage, save) VALUES
(4, 3, 'Evocation', 'A bolt of lightning strikes from the sky, dealing 4d10 damage.', 2, 10, 1),
(6, 2, 'Conjuration', 'Summons a burst of thunder to knock back enemies.', 1, 6, 1);

-- Spell Relationships
INSERT INTO entity_spell (entity_id, spell_id) VALUES
(4, 1),
(6, 2);

-- Tags
INSERT INTO tag (name) VALUES ('underground'), ('boss'), ('paladin'), ('storm'), ('mage'), ('location'), ('elemental');

-- Entity-Tag Relationships
INSERT INTO entity_tag (entity_id, tag_id) VALUES
(1, 3), -- Alaric → paladin
(2, 1), -- Grimfang → underground
(2, 2), -- Grimfang → boss
(4, 4), -- Elandra → storm
(4, 5), -- Elandra → mage
(6, 2), -- Thunderbeast → boss
(6, 7); -- Thunderbeast → elemental

-- Users
INSERT INTO user (username, password, profile_image_path) VALUES
(101, 'hashedpass1', NULL),
(102, 'hashedpass2', NULL);

-- User-Campaign Relationships
INSERT INTO user_campaign (user_id, campaign_id) VALUES
(101, 1),
(102, 2);

-- User-Note Relationships (ownership or authorship)
INSERT INTO user_note (user_id, note_id) VALUES
(101, 1),
(101, 2),
(101, 3),
(102, 4),
(102, 5),
(102, 6);
