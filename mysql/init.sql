CREATE DATABASE IF NOT EXISTS demo_db;
USE demo_db;

CREATE TABLE Users (
    UserId INT PRIMARY KEY AUTO_INCREMENT,
    FirstName VARCHAR(50),
    LastName VARCHAR(50),
    EmailAddress VARCHAR(100),
    CreatedAt DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE OrderDetails (
    OrderId INT PRIMARY KEY AUTO_INCREMENT,
    UserId INT,
    ProductName VARCHAR(100),
    OrderAmount DECIMAL(10,2),
    OrderDate DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserId) REFERENCES Users(UserId)
);

-- Insert some demo data
INSERT INTO Users (FirstName, LastName, EmailAddress) VALUES
    ('John', 'Doe', 'john.doe@example.com'),
    ('Jane', 'Smith', 'jane.smith@example.com');

INSERT INTO OrderDetails (UserId, ProductName, OrderAmount) VALUES
    (1, 'Laptop', 1299.99),
    (1, 'Mouse', 24.99),
    (2, 'Keyboard', 99.99);
