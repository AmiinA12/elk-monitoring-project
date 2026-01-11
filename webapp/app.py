import os
import time
import logging
from datetime import datetime, timedelta
from flask import Flask, jsonify, request, render_template, flash, redirect, url_for, session
from functools import wraps
from werkzeug.utils import secure_filename
from pymongo import MongoClient
import redis
from elasticsearch import Elasticsearch
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key')

# Configure upload folder
UPLOAD_FOLDER = 'data/uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_UPLOAD_SIZE', 104857600))  # 100MB

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Connection factories with retry logic
def get_mongo_connection():
    try:
        host = os.getenv('MONGO_HOST', 'localhost')
        port = int(os.getenv('MONGO_PORT', 27017))
        username = os.getenv('MONGO_USERNAME', 'admin')
        password = os.getenv('MONGO_PASSWORD', 'admin123')
        
        client = MongoClient(
            host=host,
            port=port,
            username=username,
            password=password,
            serverSelectionTimeoutMS=5000
        )
        client.server_info() # Trigger connection
        return client
    except Exception as e:
        logger.error(f"MongoDB connection failed: {e}")
        return None

def get_redis_connection():
    try:
        host = os.getenv('REDIS_HOST', 'localhost')
        port = int(os.getenv('REDIS_PORT', 6379))
        password = os.getenv('REDIS_PASSWORD', None)
        
        r = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        r.ping()
        return r
    except Exception as e:
        logger.error(f"Redis connection failed: {e}")
        return None

def get_elastic_connection():
    try:
        host = os.getenv('ELASTICSEARCH_HOST', 'localhost')
        port = int(os.getenv('ELASTICSEARCH_PORT', 9200))
        
        es = Elasticsearch([{'host': host, 'port': port}])
        if not es.ping():
            raise Exception("Elasticsearch ping failed")
        return es
    except Exception as e:
        logger.error(f"Elasticsearch connection failed: {e}")
        return None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ============================================================================
# AUTHENTICATION DECORATOR & LOGIC
# ============================================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Simple authentication (in a real app, use a DB and hash passwords)
        # Using env variables or defaults
        admin_user = os.getenv('ADMIN_USERNAME', 'admin')
        admin_pass = os.getenv('ADMIN_PASSWORD', 'admin123')
        
        if username == admin_user and password == admin_pass:
            session['user_id'] = username
            flash('Bienvenue, administrateur !', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Identifiants invalides.', 'danger')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('login'))

# ============================================================================
# FRONTEND ROUTES
# ============================================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/upload')
@login_required
def upload_page():
    return render_template('upload.html')

@app.route('/search')
@login_required
def search_page():
    return render_template('search.html')

@app.route('/kibana')
@login_required
def kibana_page():
    return render_template('kibana.html')

# ============================================================================
# API ROUTES
# ============================================================================

@app.route('/health')
def health_check():
    status = {
        "mongodb": "down",
        "redis": "down",
        "elasticsearch": "down"
    }
    
    # Check MongoDB
    mongo = get_mongo_connection()
    if mongo:
        status["mongodb"] = "up"
        mongo.close()
        
    # Check Redis
    r = get_redis_connection()
    if r:
        status["redis"] = "up"
    
    # Check Elasticsearch
    es = get_elastic_connection()
    if es:
        status["elasticsearch"] = "up"
        
    return jsonify(status)

@app.route('/api/v1/dashboard/stats')
@login_required
def dashboard_stats():
    """Get dashboard statistics"""
    es = get_elastic_connection()
    
    if not es:
        return jsonify({
            "kpis": {"total": 0, "info": 0, "warning": 0, "error": 0},
            "logs_timeline": [],
            "services_distribution": [],
            "recent_logs": []
        })
    
    try:
        # Get total count and level aggregation
        agg_query = {
            "size": 0,
            "aggs": {
                "by_level": {
                    "terms": {"field": "level.keyword"}
                },
                "by_service": {
                    "terms": {"field": "service.keyword"}
                }
            }
        }
        
        result = es.search(index="logs_csv-*", body=agg_query)
        
        # Extract KPIs
        total = result['hits']['total']['value']
        levels = {b['key']: b['doc_count'] for b in result['aggregations']['by_level']['buckets']}
        services = [{"service": b['key'], "count": b['doc_count']} 
                   for b in result['aggregations']['by_service']['buckets']]
        
        # Get recent logs
        recent_query = {
            "size": 10,
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        recent_result = es.search(index="logs_csv-*", body=recent_query)
        recent_logs = [hit['_source'] for hit in recent_result['hits']['hits']]
        
        # Simplified timeline (mock data for now)
        timeline = [
            {"hour": f"{i}h", "info": levels.get('INFO', 0) // 24, 
             "warning": levels.get('WARNING', 0) // 24, 
             "error": levels.get('ERROR', 0) // 24}
            for i in range(24)
        ]
        
        return jsonify({
            "kpis": {
                "total": total,
                "info": levels.get('INFO', 0),
                "warning": levels.get('WARNING', 0),
                "error": levels.get('ERROR', 0)
            },
            "logs_timeline": timeline,
            "services_distribution": services,
            "recent_logs": recent_logs
        })
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/search')
@login_required
def search_logs():
    """Search logs with filters"""
    es = get_elastic_connection()
    
    if not es:
        return jsonify({"results": [], "total": 0}), 200
    
    try:
        query_text = request.args.get('q', '')
        level = request.args.get('level', '')
        service = request.args.get('service', '')
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 50))
        
        # Build query
        must_clauses = []
        
        if query_text:
            must_clauses.append({
                "multi_match": {
                    "query": query_text,
                    "fields": ["message", "action"]
                }
            })
        
        if level:
            must_clauses.append({"term": {"level.keyword": level}})
        
        if service:
            must_clauses.append({"term": {"service.keyword": service}})
        
        query = {
            "from": (page - 1) * size,
            "size": size,
            "query": {
                "bool": {
                    "must": must_clauses if must_clauses else [{"match_all": {}}]
                }
            },
            "sort": [{"@timestamp": {"order": "desc"}}]
        }
        
        result = es.search(index="logs_csv-*", body=query)
        

        
        # Save search history if there are parameters
        if query_text or level or service:
            mongo = get_mongo_connection()
            if mongo:
                try:
                    db = mongo[os.getenv('MONGO_DATABASE', 'elk_metadata')]
                    db.search_history.insert_one({
                        "query": query_text,
                        "level": level,
                        "service": service,
                        "date": datetime.now(),
                        "results_count": result['hits']['total']['value']
                    })
                    mongo.close()
                except Exception as e:
                    logger.error(f"Error saving search history: {e}")
                    # Continue without failing the request
        
        return jsonify({
            "results": [hit['_source'] for hit in result['hits']['hits']],
            "total": result['hits']['total']['value']
        })
        
    except Exception as e:
        logger.error(f"Error searching logs: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/search/history')
@login_required
def get_search_history():
    """Get recent search history"""
    mongo = get_mongo_connection()
    if not mongo:
        return jsonify([])
    
    try:
        db = mongo[os.getenv('MONGO_DATABASE', 'elk_metadata')]
        history = list(db.search_history.find().sort("date", -1).limit(10))
        
        for item in history:
            item['_id'] = str(item['_id'])
            item['date'] = item['date'].isoformat()
            
        mongo.close()
        return jsonify(history)
    except Exception as e:
        logger.error(f"Error fetching search history: {e}")
        return jsonify([])



@app.route('/api/v1/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400
    
    try:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Store metadata in MongoDB
        mongo = get_mongo_connection()
        if mongo:
            db = mongo[os.getenv('MONGO_DATABASE', 'elk_metadata')]
            db.uploads.insert_one({
                "filename": filename,
                "date": datetime.now(),
                "size": os.path.getsize(filepath),
                "status": "uploaded"
            })
            mongo.close()
        
        return jsonify({
            "message": "File uploaded successfully",
            "filename": filename
        })
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/uploads/<filename>', methods=['DELETE'])
@login_required
def delete_file(filename):
    """Delete an uploaded file"""
    try:
        # Secure filename to prevent directory traversal
        filename = secure_filename(filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # 1. Remove from MongoDB
        mongo = get_mongo_connection()
        if mongo:
            db = mongo[os.getenv('MONGO_DATABASE', 'elk_metadata')]
            result = db.uploads.delete_one({"filename": filename})
            mongo.close()
            
            if result.deleted_count == 0:
                logger.warning(f"File {filename} not found in database")
        
        # 2. Remove file from disk
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Deleted file: {filepath}")
            return jsonify({"message": "File deleted successfully"})
        else:
            logger.warning(f"File not found on disk: {filepath}")
            # If it was in DB but not disk, we still consider it "gone" from the user's perspective
            if mongo and result.deleted_count > 0:
                 return jsonify({"message": "File record deleted (file was missing from disk)"})
            return jsonify({"error": "File not found"}), 404
            
    except Exception as e:
        logger.error(f"Error deleting file {filename}: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/uploads/recent')
@login_required
def recent_uploads():
    """Get recent uploads"""
    mongo = get_mongo_connection()
    
    if not mongo:
        return jsonify([])
    
    try:
        db = mongo[os.getenv('MONGO_DATABASE', 'elk_metadata')]
        uploads = list(db.uploads.find().sort("date", -1).limit(10))
        
        # Convert ObjectId to string
        for upload in uploads:
            upload['_id'] = str(upload['_id'])
            upload['date'] = upload['date'].isoformat()
        
        mongo.close()
        return jsonify(uploads)
        
    except Exception as e:
        logger.error(f"Error fetching recent uploads: {e}")
        return jsonify([])

@app.route('/api/v1/stats')
@login_required
def stats():
    """General stats endpoint"""
    es = get_elastic_connection()
    
    if not es:
        return jsonify({"total_logs": 0, "indices": []})
    
    try:
        # Get all indices
        indices = es.indices.get_alias(index="logs-*")
        
        # Get total count
        count_result = es.count(index="logs-*")
        
        return jsonify({
            "total_logs": count_result['count'],
            "indices": list(indices.keys())
        })
        
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure upload folder exists
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    
    app.run(host='0.0.0.0', port=8000, debug=True)

