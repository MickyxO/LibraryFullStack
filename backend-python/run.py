from config import app, db  # Importamos la app y db ya configuradas
from models import Book, User, Movement, Payment  # Importamos los modelos
from flask import jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


#Rutas basicas. Endpoints
#Libros
@app.route('/books', methods=['GET'])
def get_books():
    books = Book.query.all()
    return jsonify([{
        'id' : book.id,
        'title' : book.title,
        'price' : float(book.price),
        'author' : book.author
    } for book in books])

@app.route('/books', methods=['POST'])
def add_book():
    data = request.json
    new_book = Book(
        title = data['title'],
        author = data['author'],
        isbn = data['isbn'],
        price = data['price'],
        stock = data.get('stock', 0)
    )
    db.session.add(new_book)
    db.session.commit()
    return jsonify({'message' : 'Libro creado!', 'id': new_book.id }), 201


#Usuarios

@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    return jsonify([{
        'id' : user.id,
        'name' : user.name,
        'email' : user.email,
        'role' : user.role
    }] for user in users)

@app.route('/users', methods=['POST'])
def create_user():
    try:
        data = request.json
        new_user = User(
            name=data['name'],
            email=data['email'],
            role=data.get('role', 'CLIENT')
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({'message': 'Usuario creado!', 'id': new_user.id}), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400  # Código 400 para errores de validación
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'email': user.email
    })

# GET: Listar todos los movimientos
@app.route('/movements', methods=['GET'])
def get_movements():
    movements = Movement.query.all()
    return jsonify([{
        'id': movement.id,
        'user_id': movement.user_id,
        'book_id': movement.book_id,
        'type': movement.type,
        'status': movement.status,
        'movement_date': movement.movement_date.isoformat() if movement.movement_date else None
    } for movement in movements])

# POST: Crear un nuevo movimiento (ej: alquiler/compra)
@app.route('/movements', methods=['POST'])
def create_movement():
    try:
        data = request.json
        
        # 1. Validar que el libro exista
        book = Book.query.get(data['book_id'])
        if not book:
            return jsonify({'error': 'El libro no existe'}), 400

        # 2. Asignar fechas automáticamente
        movement_date = datetime.now()
        return_date = None
        
        if data['type'] == 'RENT':
            # 7 dias de renta
            return_date = movement_date + timedelta(days=7)

        new_movement = Movement(
            user_id=data['user_id'],
            book_id=data['book_id'],
            type=data['type'],
            quantity=data.get('quantity', 1),
            movement_date=movement_date,  
            return_date=return_date,      
            status='PENDING'  
        )

        
        db.session.add(new_movement)
        db.session.commit()
        
        return jsonify({
            'message': 'Movimiento creado!',
            'movement_date': movement_date.isoformat(),
            'return_date': return_date.isoformat() if return_date else None
        }), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400  # Errores de validación
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({'error': 'Error en la base de datos'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Error interno del servidor'}), 500

#ENDPOINT para actualizar el estado de un movimiento
@app.route('/movements/<int:movement_id>/status', methods=['PATCH'])
def update_movement_status(movement_id):
    movement = Movement.query.get_or_404(movement_id)
    data = request.json
    movement.status = data['status']  # 'COMPLETED', 'CANCELLED'
    db.session.commit()
    return jsonify({'message': 'Estado actualizado!'})

#GET: Obtener todos los pagos
@app.route('/payments', methods=['GET'])
def get_payments():
    payments = Payment.query.all()
    return jsonify([{
        'id' : payment.id,
        'movement' : payment.movement_id,
        'amount' : float(payment.amount),
        'method' : str(payment.method),
        'payment_date' : payment.payment_date.isoformat(),
        'status' : str(payment.status)
    }] for payment in payments)

# POST: Registrar un pago asociado a un movimiento
@app.route('/payments', methods=['POST'])
def create_payment():
    try:
        data = request.json
        new_payment = Payment(
            movement_id=data['movement_id'],
            amount=data['amount'],
            method=data['method'],  # 'CASH', 'CARD', 'TRANSFER'
            status=data.get('status', 'PENDING')
        )
        db.session.add(new_payment)
        db.session.commit()
        return jsonify({'message': 'Pago registrado!', 'id': new_payment.id}), 201
    
    except ValueError as e:
        return jsonify({'error': str(e)}), 400  # Error de validación
    except Exception as e:
        return jsonify({'error': 'Error interno'}), 500

# GET: Listar pagos de un movimiento específico
@app.route('/movements/<int:movement_id>/payments', methods=['GET'])
def get_movement_payments(movement_id):
    payments = Payment.query.filter_by(movement_id=movement_id).all()
    return jsonify([{
        'id': payment.id,
        'amount': float(payment.amount),
        'method': payment.method,
        'status': payment.status
    } for payment in payments])





if __name__ == '__main__':
    app.run(debug=True, port=5000)