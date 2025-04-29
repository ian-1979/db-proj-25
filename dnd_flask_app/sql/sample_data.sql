START TRANSACTION;

-- Insert users
INSERT INTO `user` (`id`, `username`, `password`, `profile_image_path`) VALUES
(1, 'dungeonmaster', 'scrypt:32768:8:1$9AmdzufqStoWt4fy$9600dce27739c22e662d66bd4a44fa1f5ee0eb6c5cabaae0ec01832d7797982055e740ea735c8ee69c73f803686af3aa4c955f1cae83c623d7bb28ee533525ab', NULL), -- THE PASSWORD FOR dungeonmaster is: password123
(2, 'playerone', 'scrypt:32768:8:1$e3i4HqCBWybkjYCB$1d109220c2ca183b583dbb04d741201a5699cac5a68906fb0f12b0007898cf45c551da92f029dbe287874221583afb91effeb61f42330044a5f9516010fdbf2b', NULL), -- THE PASSWORD FOR playerone is: mypassword
(3, 'playertwo', 'scrypt:32768:8:1$yKkVfRQwND6Us8y4$9936db8406c0380fa8171fa4ad3682c5f8d9c6f0c355e461d0cf3314bed0a32567e59f22672708454dbaa9fb9e0883c9ff6cd373d71df7157246c7961f51a6a6', NULL); -- THE PASSWORD FOR playertwo is: securepass

-- Insert campaigns
INSERT INTO `campaign` (`id`, `name`, `description`, `campaign_image_path`) VALUES
(1, 'The Lost Kingdom', 'An epic quest to reclaim a fallen realm.', NULL),
(2, 'Mysteries of the Deep', 'A campaign set in a mysterious underwater world.', NULL);

-- Link users to campaigns
INSERT INTO `user_campaign` (`user_id`, `campaign_id`, `role`) VALUES
(1, 1, 'dm'),
(2, 1, 'player'),
(3, 1, 'player'),
(1, 2, 'dm');

-- Insert notecards
INSERT INTO `notecard` (`id`, `name`, `type`, `text`, `campaign_id`, `public`, `note_image_path`) VALUES
(1, 'Sir Galen', 'character', 'A brave knight from the northern lands.', 1, 1, NULL),
(2, 'Goblin Scout', 'monster', 'A sneaky goblin often found in forests.', 1, 1, NULL),
(3, 'Eldermoor', 'location', 'A haunted forest shrouded in mist.', 1, 1, NULL),
(4, 'Aqua Serpent', 'monster', 'A giant snake that lurks underwater.', 2, 1, NULL);

-- Insert entities (characters and monsters tied to notecards)
INSERT INTO `entity` (`id`, `note_id`, `entity_type`, `level`, `class`, `race`, `strength`, `dexterity`, `constitution`, `intelligence`, `wisdom`, `charisma`) VALUES
(1, 1, 'character', 5, 'Paladin', 'Human', 16, 12, 14, 10, 13, 15),
(2, 2, 'monster', 1, NULL, 'Goblin', 8, 14, 10, 8, 10, 6),
(3, 4, 'monster', 3, NULL, 'Serpent', 18, 14, 16, 2, 12, 5);

-- Insert features
INSERT INTO `feature` (`id`, `note_id`, `modifier_text`) VALUES
(1, 1, '+2 bonus to saving throws against magic.'),
(2, 2, 'Stealth advantage in forest terrain.');

-- Link entities to features
INSERT INTO `entity_feature` (`entity_id`, `feature_id`) VALUES
(1, 1),
(2, 2);

-- Insert spells
INSERT INTO `spells` (`id`, `note_id`, `level`, `school`, `spell_text`, `damage_type`, `damage`, `save`) VALUES
(1, 5, 1, 'Evocation', 'A blast of fire that scorches enemies.', 'fire', 8, 14),
(2, 6, 2, 'Illusion', 'Creates a duplicate image to distract foes.', 'psychic', 0, 13);

-- Insert notecards for spells (spells also need associated notecards)
INSERT INTO `notecard` (`id`, `name`, `type`, `text`, `campaign_id`, `public`, `note_image_path`) VALUES
(5, 'Fire Blast', 'spell', 'A first-level fire spell.', 1, 1, NULL),
(6, 'Mirror Image', 'spell', 'Creates illusionary duplicates.', 1, 1, NULL);

-- Link entities to spells
INSERT INTO `entity_spell` (`entity_id`, `spell_id`) VALUES
(1, 1);  -- Sir Galen knows Fire Blast

-- Insert tags
INSERT INTO `tag` (`id`, `name`) VALUES
(1, 'Hero'),
(2, 'Monster'),
(3, 'Forest'),
(4, 'Water');

-- Link notecards to tags
INSERT INTO `notecard_tag` (`note_id`, `tag_id`) VALUES
(1, 1),
(2, 2),
(3, 3),
(4, 4);

-- Insert locations (optional: for nested locations, parent_location_id can be set to another location's id)
INSERT INTO `location` (`id`, `note_id`, `parent_location_id`, `location_type`) VALUES
(1, 3, 0, 'Forest');

-- Insert user notes (user private notes about notecards)
INSERT INTO `user_note` (`user_id`, `note_id`, `note_text`) VALUES
(2, 1, 'Sir Galen owes me a favor.'),
(3, 2, 'Beware: Goblin Scouts travel in packs.');

COMMIT;
