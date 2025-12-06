from flask import Flask, jsonify
from flask_cors import CORS
import os
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
CORS(app)

@app.route('/')
def root():
	logger.info("Root endpoint called")
	return jsonify({
		"status": "online",
		"service": "APEX Backend",
		"version": "1.0-minimal"
	})

@app.route('/api/health')
def health():
	logger.info("Health check called")
	return jsonify({
		"status": "healthy",
		"service": "apex-backend",
		"timestamp": "2025-12-06"
	})

@app.route('/api/contacts', methods=['GET'])
def get_contacts():
	return jsonify({
		"contacts": [],
		"total": 0,
		"message": "Backend live - features being restored incrementally"
	})

if __name__ == '__main__':
	port = int(os.getenv('PORT', 8000))
	logger.info(f"🚀 Starting APEX Backend on port {port}")
	app.run(host='0.0.0.0', port=port, debug=False)
