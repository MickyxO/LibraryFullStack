-- Usuarios de ejemplo
INSERT INTO users (name, email, role) VALUES 
('Admin', 'admin@libreria.com', 'ADMIN'),
('Cliente 1', 'cliente1@email.com', 'CLIENT');

-- Libros de ejemplo
INSERT INTO books (title, author, isbn, price, stock) VALUES 
('Cien años de soledad', 'Gabriel García Márquez', '9781234567890', 25.99, 10),
('El principito', 'Antoine de Saint-Exupéry', '9789876543210', 15.50, 5);

-- Movimiento de alquiler
INSERT INTO movements (user_id, book_id, type, return_date, status) VALUES 
(2, 1, 'RENT', DATE_ADD(NOW(), INTERVAL 7 DAY), 'COMPLETED');

-- Pago asociado
INSERT INTO payments (movement_id, amount, method, status) VALUES 
(1, 25.99, 'CARD', 'PAID');