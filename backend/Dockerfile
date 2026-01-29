FROM python:3.10

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Set working directory to user home
WORKDIR /home/user/app

# Copy and install requirements
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Copy project files
COPY --chown=user . .

# Expose the port
EXPOSE 7860

# Run the app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "7860", "--log-level", "debug"]
