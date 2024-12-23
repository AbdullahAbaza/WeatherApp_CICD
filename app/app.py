import os
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from flask_caching import Cache
from werkzeug.middleware.proxy_fix import ProxyFix
import sqlite3
import requests
import matplotlib.pyplot as plt
import io
import logging
from logging.handlers import RotatingFileHandler
from functools import wraps
import time

# Initialize Flask app
app = Flask(__name__)

# Production configurations
app.config.update(
    SECRET_KEY=os.getenv('SECRET_KEY', 'your-secret-key-here'),
    CACHE_TYPE='simple',
    CACHE_DEFAULT_TIMEOUT=300,
    JSON_SORT_KEYS=False,
    MAX_CONTENT_LENGTH=10 * 1024 * 1024  # 10MB max-limit
)

# Setup caching
cache = Cache(app)

# Database configuration
DB_FILE = 'weather_data.db'
API_KEY = os.getenv('OPENWEATHER_API_KEY', '603cc5249b17c63fee45270700ae6d3f')

# Setup logging
if not os.path.exists('logs'):
    os.makedirs('logs')

formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler = RotatingFileHandler(
    'logs/app.log', maxBytes=10000000, backupCount=5
)
handler.setFormatter(formatter)
app.logger.addHandler(handler)
app.logger.setLevel(logging.INFO)

# Support for proxy servers
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Performance monitoring decorator
def monitor_performance(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        duration = time.time() - start_time
        app.logger.info(f'{f.__name__} took {duration:.2f} seconds to execute')
        return result
    return decorated_function

# Database connection with context manager
class DatabaseConnection:
    def __init__(self, db_file):
        self.db_file = db_file

    def __enter__(self):
        self.conn = sqlite3.connect(self.db_file)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            self.conn.close()

def get_db():
    return DatabaseConnection(DB_FILE)

# Initialize database
def init_db():
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                temperature REAL,
                humidity INTEGER,
                description TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()

# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': time.time()})

@app.route('/')
@monitor_performance
def home():
    return render_template('index.html')

@app.route('/add_city', methods=['POST'])
@monitor_performance
def add_city():
    city = request.form.get('city', '').strip()
    if not city:
        app.logger.warning('Empty city name submitted')
        return redirect(url_for('home'))

    try:
        weather_data = fetch_weather(city)
        if weather_data:
            save_to_db(city, weather_data)
            app.logger.info(f'Successfully added weather data for {city}')
        else:
            app.logger.error(f'Failed to fetch weather data for {city}')
    except Exception as e:
        app.logger.error(f'Error processing city {city}: {str(e)}')

    return redirect(url_for('home'))

@app.route('/weather')
@cache.cached(timeout=60)  # Cache for 1 minute
@monitor_performance
def weather():
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, temperature, humidity, description, timestamp 
                FROM weather 
                ORDER BY timestamp DESC
                LIMIT 50
            ''')
            data = cursor.fetchall()
        return render_template('weather.html', weather_data=data)
    except Exception as e:
        app.logger.error(f'Error fetching weather data: {str(e)}')
        return render_template('error.html', error='Unable to fetch weather data'), 500

@app.route('/plot')
@cache.cached(timeout=300)  # Cache for 5 minutes
@monitor_performance
def plot():
    try:
        # Use BytesIO instead of saving to disk
        img_io = io.BytesIO()
        
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT city, temperature 
                FROM weather 
                ORDER BY timestamp DESC 
                LIMIT 10
            ''')
            data = cursor.fetchall()

        cities = [row['city'] for row in data]
        temperatures = [row['temperature'] for row in data]

        plt.figure(figsize=(10, 6))
        plt.bar(cities, temperatures, color='skyblue')
        plt.title('Recent City Temperatures')
        plt.xlabel('City')
        plt.ylabel('Temperature (°C)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        plt.savefig(img_io, format='png')
        img_io.seek(0)
        plt.close()  # Close the figure to free memory
        
        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        app.logger.error(f'Error generating plot: {str(e)}')
        return jsonify({'error': 'Unable to generate plot'}), 500

@cache.memoize(timeout=300)
def fetch_weather(city):
    try:
        url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric'
        response = requests.get(url, timeout=5)  # Add timeout
        response.raise_for_status()
        data = response.json()

        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'description': data['weather'][0]['description']
        }
    except requests.RequestException as e:
        app.logger.error(f"Error fetching weather data for {city}: {str(e)}")
        return None

def save_to_db(city, weather_data):
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO weather (city, temperature, humidity, description)
                VALUES (?, ?, ?, ?)
            ''', (city, weather_data['temperature'], weather_data['humidity'], weather_data['description']))
            conn.commit()
    except Exception as e:
        app.logger.error(f"Error saving to database: {str(e)}")
        raise

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error='Page not found'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error='Internal server error'), 500

if __name__ == '__main__':
    init_db()
    port = int(os.getenv('PORT', 5001))
    app.run(host='0.0.0.0', port=port)
