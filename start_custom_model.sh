#!/bin/bash
echo "🚀 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

echo "⏳ Waiting for Ollama to be ready..."
for i in {1..30}; do
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "Ollama is ready"
        break
    fi
    sleep 2
done

# Pull models if they do not exist
echo "Checking models..."
if ! ollama list | grep -q "tinyllama:1.1b"; then
    echo "Pulling tinyllama:1.1b (this will take several minutes)..."
    ollama pull tinyllama:1.1b
    echo "tinyllama:1.1b downloaded!"
else
    echo "tinyllama:1.1b already exists"
fi

if ! ollama list | grep -q "nomic-embed-text"; then
    echo "Pulling nomic-embed-text..."
    ollama pull nomic-embed-text
    echo "nomic-embed-text downloaded!"
else
    echo "nomic-embed-text already exists"
fi

echo "All models ready!"
echo "Available models:"
ollama list


# Keep Ollama running
wait $OLLAMA_PID