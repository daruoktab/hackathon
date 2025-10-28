"""
Flask API to serve temporary interactive Marimo dashboards for invoice analysis.

This server creates temporary, shareable links to interactive Marimo notebooks
that users can use to explore their invoice data.
"""

from flask import Flask, jsonify, request, redirect
import subprocess
import secrets
import os
import tempfile
import shutil
from datetime import datetime, timedelta
from pathlib import Path
import threading
import time
import signal
import sys

app = Flask(__name__)

# Store active sessions: session_id -> {process, port, created_at, user_id, db_path}
active_sessions = {}

# Configuration
BASE_PORT = 8200
MAX_SESSIONS = 10
SESSION_TIMEOUT_MINUTES = 30
MARIMO_APP_PATH = Path(__file__).parent / "marimo_app" / "dashboard.py"


class SessionManager:
    """Manage temporary Marimo dashboard sessions."""
    
    def __init__(self):
        self.lock = threading.Lock()
        self.next_port = BASE_PORT
    
    def allocate_port(self):
        """Allocate a unique port for a new session."""
        with self.lock:
            port = self.next_port
            self.next_port += 1
            return port
    
    def create_session(self, user_id=None):
        """Create a new Marimo dashboard session."""
        # First, check limits and allocate resources with lock
        with self.lock:
            print(f"Checking session limits... (active: {len(active_sessions)}/{MAX_SESSIONS})")
            # Check session limit
            if len(active_sessions) >= MAX_SESSIONS:
                self.cleanup_old_sessions()
                
                if len(active_sessions) >= MAX_SESSIONS:
                    return None, "Maximum number of active sessions reached"
            
            # Generate unique session ID
            session_id = secrets.token_urlsafe(16)
            # Allocate port directly (we already have the lock)
            port = self.next_port
            self.next_port += 1
            print(f"Allocated session {session_id} on port {port}")
        
        # Now do the heavy work outside the lock
        print(f"Creating temp directory...")
        # Create temporary directory for this session
        temp_dir = tempfile.mkdtemp(prefix=f"marimo_session_{session_id}_")
        
        print(f"Copying database...")
        # Copy the database for this session (isolated view)
        original_db = Path(__file__).parent / "database" / "invoices.db"
        session_db = Path(temp_dir) / "invoices.db"
        
        if original_db.exists():
            shutil.copy2(original_db, session_db)
            print(f"Database copied to {session_db}")
        else:
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, "No invoice database found"
        
        # Start Marimo server
        try:
            # Marimo will run from temp directory so it can find invoices.db
            marimo_cmd = [
                sys.executable, "-m", "marimo", "run",
                str(MARIMO_APP_PATH),
                "--host", "127.0.0.1",
                "--port", str(port),
                "--headless"  # No browser launch
            ]
            
            # Set environment variable for the session DB path
            env = os.environ.copy()
            
            print(f"Starting Marimo process on port {port}...")
            process = subprocess.Popen(
                marimo_cmd,
                cwd=temp_dir,  # Run from temp dir so dashboard.py finds invoices.db
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            
            # Wait for the server to start (Marimo takes a while)
            print("Waiting for Marimo to initialize...")
            max_wait = 10  # Maximum 10 seconds
            waited = 0
            while waited < max_wait:
                time.sleep(1)
                waited += 1
                
                # Check if process died
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                    print(f"Marimo process died: {error_msg}")
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return None, f"Marimo server failed to start: {error_msg[:200]}"
                
                # Try to connect to check if server is up
                try:
                    import urllib.request
                    urllib.request.urlopen(f"http://127.0.0.1:{port}", timeout=1)
                    print(f"Marimo server ready on port {port} after {waited}s")
                    break
                except:
                    continue
            
            # Final check if process is still running
            if process.poll() is not None:
                shutil.rmtree(temp_dir, ignore_errors=True)
                return None, "Failed to start Marimo server"
            
            # Store session info (with lock)
            with self.lock:
                active_sessions[session_id] = {
                    'process': process,
                    'port': port,
                    'created_at': datetime.now(),
                    'user_id': user_id,
                    'db_path': session_db,
                    'temp_dir': temp_dir
                }
                print(f"Session {session_id} registered successfully")
            
            return session_id, None
            
        except Exception as e:
            print(f"Exception during session creation: {e}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return None, f"Error starting Marimo: {str(e)}"
    
    def get_session_url(self, session_id):
        """Get the URL for a session."""
        if session_id not in active_sessions:
            return None
        
        port = active_sessions[session_id]['port']
        return f"http://127.0.0.1:{port}"
    
    def cleanup_old_sessions(self):
        """Clean up sessions older than SESSION_TIMEOUT_MINUTES."""
        now = datetime.now()
        to_remove = []
        
        for session_id, info in active_sessions.items():
            age = now - info['created_at']
            if age > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
                to_remove.append(session_id)
        
        for session_id in to_remove:
            self.terminate_session(session_id)
    
    def terminate_session(self, session_id):
        """Terminate a specific session."""
        if session_id not in active_sessions:
            return False
        
        info = active_sessions[session_id]
        
        # Kill the process
        try:
            info['process'].terminate()
            info['process'].wait(timeout=5)
        except:
            try:
                info['process'].kill()
            except:
                pass
        
        # Clean up temp directory
        try:
            shutil.rmtree(info['temp_dir'], ignore_errors=True)
        except:
            pass
        
        del active_sessions[session_id]
        return True
    
    def terminate_all_sessions(self):
        """Terminate all active sessions."""
        session_ids = list(active_sessions.keys())
        for session_id in session_ids:
            self.terminate_session(session_id)


# Create session manager
session_manager = SessionManager()


# Background cleanup thread
def cleanup_thread():
    """Background thread to periodically clean up old sessions."""
    while True:
        time.sleep(60)  # Check every minute
        try:
            session_manager.cleanup_old_sessions()
        except Exception as e:
            print(f"Error in cleanup thread: {e}")


# Start cleanup thread
cleanup_worker = threading.Thread(target=cleanup_thread, daemon=True)
cleanup_worker.start()


# API Endpoints

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'ok',
        'active_sessions': len(active_sessions),
        'max_sessions': MAX_SESSIONS
    })


@app.route('/api/dashboard/create', methods=['POST'])
def create_dashboard():
    """
    Create a new interactive dashboard session.
    
    Request body (optional):
        {
            "user_id": "telegram_user_id"
        }
    
    Response:
        {
            "session_id": "unique_session_id",
            "url": "http://127.0.0.1:port",
            "expires_at": "ISO timestamp"
        }
    """
    print("=== CREATE DASHBOARD REQUEST RECEIVED ===")
    data = request.get_json() or {}
    user_id = data.get('user_id')
    print(f"User ID: {user_id}")
    
    print("Creating session...")
    session_id, error = session_manager.create_session(user_id=user_id)
    print(f"Session creation result - ID: {session_id}, Error: {error}")
    
    if error:
        print(f"Returning error: {error}")
        return jsonify({'error': error}), 500
    
    url = session_manager.get_session_url(session_id)
    expires_at = datetime.now() + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    
    print(f"Returning success - URL: {url}")
    return jsonify({
        'session_id': session_id,
        'url': url,
        'expires_at': expires_at.isoformat(),
        'timeout_minutes': SESSION_TIMEOUT_MINUTES
    }), 201


@app.route('/api/dashboard/<session_id>', methods=['GET'])
def get_dashboard(session_id):
    """
    Get information about a dashboard session.
    
    Response:
        {
            "session_id": "session_id",
            "url": "http://127.0.0.1:port",
            "created_at": "ISO timestamp",
            "expires_at": "ISO timestamp"
        }
    """
    if session_id not in active_sessions:
        return jsonify({'error': 'Session not found or expired'}), 404
    
    info = active_sessions[session_id]
    url = session_manager.get_session_url(session_id)
    expires_at = info['created_at'] + timedelta(minutes=SESSION_TIMEOUT_MINUTES)
    
    return jsonify({
        'session_id': session_id,
        'url': url,
        'created_at': info['created_at'].isoformat(),
        'expires_at': expires_at.isoformat()
    })


@app.route('/api/dashboard/<session_id>/terminate', methods=['DELETE'])
def terminate_dashboard(session_id):
    """Terminate a dashboard session."""
    if session_manager.terminate_session(session_id):
        return jsonify({'message': 'Session terminated successfully'})
    else:
        return jsonify({'error': 'Session not found'}), 404


@app.route('/api/dashboard/list', methods=['GET'])
def list_dashboards():
    """List all active dashboard sessions."""
    sessions = []
    for session_id, info in active_sessions.items():
        sessions.append({
            'session_id': session_id,
            'url': session_manager.get_session_url(session_id),
            'created_at': info['created_at'].isoformat(),
            'user_id': info.get('user_id')
        })
    
    return jsonify({
        'active_sessions': len(sessions),
        'max_sessions': MAX_SESSIONS,
        'sessions': sessions
    })


@app.route('/d/<session_id>', methods=['GET'])
def redirect_to_dashboard(session_id):
    """Redirect to the Marimo dashboard (user-friendly URL)."""
    url = session_manager.get_session_url(session_id)
    if url:
        return redirect(url)
    else:
        return "Dashboard session not found or expired", 404


# Cleanup on shutdown
def signal_handler(sig, frame):
    """Handle shutdown signals."""
    print("\nShutting down Marimo server...")
    session_manager.terminate_all_sessions()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


if __name__ == '__main__':
    print(f"Starting Marimo Dashboard Server...")
    print(f"Max sessions: {MAX_SESSIONS}")
    print(f"Session timeout: {SESSION_TIMEOUT_MINUTES} minutes")
    print(f"Base port: {BASE_PORT}")
    
    # Run Flask app
    app.run(host='127.0.0.1', port=5001, debug=False, threaded=True)
