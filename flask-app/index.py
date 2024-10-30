# index.py
from app import create_app

app = create_app()

# Vercel uses this as the entry point
app = app