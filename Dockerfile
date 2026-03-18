FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including git (required for uv git dependencies)
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates git

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

# Copy dependency files first — layer cache means deps only reinstall when these change
COPY pyproject.toml uv.lock README.md ./
COPY sympy_mcp/ ./sympy_mcp/

# Pre-install all dependencies at build time (no installs at container startup)
RUN uv sync --frozen --no-dev

# Expose the default MCP port
EXPOSE 8081

# Add healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8081/health || exit 1

# Run the server in rest mode (REST API + MCP over HTTP)
CMD ["uv", "run", "sympy-mcp", "--mode", "rest", "--host", "0.0.0.0", "--port", "8081", "--no-auth"]
