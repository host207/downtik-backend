from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import logging

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # السماح بالطلبات من أي مصدر

@app.route('/api/instagram', methods=['POST'])
def download_instagram():
    """
    استقبال رابط Instagram وإرجاع رابط التحميل المباشر
    """
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        logger.info(f"📥 Received request for: {url}")
        
        if not url:
            return jsonify({
                'success': False,
                'error': 'URL is required'
            }), 400
        
        # استخدام yt-dlp لاستخراج رابط الفيديو
        logger.info("🔄 Running yt-dlp...")
        
        result = subprocess.run(
            [
                'yt-dlp',
                '--get-url',
                '--no-playlist',
                '--no-warnings',
                '-f', 'best[ext=mp4]/best',
                url
            ],
            capture_output=True,
            text=True,
            timeout=45
        )
        
        if result.returncode == 0:
            video_url = result.stdout.strip().split('\n')[0]
            if video_url.startswith('http'):
                logger.info(f"✅ Success: {video_url[:50]}...")
                return jsonify({
                    'success': True,
                    'video_url': video_url
                })
        
        # في حالة الفشل
        error_msg = result.stderr.strip() if result.stderr else 'Unknown error'
        logger.error(f"❌ yt-dlp failed: {error_msg}")
        
        return jsonify({
            'success': False,
            'error': 'Failed to extract video URL',
            'details': error_msg
        }), 500
        
    except subprocess.TimeoutExpired:
        logger.error("⏱️ Timeout")
        return jsonify({
            'success': False,
            'error': 'Request timeout (45s)'
        }), 504
        
    except Exception as e:
        logger.error(f"💥 Exception: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health():
    """
    فحص حالة السيرفر
    """
    try:
        # تحقق من وجود yt-dlp
        result = subprocess.run(['yt-dlp', '--version'], capture_output=True)
        yt_dlp_version = result.stdout.decode().strip() if result.returncode == 0 else 'Not installed'
        
        return jsonify({
            'status': 'ok',
            'service': 'DownTik Instagram Backend',
            'yt_dlp_version': yt_dlp_version
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/', methods=['GET'])
def home():
    """
    الصفحة الرئيسية
    """
    return jsonify({
        'service': 'DownTik Instagram Backend',
        'version': '1.0',
        'endpoints': {
            '/api/instagram': 'POST - Extract Instagram video URL',
            '/health': 'GET - Check service health'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    
    logger.info("🚀 Starting DownTik Backend Server...")
    logger.info(f"📡 Server will be available on port: {port}")
    logger.info("🔗 API endpoint: /api/instagram")
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=False
    )
