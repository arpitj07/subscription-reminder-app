"""
Subscription Reminder App - Updated for Cloud Hosting
Optimized for FREE hosting on Render.com
"""

import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import json

app = Flask(__name__)
CORS(app)

# Database configuration - works with free hosting
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # For cloud hosting
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # For local development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///subscriptions.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Model
class Subscription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    renewal_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Float, default=0)
    reminder_days = db.Column(db.Integer, default=3)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        days_left = (self.renewal_date - datetime.now().date()).days
        status = 'critical' if days_left < 0 else 'warning' if days_left <= 3 else 'success'

        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'renewal_date': self.renewal_date.isoformat(),
            'cost': self.cost,
            'reminder_days': self.reminder_days,
            'notes': self.notes,
            'days_left': days_left,
            'status': status,
            'created_at': self.created_at.isoformat()
        }

# Create tables on startup
with app.app_context():
    db.create_all()

# ==================== API Routes ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the main dashboard"""
    return render_template('index.html')

@app.route('/api/subscriptions', methods=['GET'])
def get_subscriptions():
    """Get all subscriptions with optional filtering"""
    category = request.args.get('category')
    filter_type = request.args.get('filter')

    query = Subscription.query

    if category and category != 'all':
        query = query.filter_by(category=category)

    subscriptions = query.all()

    if filter_type == 'critical':
        subscriptions = [s for s in subscriptions if s.to_dict()['status'] == 'critical']

    return jsonify([s.to_dict() for s in subscriptions])

@app.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    data = request.json

    try:
        subscription = Subscription(
            name=data['name'],
            category=data['category'],
            renewal_date=datetime.fromisoformat(data['renewal_date']).date(),
            cost=data.get('cost', 0),
            reminder_days=data.get('reminder_days', 3),
            notes=data.get('notes', '')
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Subscription added successfully',
            'data': subscription.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/subscriptions/<int:id>', methods=['GET'])
def get_subscription(id):
    """Get a specific subscription"""
    subscription = Subscription.query.get(id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404
    return jsonify(subscription.to_dict())

@app.route('/api/subscriptions/<int:id>', methods=['PUT'])
def update_subscription(id):
    """Update a subscription"""
    subscription = Subscription.query.get(id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    data = request.json

    try:
        if 'name' in data:
            subscription.name = data['name']
        if 'category' in data:
            subscription.category = data['category']
        if 'renewal_date' in data:
            subscription.renewal_date = datetime.fromisoformat(data['renewal_date']).date()
        if 'cost' in data:
            subscription.cost = data['cost']
        if 'reminder_days' in data:
            subscription.reminder_days = data['reminder_days']
        if 'notes' in data:
            subscription.notes = data['notes']

        subscription.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Subscription updated successfully',
            'data': subscription.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/subscriptions/<int:id>', methods=['DELETE'])
def delete_subscription(id):
    """Delete a subscription"""
    subscription = Subscription.query.get(id)
    if not subscription:
        return jsonify({'error': 'Subscription not found'}), 404

    try:
        db.session.delete(subscription)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Subscription deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    subscriptions = Subscription.query.all()
    today = datetime.now().date()

    total = len(subscriptions)
    due_soon = len([s for s in subscriptions if 0 <= (s.renewal_date - today).days <= 7])
    monthly_spend = sum(s.cost for s in subscriptions)
    overdue = len([s for s in subscriptions if (s.renewal_date - today).days < 0])

    return jsonify({
        'total_subscriptions': total,
        'due_soon': due_soon,
        'monthly_spend': monthly_spend,
        'overdue': overdue
    })

@app.route('/api/export', methods=['GET'])
def export_data():
    """Export all subscriptions as JSON"""
    subscriptions = Subscription.query.all()
    data = [s.to_dict() for s in subscriptions]
    return jsonify(data)

@app.route('/api/import', methods=['POST'])
def import_data():
    """Import subscriptions from JSON"""
    try:
        data = request.json

        if not isinstance(data, list):
            return jsonify({'error': 'Data must be a list'}), 400

        for item in data:
            subscription = Subscription(
                name=item['name'],
                category=item['category'],
                renewal_date=datetime.fromisoformat(item['renewal_date']).date(),
                cost=item.get('cost', 0),
                reminder_days=item.get('reminder_days', 3),
                notes=item.get('notes', '')
            )
            db.session.add(subscription)

        db.session.commit()

        return jsonify({
            'success': True,
            'message': f'Imported {len(data)} subscriptions'
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 400

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# Health check for free hosting
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    # Use PORT environment variable if available (for cloud hosting)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)