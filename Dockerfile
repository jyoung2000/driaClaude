FROM python:3.11-slim

# Install system dependencies including gosu for user switching
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    curl \
    git \
    ffmpeg \
    libsndfile1 \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/data /app/voices /app/outputs /app/static

# Create enhanced entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Default to UID/GID 1000 if not provided\n\
USER_ID=${PUID:-1000}\n\
GROUP_ID=${PGID:-1000}\n\
\n\
echo "Starting with UID:GID = $USER_ID:$GROUP_ID"\n\
\n\
# Create user if it doesnt exist\n\
if ! id -u appuser >/dev/null 2>&1; then\n\
    groupadd -g $GROUP_ID appgroup || true\n\
    useradd -m -u $USER_ID -g appgroup appuser\n\
else\n\
    # Modify existing user to match desired UID/GID\n\
    groupmod -g $GROUP_ID appgroup || true\n\
    usermod -u $USER_ID -g $GROUP_ID appuser || true\n\
fi\n\
\n\
# Fix ownership of app directory\n\
chown -R appuser:appgroup /app\n\
\n\
# Create required directories with correct permissions\n\
mkdir -p /app/data/hf_cache /app/voices /app/outputs\n\
\n\
# Fix permissions for mounted volumes if they exist\n\
for dir in /app/data /app/voices /app/outputs; do\n\
    if [ -d "$dir" ]; then\n\
        chown -R appuser:appgroup "$dir" || echo "Warning: Could not change ownership of $dir"\n\
        chmod -R 755 "$dir" || echo "Warning: Could not change permissions of $dir"\n\
    fi\n\
done\n\
\n\
# Create voices.json if it doesnt exist\n\
if [ ! -f /app/voices/voices.json ]; then\n\
    echo "{}" > /app/voices/voices.json\n\
    chown appuser:appgroup /app/voices/voices.json\n\
fi\n\
\n\
echo "Permissions fixed, switching to user appuser..."\n\
\n\
# Switch to appuser and run the command\n\
exec gosu appuser "$@"' > /app/entrypoint.sh && \
    chmod +x /app/entrypoint.sh

# Stay as root for entrypoint to work
# USER will be switched by gosu in entrypoint

# Expose port
EXPOSE 4144

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV HF_HOME=/app/data/hf_cache
ENV TRANSFORMERS_CACHE=/app/data/hf_cache

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD curl -f http://localhost:4144/health || exit 1

# Use entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the application
CMD ["python", "main.py"]