-- phpMyAdmin SQL Dump
-- version 4.8.2
-- https://www.phpmyadmin.net/
--
-- Host: localhost:8889
-- Generation Time: Sep 13, 2018 at 02:09 AM
-- Server version: 5.7.21
-- PHP Version: 7.2.7

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

--
-- Database: `payroll`
--

-- --------------------------------------------------------

--
-- Table structure for table `current_period`
--

CREATE TABLE `current_period` (
  `year` int(11) NOT NULL,
  `month` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `current_period`
--

INSERT INTO `current_period` (`year`, `month`) VALUES
(2018, 8);

-- --------------------------------------------------------

--
-- Table structure for table `employee`
--

CREATE TABLE `employee` (
  `id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `employee`
--

INSERT INTO `employee` (`id`, `name`) VALUES
(1, 'Alexander Cook'),
(2, 'Christine Smellow'),
(3, 'Thomas Perchlik'),
(4, 'Sharon Helm'),
(5, 'Kyle Ridings'),
(6, 'Jennifer Conway');

-- --------------------------------------------------------

--
-- Table structure for table `landi_value`
--

CREATE TABLE `landi_value` (
  `category` varchar(25) NOT NULL,
  `year` int(11) NOT NULL,
  `value` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `landi_value`
--

INSERT INTO `landi_value` (`category`, `year`, `value`) VALUES
('ADMIN', 2018, 0.2973),
('CHILDCARE', 2018, 1.0494);

-- --------------------------------------------------------

--
-- Table structure for table `monthly_input`
--

CREATE TABLE `monthly_input` (
  `employee_id` int(11) NOT NULL,
  `input_type` varchar(50) NOT NULL,
  `value` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `monthly_input`
--

INSERT INTO `monthly_input` (`employee_id`, `input_type`, `value`) VALUES
(3, 'FB', 406.41),
(3, 'RW', 700),
(3, 'MIW', 458.04),
(1, 'HOURS', 14),
(4, 'HOURS', 52);

-- --------------------------------------------------------

--
-- Table structure for table `profile`
--

CREATE TABLE `profile` (
  `employee_id` int(11) NOT NULL,
  `landi_category` varchar(25) NOT NULL,
  `type` char(1) NOT NULL COMMENT 'H=Hourly, S=Salaried',
  `rate` double NOT NULL,
  `hours` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Dumping data for table `profile`
--

INSERT INTO `profile` (`employee_id`, `landi_category`, `type`, `rate`, `hours`) VALUES
(1, 'CHILDCARE', 'H', 14, NULL),
(2, 'ADMIN', 'S', 1574.93, 60.6666666666),
(3, 'ADMIN', 'S', 3312.5, 173.333333333),
(4, 'ADMIN', 'H', 15.61, NULL),
(5, 'CHILDCARE', 'H', 14, NULL),
(6, 'ADMIN', 'S', 1887, 86.666666666);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `employee`
--
ALTER TABLE `employee`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `landi_value`
--
ALTER TABLE `landi_value`
  ADD PRIMARY KEY (`category`,`year`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `employee`
--
ALTER TABLE `employee`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;
