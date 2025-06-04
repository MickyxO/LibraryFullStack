    -- Tabla de usuarios
    CREATE TABLE users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        role ENUM('CLIENT', 'ADMIN') DEFAULT 'CLIENT',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Tabla de libros
    CREATE TABLE books (
        id INT AUTO_INCREMENT PRIMARY KEY,
        title VARCHAR(200) NOT NULL,
        author VARCHAR(100) NOT NULL,
        isbn VARCHAR(100) UNIQUE NOT NULL,
        price DECIMAL(10,2) NOT NULL,
        stock INT DEFAULT 0,
        is_available BOOLEAN DEFAULT TRUE
    );

    -- Tabla de movimientos (transacciones)
CREATE TABLE movements (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    type ENUM('RENT', 'PURCHASE', 'RETURN') NOT NULL,
    quantity INT DEFAULT 1,
    movement_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    return_date TIMESTAMP NULL, -- Solo para alquileres
    status ENUM('PENDING', 'COMPLETED', 'CANCELLED') DEFAULT 'PENDING',
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (book_id) REFERENCES books(id)
);

-- Tabla de pagos
CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    movement_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    method ENUM('CASH', 'CARD', 'TRANSFER') NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status ENUM('PAID', 'PENDING', 'REFUNDED') DEFAULT 'PENDING',
    FOREIGN KEY (movement_id) REFERENCES movements(id)
);