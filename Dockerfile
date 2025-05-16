# Use the official Python image for ARM (Raspberry Pi)
FROM python:3.13-rc-slim AS builder

# Install uv
RUN pip install uv

# Create virtual environment and install dependencies
WORKDIR /app
COPY . .
RUN uv venv && . /app/.venv/bin/activate && \
    uv pip sync uv.lock

# Final stage
FROM python:3.13-rc-slim

# Copy virtual environment from builder
COPY --from=builder /app /app

# Set up environment
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH" \
    FLASK_APP=app.py

# Expose port and run application
EXPOSE 5000
CMD ["uv run", "app.py"]