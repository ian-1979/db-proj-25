-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 27, 2025 at 10:34 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dbdatabase1`
--
CREATE DATABASE IF NOT EXISTS `dbdatabase1` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `dbdatabase1`;

-- --------------------------------------------------------

--
-- Table structure for table `campaign`
--

DROP TABLE IF EXISTS `campaign`;
CREATE TABLE `campaign` (
  `id` int(11) NOT NULL,
  `name` tinytext NOT NULL,
  `description` text DEFAULT NULL,
  `campaign_image_path` tinytext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `campaign`:
--

-- --------------------------------------------------------

--
-- Table structure for table `entity`
--

DROP TABLE IF EXISTS `entity`;
CREATE TABLE `entity` (
  `id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL,
  `entity_type` enum('character','monster','npc','location','spell','feature') NOT NULL,
  `level` int(11) DEFAULT NULL,
  `class` tinytext DEFAULT NULL,
  `race` tinytext DEFAULT NULL,
  `strength` int(11) DEFAULT NULL,
  `dexterity` int(11) DEFAULT NULL,
  `constitution` int(11) DEFAULT NULL,
  `intelligence` int(11) DEFAULT NULL,
  `wisdom` int(11) DEFAULT NULL,
  `charisma` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `entity`:
--   `note_id`
--       `notecard` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `entity_feature`
--

DROP TABLE IF EXISTS `entity_feature`;
CREATE TABLE `entity_feature` (
  `entity_id` int(11) NOT NULL,
  `feature_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `entity_feature`:
--   `entity_id`
--       `entity` -> `id`
--   `feature_id`
--       `feature` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `entity_spell`
--

DROP TABLE IF EXISTS `entity_spell`;
CREATE TABLE `entity_spell` (
  `entity_id` int(11) NOT NULL,
  `spell_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `entity_spell`:
--   `entity_id`
--       `entity` -> `id`
--   `spell_id`
--       `spells` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `feature`
--

DROP TABLE IF EXISTS `feature`;
CREATE TABLE `feature` (
  `id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL,
  `modifier_text` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `feature`:
--   `note_id`
--       `notecard` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `location`
--

DROP TABLE IF EXISTS `location`;
CREATE TABLE `location` (
  `id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL,
  `parent_location_id` int(11) NOT NULL,
  `location_type` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `location`:
--   `note_id`
--       `notecard` -> `id`
--   `parent_location_id`
--       `location` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `notecard`
--

DROP TABLE IF EXISTS `notecard`;
CREATE TABLE `notecard` (
  `id` int(11) NOT NULL,
  `name` tinytext NOT NULL,
  `type` enum('character','monster','npc','location') NOT NULL,
  `text` text DEFAULT NULL,
  `campaign_id` int(11) NOT NULL,
  `public` tinyint(1) NOT NULL,
  `note_image_path` tinytext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `notecard`:
--   `campaign_id`
--       `campaign` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `notecard_tag`
--

DROP TABLE IF EXISTS `notecard_tag`;
CREATE TABLE `notecard_tag` (
  `note_id` int(11) NOT NULL,
  `tag_id` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `notecard_tag`:
--   `note_id`
--       `notecard` -> `id`
--   `tag_id`
--       `tag` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `spells`
--

DROP TABLE IF EXISTS `spells`;
CREATE TABLE `spells` (
  `id` int(11) NOT NULL,
  `note_id` int(11) NOT NULL,
  `level` int(11) NOT NULL,
  `school` tinytext NOT NULL,
  `spell_text` text DEFAULT NULL,
  `damage_type` tinytext NOT NULL,
  `damage` tinyint(4) NOT NULL,
  `save` tinyint(4) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `spells`:
--   `note_id`
--       `notecard` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `tag`
--

DROP TABLE IF EXISTS `tag`;
CREATE TABLE `tag` (
  `id` int(11) NOT NULL,
  `name` tinytext NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `tag`:
--

-- --------------------------------------------------------

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(10) UNSIGNED NOT NULL,
  `username` tinytext NOT NULL,
  `password` tinytext NOT NULL,
  `profile_image_path` tinytext DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `user`:
--

-- --------------------------------------------------------

--
-- Table structure for table `user_campaign`
--

DROP TABLE IF EXISTS `user_campaign`;
CREATE TABLE `user_campaign` (
  `user_id` int(10) NOT NULL,
  `campaign_id` int(11) NOT NULL,
  `role` enum('dm','player') DEFAULT 'player'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `user_campaign`:
--   `campaign_id`
--       `campaign` -> `id`
--   `user_id`
--       `user` -> `id`
--

-- --------------------------------------------------------

--
-- Table structure for table `user_note`
--

DROP TABLE IF EXISTS `user_note`;
CREATE TABLE `user_note` (
  `user_id` int(10) NOT NULL,
  `note_id` int(11) NOT NULL,
  `note_text` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- RELATIONSHIPS FOR TABLE `user_note`:
--   `note_id`
--       `notecard` -> `id`
--   `user_id`
--       `user` -> `id`
--

--
-- Indexes for dumped tables
--

--
-- Indexes for table `campaign`
--
ALTER TABLE `campaign`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `campname` (`name`) USING HASH;

--
-- Indexes for table `entity`
--
ALTER TABLE `entity`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `note_id` (`note_id`);

--
-- Indexes for table `entity_feature`
--
ALTER TABLE `entity_feature`
  ADD PRIMARY KEY (`entity_id`,`feature_id`);

--
-- Indexes for table `entity_spell`
--
ALTER TABLE `entity_spell`
  ADD PRIMARY KEY (`entity_id`,`spell_id`);

--
-- Indexes for table `feature`
--
ALTER TABLE `feature`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `note_id` (`note_id`);

--
-- Indexes for table `location`
--
ALTER TABLE `location`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `note_id` (`note_id`);

--
-- Indexes for table `notecard`
--
ALTER TABLE `notecard`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `notecard_tag`
--
-- ALTER TABLE `notecard_tag`
--   ADD PRIMARY KEY (`note_id`,`tag_id`);

--
-- Indexes for table `spells`
--
ALTER TABLE `spells`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `note_id` (`note_id`);

--
-- Indexes for table `tag`
--
ALTER TABLE `tag`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `Username` (`username`) USING HASH;

--
-- Indexes for table `user_campaign`
--
ALTER TABLE `user_campaign`
  ADD PRIMARY KEY (`user_id`,`campaign_id`);

--
-- Indexes for table `user_note`
--
ALTER TABLE `user_note`
  ADD PRIMARY KEY (`user_id`,`note_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `campaign`
--
ALTER TABLE `campaign`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `entity`
--
ALTER TABLE `entity`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `feature`
--
ALTER TABLE `feature`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `location`
--
ALTER TABLE `location`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notecard`
--
ALTER TABLE `notecard`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `spells`
--
ALTER TABLE `spells`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `tag`
--
ALTER TABLE `tag`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `id` int(10) UNSIGNED NOT NULL AUTO_INCREMENT;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
