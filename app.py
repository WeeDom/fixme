"""Main Flask application for FixMe pixel art platform."""
import os
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
from dotenv import load_dotenv
import stripe
import redis
import json
from datetime import datetime
import secrets

from models import db, Project, PixelHistory, User

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///fixme.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize Redis
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
try:
    redis_client = redis.from_url(redis_url)
except Exception as e:
    print(f"Redis connection failed: {e}")
    redis_client = None

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
STRIPE_PUBLIC_KEY = os.getenv('STRIPE_PUBLIC_KEY', '')
PIXEL_PRICE_CENTS = int(os.getenv('PIXEL_PRICE_CENTS', 100))


@app.route('/')
def index():
    """Main page with pixel art canvas."""
    projects = Project.query.filter_by(is_active=True).all()
    return render_template('index.html', 
                         projects=projects,
                         stripe_public_key=STRIPE_PUBLIC_KEY,
                         pixel_price=PIXEL_PRICE_CENTS)


@app.route('/admin')
def admin():
    """Admin panel for project management."""
    # Simple authentication check (in production, use proper auth)
    admin_user = request.args.get('user')
    admin_pass = request.args.get('pass')
    
    if admin_user == os.getenv('ADMIN_USERNAME') and admin_pass == os.getenv('ADMIN_PASSWORD'):
        projects = Project.query.all()
        return render_template('admin.html', projects=projects)
    
    return 'Unauthorized', 401


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """Get all active projects."""
    projects = Project.query.filter_by(is_active=True).all()
    return jsonify([p.to_dict() for p in projects])


@app.route('/api/projects', methods=['POST'])
def create_project():
    """Create a new project (admin only)."""
    data = request.json
    
    project = Project(
        name=data.get('name'),
        description=data.get('description'),
        original_image_url=data.get('original_image_url'),
        width=data.get('width', 100),
        height=data.get('height', 100)
    )
    
    db.session.add(project)
    db.session.commit()
    
    return jsonify(project.to_dict()), 201


@app.route('/api/projects/<int:project_id>/pixels', methods=['GET'])
def get_project_pixels(project_id):
    """Get all pixels for a project."""
    pixels = PixelHistory.query.filter_by(project_id=project_id).order_by(PixelHistory.timestamp).all()
    return jsonify([p.to_dict() for p in pixels])


@app.route('/api/projects/<int:project_id>/current-state', methods=['GET'])
def get_current_state(project_id):
    """Get the current state of the canvas (latest pixel for each coordinate)."""
    project = Project.query.get_or_404(project_id)
    
    # Get the latest pixel for each (x, y) coordinate
    pixel_dict = {}
    pixels = PixelHistory.query.filter_by(project_id=project_id).order_by(PixelHistory.timestamp).all()
    
    for pixel in pixels:
        key = f"{pixel.x},{pixel.y}"
        pixel_dict[key] = {
            'x': pixel.x,
            'y': pixel.y,
            'red': pixel.red,
            'green': pixel.green,
            'blue': pixel.blue
        }
    
    return jsonify({
        'project': project.to_dict(),
        'pixels': list(pixel_dict.values())
    })


@app.route('/api/create-payment-intent', methods=['POST'])
def create_payment_intent():
    """Create a Stripe payment intent for pixel purchase."""
    try:
        data = request.json
        
        intent = stripe.PaymentIntent.create(
            amount=PIXEL_PRICE_CENTS,
            currency='usd',
            metadata={
                'project_id': data.get('project_id'),
                'x': data.get('x'),
                'y': data.get('y'),
                'red': data.get('red'),
                'green': data.get('green'),
                'blue': data.get('blue')
            }
        )
        
        return jsonify({
            'client_secret': intent.client_secret,
            'payment_intent_id': intent.id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/confirm-pixel', methods=['POST'])
def confirm_pixel():
    """Confirm pixel payment and save to database."""
    try:
        data = request.json
        payment_id = data.get('payment_id')
        
        # Verify payment with Stripe
        payment_intent = stripe.PaymentIntent.retrieve(payment_id)
        
        if payment_intent.status == 'succeeded':
            # Extract metadata
            metadata = payment_intent.metadata
            
            # Create user session ID if not exists
            if 'user_id' not in session:
                session['user_id'] = secrets.token_hex(16)
            
            user_id = session['user_id']
            
            # Save pixel to database
            pixel = PixelHistory(
                project_id=int(metadata['project_id']),
                x=int(metadata['x']),
                y=int(metadata['y']),
                red=int(metadata['red']),
                green=int(metadata['green']),
                blue=int(metadata['blue']),
                user_id=user_id,
                payment_id=payment_id
            )
            
            db.session.add(pixel)
            db.session.commit()
            
            # Broadcast pixel update via WebSocket
            socketio.emit('pixel_update', {
                'project_id': pixel.project_id,
                'x': pixel.x,
                'y': pixel.y,
                'red': pixel.red,
                'green': pixel.green,
                'blue': pixel.blue,
                'timestamp': pixel.timestamp.isoformat()
            }, broadcast=True)
            
            return jsonify({'success': True, 'pixel': pixel.to_dict()})
        else:
            return jsonify({'error': 'Payment not completed'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 400


# WebSocket event handlers
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connected', {'message': 'Connected to FixMe server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


@socketio.on('request_canvas_state')
def handle_canvas_state_request(data):
    """Send current canvas state to requesting client."""
    project_id = data.get('project_id', 1)
    
    # Get current state from database
    pixel_dict = {}
    pixels = PixelHistory.query.filter_by(project_id=project_id).order_by(PixelHistory.timestamp).all()
    
    for pixel in pixels:
        key = f"{pixel.x},{pixel.y}"
        pixel_dict[key] = {
            'x': pixel.x,
            'y': pixel.y,
            'red': pixel.red,
            'green': pixel.green,
            'blue': pixel.blue
        }
    
    emit('canvas_state', {'pixels': list(pixel_dict.values())})


def init_db():
    """Initialize the database."""
    with app.app_context():
        db.create_all()
        
        # Create default project if none exists
        if Project.query.count() == 0:
            default_project = Project(
                name='Fix My Art',
                description='Help fix this intentionally botched pixel art!',
                width=100,
                height=100
            )
            db.session.add(default_project)
            db.session.commit()
            print('Created default project')


if __name__ == '__main__':
    init_db()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)
