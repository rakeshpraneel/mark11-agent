# /etc/caddy/Caddyfile
# Listen on the port Render exposes (e.g., 10000)
:10000 {
    # Forward all requests to Ollama's internal port
    reverse_proxy 127.0.0.1:11434
    
    # Increase the timeout for the heavy LLM requests
    # Set a 5 minute timeout (300 seconds) for the reverse proxy
    # This prevents the client from timing out during the model load
    duration 300s
}