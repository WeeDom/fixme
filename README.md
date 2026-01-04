# FixMe - Collaborative Pixel Art Modification Platform

Pay per-pixel collective image repair platform where users can modify intentionally botched pixel art images.

## Features

- **HTML5 Canvas**: 100x100 pixel grid with real-time rendering
- **Click to Select**: Click any pixel to select it, choose a color, and purchase
- **Stripe Payment Integration**: Secure payment processing for pixel modifications
- **WebSocket Real-Time Updates**: See changes from other users instantly
- **PostgreSQL Backend**: Complete pixel history tracking (x, y, RGB, user_id, payment_id, timestamp)
- **Flask + Flask-SocketIO**: Robust backend with WebSocket support
- **Admin Panel**: Manage projects and moderate content
- **Redis**: WebSocket connection management
- **Tailwind CSS**: Modern, responsive UI

## Tech Stack

- **Backend**: Flask, Flask-SocketIO, PostgreSQL, Redis
- **Frontend**: HTML5 Canvas, Tailwind CSS, Socket.IO client
- **Payment**: Stripe API
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Real-time**: WebSocket via Socket.IO

## Installation

### Prerequisites

- Python 3.8+
- PostgreSQL
- Redis
- Stripe account (for payment processing)

### Setup Instructions

1. **Clone the repository**
   ```bash
   git clone https://github.com/WeeDom/fixme.git
   cd fixme
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up PostgreSQL**
   ```bash
   # Create database and user
   psql -U postgres
   CREATE DATABASE fixme_db;
   CREATE USER fixme_user WITH PASSWORD 'fixme_password';
   GRANT ALL PRIVILEGES ON DATABASE fixme_db TO fixme_user;
   \q
   ```

5. **Set up Redis**
   ```bash
   # Install Redis (Ubuntu/Debian)
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # Or using Docker
   docker run -d -p 6379:6379 redis:latest
   ```

6. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   - `SECRET_KEY`: Flask secret key
   - `DATABASE_URL`: PostgreSQL connection string
   - `REDIS_URL`: Redis connection string
   - `STRIPE_PUBLIC_KEY`: Your Stripe publishable key
   - `STRIPE_SECRET_KEY`: Your Stripe secret key
   - `STRIPE_WEBHOOK_SECRET`: Your Stripe webhook secret
   - `ADMIN_USERNAME`: Admin panel username
   - `ADMIN_PASSWORD`: Admin panel password

7. **Initialize the database**
   ```bash
   python app.py
   # This will create tables and a default project
   ```

## Running the Application

### Development Mode

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### Production Mode

```bash
gunicorn --worker-class gevent -w 1 app:app --bind 0.0.0.0:5000
```

## Usage

### User Interface

1. **Navigate to the main page** at `http://localhost:5000`
2. **Click on a pixel** in the canvas to select it
3. **Choose a color** using the color picker
4. **Click "Purchase Pixel"** to buy and modify the pixel
5. **Complete payment** through Stripe (in production)
6. **See real-time updates** from other users

### Admin Panel

1. **Navigate to** `http://localhost:5000/admin?user=admin&pass=your_password`
2. **Create new projects** with custom dimensions
3. **Manage existing projects** (activate/deactivate)
4. **View platform statistics**

## API Endpoints

### Public Endpoints

- `GET /` - Main canvas page
- `GET /api/projects` - List all active projects
- `GET /api/projects/<id>/pixels` - Get pixel history for a project
- `GET /api/projects/<id>/current-state` - Get current canvas state
- `POST /api/create-payment-intent` - Create Stripe payment intent
- `POST /api/confirm-pixel` - Confirm pixel purchase after payment

### Admin Endpoints

- `GET /admin` - Admin panel (requires authentication)
- `POST /api/projects` - Create new project

### WebSocket Events

- `connect` - Client connects to server
- `disconnect` - Client disconnects from server
- `request_canvas_state` - Request current canvas state
- `canvas_state` - Receive canvas state
- `pixel_update` - Broadcast pixel modifications

## Database Schema

### Projects Table
- `id`: Integer (Primary Key)
- `name`: String (200)
- `description`: Text
- `original_image_url`: String (500)
- `width`: Integer (default: 100)
- `height`: Integer (default: 100)
- `is_active`: Boolean (default: True)
- `created_at`: DateTime

### Pixel History Table
- `id`: Integer (Primary Key)
- `project_id`: Integer (Foreign Key)
- `x`: Integer
- `y`: Integer
- `red`: Integer (0-255)
- `green`: Integer (0-255)
- `blue`: Integer (0-255)
- `user_id`: String (100)
- `payment_id`: String (200)
- `timestamp`: DateTime (indexed)

### Users Table
- `id`: String (100, Primary Key)
- `email`: String (200)
- `total_pixels`: Integer (default: 0)
- `created_at`: DateTime

## Configuration

Key configuration options in `.env`:

- `PIXEL_PRICE_CENTS`: Price per pixel in cents (default: 100 = $1.00)
- `CANVAS_WIDTH`: Default canvas width (default: 100)
- `CANVAS_HEIGHT`: Default canvas height (default: 100)

## Payment Integration

The application supports Stripe for payment processing. In the demo mode, payments are simulated. For production:

1. Set up Stripe account and get API keys
2. Configure webhook endpoints for payment confirmations
3. Implement Stripe Elements for secure payment collection
4. Handle payment failures and refunds

## Security Considerations

- Store sensitive keys in environment variables
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Validate all user inputs
- Implement proper authentication for admin panel
- Set up CORS policies appropriately
- Monitor for fraudulent activities

## Future Enhancements

- User authentication and profiles
- Multiple payment providers (Google Pay, Apple Pay)
- Canvas templates and themes
- Pixel ownership and trading
- Undo/redo functionality
- Export canvas as image
- Social sharing features
- Mobile app support

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
