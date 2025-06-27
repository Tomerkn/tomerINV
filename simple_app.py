#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
אפליקציה פשוטה לבדיקת פריסה בענן
"""

import os
import sys
import logging
from flask import Flask, jsonify

# הגדרת לוגים
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# יצירת האפליקציה
app = Flask(__name__)

@app.route('/')
def index():
    """נתיב ראשי"""
    return jsonify({
        'message': 'האפליקציה עובדת!',
        'status': 'success',
        'port': os.getenv('PORT', '4000')
    })

@app.route('/health')
def health():
    """נתיב בדיקת בריאות"""
    return jsonify({
        'status': 'healthy',
        'port': os.getenv('PORT', '4000'),
        'database_url': 'set' if os.getenv('DATABASE_URL') else 'not_set'
    })

@app.route('/test')
def test():
    """נתיב בדיקה פשוט"""
    return "האפליקציה עובדת!"

if __name__ == '__main__':
    port = int(os.getenv('PORT', 4000))
    logger.info(f"האפליקציה רצה על פורט {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 