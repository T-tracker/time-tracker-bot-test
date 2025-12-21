# app/routes/web_routes.py
from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app import db
from app.models import Category, Event
from datetime import datetime

web_bp = Blueprint('web', __name__, url_prefix='/api/v1')


@web_bp.route('/categories', methods=['GET'])
@login_required  # Только для авторизованных
def get_categories():
    """Получить ВСЕ категории текущего пользователя"""

    # current_user доступен благодаря flask_login
    categories = Category.query.filter_by(user_id=current_user.id).all()

    # Используем метод to_dict() из модели
    categories_list = [cat.to_dict() for cat in categories]

    return jsonify({
        'status': 'success',
        'count': len(categories_list),
        'categories': categories_list
    })


@web_bp.route('/events', methods=['POST'])
@login_required
def create_event():
    """Создать новое событие (план) из веб-интерфейса"""
    data = request.get_json()

    # Проверяем обязательные поля
    required = ['category_id', 'start_time', 'end_time']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Проверяем, что категория принадлежит пользователю
    category = Category.query.filter_by(
        id=data['category_id'],
        user_id=current_user.id
    ).first()

    if not category:
        return jsonify({'error': 'Category not found'}), 404

    # Создаём событие (по умолчанию type='plan', source='web')
    event = Event(
        user_id=current_user.id,
        category_id=data['category_id'],
        start_time=datetime.fromisoformat(data['start_time']),
        end_time=datetime.fromisoformat(data['end_time']),
        type=data.get('type', 'plan'),  # По умолчанию 'plan'
        source='web'  # Событие из веб-интерфейса
    )

    db.session.add(event)
    db.session.commit()

    return jsonify({
        'status': 'success',
        'event_id': event.id,
        'message': 'Event created successfully'
    }), 201