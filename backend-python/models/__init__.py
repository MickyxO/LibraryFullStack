from flask_sqlalchemy import SQLAlchemy
import re
from flask import current_app
from sqlalchemy.orm import validates
from datetime import datetime

db = SQLAlchemy()

# Modelo User (usuarios)
class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    role = db.Column(db.String(20), default='CLIENT')  # ENUM se traduce como String
    created_at = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())

    #Se corre automaticamente al agregar o actualizar la informacion del email
    @validates('email')
    def validate_email(self, key, email):
        if not email:
            raise ValueError("El email no puede estar vacío")
        
        # Patrón regex para validar emails estándar
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            raise ValueError("Formato de email inválido")
        
        # Verificar unicidad (opcional, ya que la columna es 'unique')
        if User.query.filter(User.email == email).first() and getattr(self, 'id') is None:
            raise ValueError("El email ya está registrado")
        
        return email

    # Relación con Movement (opcional, para acceder desde User)
    movements = db.relationship('Movement', backref='user', lazy=True)

    def __repr__(self):
        return f'<User {self.email}>'

# Modelo Book (libros)
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(100), unique=True, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL(10,2)
    stock = db.Column(db.Integer, default=0)
    is_available = db.Column(db.Boolean, default=True)

    # Relación con Movement (opcional)
    movements = db.relationship('Movement', backref='book', lazy=True)

    def __repr__(self):
        return f'<Book {self.title}>'

# Modelo Movement (movimientos)
class Movement(db.Model):
    __tablename__ = 'movements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # ENUM como String
    quantity = db.Column(db.Integer, default=1)
    movement_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    return_date = db.Column(db.TIMESTAMP, nullable=True)  # Solo para alquileres
    status = db.Column(db.String(20), default='PENDING')  # ENUM como String

    @validates('return_date')
    def validate_return_date(self, key, return_date):
        if return_date is not None:
            if self.type == 'RENT':
                if return_date <= datetime.now():
                    raise ValueError("La fecha de retorno debe ser mayor a la fecha actual.")
            elif self.type == 'PURCHASE' and return_date is not None:
                raise ValueError("Una purchase no debe de tener fecha de retorno.")
        return return_date    
    
    @validates('user_id')
    def validate_user(self, key, user_id):
        if not User.query.get(user_id):
            raise ValueError("El usuario no existe. ")
        return user_id
    
    @validates('status')
    def validate_status(self, key, status):
        if status not in {'PENDING', 'COMPLETED', 'CANCELLED'}:
            raise ValueError(f"Estado invalido. Usa: {'PENDING, COMPLETED, CANCELED'}")

    @validates('type')
    def validate_type(self, key, type):
        valid_types = {'RENT', 'PURCHASE', 'RETURN'}
        if type not in valid_types:
            raise ValueError(f"Tipo de movimiento invalido. Usa: {valid_types}")
        return type

    #key es la llave que estamos validando, value es el valor que le estamos dando en ese momento
    @validates('book_id', 'type', 'quantity')
    def validate_stock(self, key, value):
        if key == 'book_id' and hasattr(self, 'type') and self.type in {'RENT', 'PURCHASE'}:
            book = Book.query.get(value)
            if book.stock < self.quantity:
                raise ValueError("Stock insuficiente para este movimiento. ")
        return value        
    


    # Relación con Payment (opcional)
    payment = db.relationship('Payment', backref='movement', uselist=False)

    def __repr__(self):
        return f'<Movement {self.type} - {self.status}>'

# Modelo Payment (pagos)
class Payment(db.Model):
    __tablename__ = 'payments'

    id = db.Column(db.Integer, primary_key=True)
    movement_id = db.Column(db.Integer, db.ForeignKey('movements.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)  # DECIMAL(10,2)
    method = db.Column(db.String(20), nullable=False)  # ENUM como String
    payment_date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    status = db.Column(db.String(20), default='PENDING')  # ENUM como String

    @validates('movement_id')
    def validate_movement_id(self, key, movement_id):
        if movement_id is not None:
            if not Movement.query.get(movement_id):
                raise ValueError("El movimiento no existe. ")
        else:
            raise ValueError("No hay un movimiento id.")
        return movement_id

    @validates('amount', 'movement_id')
    def validate_amount(self, key, value):
        if key == 'movement_id':
            movement  = Movement.query.get(value)
            if movement.type == 'PURCHASE':
                book = Book.query.get(movement.book_id)
                if getattr(self, 'amount', None) is None:
                    self.amount = book.price * movement.quantity
        return value            


    def __repr__(self):
        return f'<Payment {self.method} - {self.amount}>'