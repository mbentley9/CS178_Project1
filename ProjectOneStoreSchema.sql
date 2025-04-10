-- Create the database
CREATE DATABASE ProjectOneStoreSchema;
USE ProjectOneStoreSchema;

-- Create the Category table
CREATE TABLE Category (
    categoryID INT PRIMARY KEY,
    name VARCHAR(50)
);

-- Insert categories
INSERT INTO Category (categoryID, name) VALUES
(1, 'Destinations'),
(2, 'Activities'),
(3, 'Travel Gear');

-- Create the Inventory table
CREATE TABLE Inventory (
    ID INT PRIMARY KEY,
    description VARCHAR(100),
    price FLOAT,
    categoryID INT,
    FOREIGN KEY (categoryID) REFERENCES Category(categoryID)
);

-- Insert 10 travel-related items
INSERT INTO Inventory (ID, description, price, categoryID) VALUES
(1, 'Bali, Indonesia – 7-Night Beach Resort', 1299.00, 1),
(2, 'Swiss Alps – Ski Weekend', 999.99, 1),
(3, 'Tokyo, Japan – 5-Day City Adventure', 1450.50, 1),
(4, 'Snorkeling with Sea Turtles – Hawaii', 89.99, 2),
(5, 'Hot Air Balloon Ride – Cappadocia', 150.00, 2),
(6, 'Cooking Class – Tuscan Countryside', 95.00, 2),
(7, 'Waterproof Travel Backpack', 75.00, 3),
(8, 'Universal Power Adapter', 25.99, 3),
(9, 'Noise-Cancelling Travel Headphones', 199.00, 3),
(10, 'Neck Pillow & Eye Mask Combo', 19.99, 3);
