from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import json
import logging
import os
import requests

# إعداد Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

def try_rapidapi(url):
    """محاولة استخدام RapidAPI"""
    try:
        api_url = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"
        headers = {
            "x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
        }
        response = requests.get(api_url, headers=headers, params={"url": url}, timeout=20)
        if response.status_code == 200:
            data = response.json()
            if data.get('download_url'):
                return data['download_url']
    except:
        pass
    return None

def try_snapinsta(url):
    """محاولة استخدام SnapInsta API"""
    try:
        api_url = "https://snapinsta.app/api/ajaxSearch"
        response = requests.post(
            api_url,
            data={"q": url, "t": "media", "lang": "en"},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=20
        )
        if response.status_code == 200:
            import re
            html = response.text
            match = re.search(r'href="(https://[^"]+\.mp4[^"]*)"', html)
            if match:
                return match.group(1).replace('&amp;', '&')
    except:
        pass
    return None

@app.route('/api/instagram', methods=['POST'])
def download_instagram():
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        
        logger.info(f"📥 Received: {url}")
        
        if not url:
            return jsonify({'success': False, 'error': 'URL required'}), 400
        
        # Method 1: SnapInsta
        logger.info("🔄 Trying SnapInsta...")
        video_url = try_snapinsta(url)
        if video_url:
            logger.info("✅ SnapInsta success")
            return jsonify({'success': True, 'video_url': video_url})
        
        # Method 2: yt-dlp (fallback)
        logger.info("🔄 Trying yt-dlp...")
        result = subprocess.run(
            ['yt-dlp', '--get-url', '--no-warnings', '-f', 'best', url],
            capture_output=True, text=True, timeout=30
        )
        
        if result.returncode == 0:
            video_url = result.stdout.strip().split('\n')[0]
            if video_url.startswith('http'):
                logger.info("✅ yt-dlp success")
                return jsonify({'success': True, 'video_url': video_url})
        
        logger.error("❌ All methods failed")
        return jsonify({
            'success': False,
            'error': 'Could not download video',
            'details': result.stderr if result.stderr else 'Unknown error'
        }), 500
        
    except Exception as e:
        logger.error(f"💥 Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'ok',
        'service': 'DownTik Instagram Backend',
        'version': '2.0'
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'service': 'DownTik Instagram Backend',
        'version': '2.0',
        'endpoints': {
            '/api/instagram': 'POST - Extract Instagram video',
            '/health': 'GET - Health check'
        }
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info("🚀 Starting DownTik Backend v2.0...")
    logger.info(f"📡 Port: {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
