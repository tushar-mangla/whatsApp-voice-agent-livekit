# LiveKit Voice Agent Server

This server provides a REST API to control the LiveKit Voice Agent remotely on port 8080.

## Quick Start

### Running Locally
```bash
# Install dependencies
pip install -r requirements.txt

# Start the server
python server.py
```

### Running with Docker
```bash
# Build the image
docker build -t livekit-voice-agent .

# Run the container
docker run -p 8080:8080 livekit-voice-agent
```

## API Endpoints

### Start Agent
- **Endpoint**: `/start-agent`
- **Methods**: `GET` or `POST`
- **Description**: Starts the voice agent with `python agent.py dev`

```bash
# Using curl
curl -X POST http://localhost:8080/start-agent

# Or using GET
curl http://localhost:8080/start-agent
```

**Response**:
```json
{
    "status": "success",
    "message": "Agent started successfully",
    "timestamp": "2025-01-27T10:30:00.000000"
}
```

### Stop Agent
- **Endpoint**: `/stop-agent`
- **Method**: `POST`
- **Description**: Stops the running voice agent

```bash
curl -X POST http://localhost:8080/stop-agent
```

### Check Status
- **Endpoint**: `/status`
- **Method**: `GET`
- **Description**: Check if the agent is currently running

```bash
curl http://localhost:8080/status
```

### Health Check
- **Endpoint**: `/health`
- **Method**: `GET`
- **Description**: Server health check

```bash
curl http://localhost:8080/health
```

### Service Info
- **Endpoint**: `/`
- **Method**: `GET`
- **Description**: Get service information and available endpoints

```bash
curl http://localhost:8080/
```

## Usage Examples

### Starting the Agent from External System
```bash
# Start the agent
response=$(curl -s -X POST http://your-server:8080/start-agent)
echo $response

# Check if it started successfully
if echo $response | grep -q "success"; then
    echo "Agent started successfully"
else
    echo "Failed to start agent"
fi
```

### Monitoring Agent Status
```bash
# Check status
curl -s http://localhost:8080/status | jq '.status'
```

### Integration with Other Services
You can integrate this server with:
- CI/CD pipelines
- Monitoring systems
- Other microservices
- Web applications
- Mobile apps

## Environment Variables

Make sure to set up your `.env` file with the required environment variables that `agent.py` needs:
- `N8N_MCP_SERVER_URL`
- Any other environment variables required by your LiveKit setup

## Error Handling

The server provides proper HTTP status codes and error messages:
- `200`: Success
- `400`: Bad request (e.g., agent already running)
- `500`: Internal server error

## Security Considerations

- The server runs on `0.0.0.0:8080` by default
- Consider adding authentication for production use
- Use HTTPS in production environments
- Implement rate limiting if needed
