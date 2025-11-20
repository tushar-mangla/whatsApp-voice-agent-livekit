from flask import Flask, jsonify
import subprocess
import threading
import os
import signal
import sys
from datetime import datetime

app = Flask(__name__)

# Global variable to track the agent process
agent_process = None

def run_agent():
    """Run the run_agent.sh script"""
    global agent_process
    try:
        # Make sure the script is executable
        script_path = os.path.join(os.getcwd(), "run_agent.sh")
        os.chmod(script_path, 0o755)
        
        # Run the shell script
        agent_process = subprocess.Popen(
            ["./run_agent.sh"],
            cwd=os.getcwd(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True
        )
        
        # Wait for the process to complete
        stdout, stderr = agent_process.communicate()
        
        if agent_process.returncode == 0:
            print(f"Agent completed successfully at {datetime.now()}")
            print(f"Output: {stdout}")
        else:
            print(f"Agent failed with return code {agent_process.returncode}")
            print(f"Error: {stderr}")
            
    except Exception as e:
        print(f"Error running agent: {str(e)}")
    finally:
        agent_process = None

@app.route('/start-agent', methods=['POST', 'GET'])
def start_agent():
    """Endpoint to start the agent"""
    global agent_process
    
    try:
        # Check if agent is already running
        if agent_process and agent_process.poll() is None:
            return jsonify({
                'status': 'error',
                'message': 'Agent is already running',
                'timestamp': datetime.now().isoformat()
            }), 400
        
        # Start the agent in a separate thread
        agent_thread = threading.Thread(target=run_agent, daemon=True)
        agent_thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Agent started successfully',
            'timestamp': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to start agent: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/stop-agent', methods=['POST'])
def stop_agent():
    """Endpoint to stop the agent"""
    global agent_process
    
    try:
        if agent_process and agent_process.poll() is None:
            # Terminate the agent process
            agent_process.terminate()
            agent_process.wait(timeout=10)  # Wait up to 10 seconds for graceful shutdown
            
            return jsonify({
                'status': 'success',
                'message': 'Agent stopped successfully',
                'timestamp': datetime.now().isoformat()
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'No agent process is currently running',
                'timestamp': datetime.now().isoformat()
            }), 400
            
    except subprocess.TimeoutExpired:
        # Force kill if graceful shutdown fails
        agent_process.kill()
        return jsonify({
            'status': 'success',
            'message': 'Agent force stopped',
            'timestamp': datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Failed to stop agent: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Endpoint to check agent status"""
    global agent_process
    
    if agent_process and agent_process.poll() is None:
        status = 'running'
        message = 'Agent is currently running'
    else:
        status = 'stopped'
        message = 'Agent is not running'
    
    return jsonify({
        'status': status,
        'message': message,
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'LiveKit Voice Agent Server',
        'timestamp': datetime.now().isoformat()
    }), 200

@app.route('/', methods=['GET'])
def root():
    """Root endpoint with basic information"""
    return jsonify({
        'service': 'LiveKit Voice Agent Server',
        'version': '1.0.0',
        'endpoints': {
            'start_agent': '/start-agent (POST/GET)',
            'stop_agent': '/stop-agent (POST)',
            'status': '/status (GET)',
            'health': '/health (GET)'
        },
        'timestamp': datetime.now().isoformat()
    }), 200

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    global agent_process
    print('\nShutting down server...')
    
    if agent_process and agent_process.poll() is None:
        print('Stopping agent process...')
        agent_process.terminate()
        try:
            agent_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            agent_process.kill()
    
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)
