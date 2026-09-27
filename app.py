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
    person_name = db.Column(db.String(100), default='Self')  # Family member name
    start_date = db.Column(db.Date)  # Optional start date
    renewal_date = db.Column(db.Date, nullable=False)
    cost = db.Column(db.Float, default=0)
    subscription_type = db.Column(db.String(20), default='Monthly')  # Monthly, Yearly, Half-yearly, Quarterly, Custom
    period_days = db.Column(db.Integer, default=30)  # Period in days (30, 84, 330, etc.)
    is_recurring = db.Column(db.Boolean, default=True)  # True=recurring, False=one-time
    parent_subscription_id = db.Column(db.Integer, db.ForeignKey('subscription.id'), nullable=True)  # For add-ons
    reminder_days = db.Column(db.Integer, default=3)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self, include_addons=True):
        days_left = (self.renewal_date - datetime.now().date()).days
        status = 'critical' if days_left < 0 else 'warning' if days_left <= 3 else 'success'

        # Calculate monthly equivalent cost
        monthly_cost = calculate_monthly_cost(self)

        # Get add-ons if this is a parent subscription
        addons = []
        if include_addons and self.parent_subscription_id is None:
            child_subs = Subscription.query.filter_by(parent_subscription_id=self.id).all()
            addons = [{'id': c.id, 'name': c.name, 'category': c.category} for c in child_subs]

        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'renewal_date': self.renewal_date.isoformat(),
            'cost': self.cost,
            'person_name': self.person_name,
            'subscription_type': self.subscription_type,
            'period_days': self.period_days,
            'is_recurring': self.is_recurring,
            'monthly_cost': round(monthly_cost, 2),
            'parent_subscription_id': self.parent_subscription_id,
            'addons': addons,
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
    person = request.args.get('person')
    filter_type = request.args.get('filter')

    query = Subscription.query.filter_by(parent_subscription_id=None)  # Only root subscriptions

    if category and category != 'all':
        query = query.filter_by(category=category)

    if person:
        query = query.filter_by(person_name=person)

    subscriptions = query.all()

    if filter_type == 'critical':
        subscriptions = [s for s in subscriptions if s.to_dict()['status'] == 'critical']

    return jsonify([s.to_dict() for s in subscriptions])

@app.route('/api/subscriptions', methods=['POST'])
def create_subscription():
    """Create a new subscription"""
    data = request.json

    try:
        start_date = None
        if data.get('start_date'):
            start_date = datetime.fromisoformat(data['start_date']).date()

        # Calculate period_days based on subscription_type
        sub_type = data.get('subscription_type', 'Monthly')
        if sub_type == 'Custom':
            period_days = data.get('period_days', 30)
        elif sub_type == 'Yearly':
            period_days = 365
        elif sub_type == 'Half-yearly':
            period_days = 180
        elif sub_type == 'Quarterly':
            period_days = 90
        else:  # Monthly
            period_days = 30

        subscription = Subscription(
            name=data['name'],
            category=data['category'],
            start_date=start_date,
            renewal_date=datetime.fromisoformat(data['renewal_date']).date(),
            cost=data.get('cost', 0),
            subscription_type=sub_type,
            period_days=period_days,
            is_recurring=data.get('is_recurring', True),
            parent_subscription_id=data.get('parent_subscription_id'),
            person_name=data.get('person_name', 'Self'),
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
        if 'start_date' in data:
            subscription.start_date = datetime.fromisoformat(data['start_date']).date() if data['start_date'] else None
        if 'renewal_date' in data:
            subscription.renewal_date = datetime.fromisoformat(data['renewal_date']).date()
        if 'cost' in data:
            subscription.cost = data['cost']
        if 'subscription_type' in data:
            subscription.subscription_type = data['subscription_type']
            # Auto-calculate period_days based on type
            if data['subscription_type'] == 'Custom':
                subscription.period_days = data.get('period_days', 30)
            elif data['subscription_type'] == 'Yearly':
                subscription.period_days = 365
            elif data['subscription_type'] == 'Half-yearly':
                subscription.period_days = 180
            elif data['subscription_type'] == 'Quarterly':
                subscription.period_days = 90
            else:  # Monthly
                subscription.period_days = 30
        if 'period_days' in data:
            subscription.period_days = data['period_days']
        if 'is_recurring' in data:
            subscription.is_recurring = data['is_recurring']
        if 'parent_subscription_id' in data:
            subscription.parent_subscription_id = data['parent_subscription_id']
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

def calculate_monthly_cost(subscription):
    """Calculate monthly equivalent cost based on period and recurrence"""
    if not subscription.is_recurring:
        return 0  # One-time payments don't contribute to monthly spend

    cost = subscription.cost or 0
    period_days = subscription.period_days or 30

    # Convert to monthly cost (30-day month)
    monthly_cost = (cost / period_days) * 30
    return monthly_cost

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    subscriptions = Subscription.query.filter_by(parent_subscription_id=None).all()  # Only root subscriptions
    today = datetime.now().date()

    total = len(subscriptions)
    due_soon = len([s for s in subscriptions if 0 <= (s.renewal_date - today).days <= 7])
    monthly_spend = sum(calculate_monthly_cost(s) for s in subscriptions)
    overdue = len([s for s in subscriptions if (s.renewal_date - today).days < 0])

    return jsonify({
        'total_subscriptions': total,
        'due_soon': due_soon,
        'monthly_spend': round(monthly_spend, 2),
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
            start_date = None
            if item.get('start_date'):
                start_date = datetime.fromisoformat(item['start_date']).date()

            subscription = Subscription(
                name=item['name'],
                category=item['category'],
                start_date=start_date,
                renewal_date=datetime.fromisoformat(item['renewal_date']).date(),
                cost=item.get('cost', 0),
                subscription_type=item.get('subscription_type', 'Monthly'),
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

@app.route('/api/people', methods=['GET'])
def get_people():
    """Get list of all family members"""
    people = db.session.query(Subscription.person_name).distinct().all()
    return jsonify([p[0] for p in people if p[0]])

@app.route('/static/logos/<path:filename>')
def serve_logo(filename):
    """Serve brand logo SVG assets"""
    from flask import send_from_directory
    return send_from_directory(os.path.join(os.path.dirname(__file__), 'static', 'logos'), filename)

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