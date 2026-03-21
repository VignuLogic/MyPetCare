DROP DATABASE IF EXISTS petcare;
CREATE DATABASE petcare;
USE petcare;

-- Create Database
CREATE DATABASE petcare;
USE petcare;

-- =========================
-- USERS TABLE
-- =========================
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    mobile VARCHAR(15),
    email VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =========================
-- PETS TABLE
-- =========================
CREATE TABLE pets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_name VARCHAR(100) NOT NULL,
    pet_type VARCHAR(50) NOT NULL,
    age INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- =========================
-- SERVICES TABLE (Better Design)
-- =========================
CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_name VARCHAR(100) NOT NULL
);

-- Insert Default Services
INSERT INTO services (service_name) VALUES
('Grooming'),
('Health Checkup'),
('Vaccination'),
('Pet Training');

-- =========================
-- BOOKINGS TABLE
-- =========================
CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pet_id INT NOT NULL,
    service_id INT NOT NULL,
    booking_date DATE NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
    FOREIGN KEY (service_id) REFERENCES services(id) ON DELETE CASCADE
);

USE petcare;
SELECT * FROM users;
SELECT * FROM pets;

show tables;
SELECT database();

DELETE FROM users WHERE id IN (1,2,3,4,6,9,11,12,13);