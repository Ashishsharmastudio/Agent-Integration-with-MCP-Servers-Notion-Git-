# app.py
import os
from flask import Flask
from src.web.routes import create_app

# Entrypoint. We keep app creation in a factory to allow testing.
app: Flask = create_app()

if __name__ == "__main__":
    # Dev server only; use gunicorn in production
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", 5000)))
