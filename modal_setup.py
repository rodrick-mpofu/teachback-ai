"""
Modal Setup - Base configuration for TeachBack AI Modal deployment.

This module defines the Modal app, base image, and secrets used across
all Modal functions in the TeachBack AI project.
"""

import modal

# Define Modal app
app = modal.App("teachback-ai")

# Define secrets
anthropic_secret = modal.Secret.from_name("anthropic-api-key")
elevenlabs_secret = modal.Secret.from_name("elevenlabs-api-key")

# Define base image with required dependencies
image = (
    modal.Image.debian_slim()
    .pip_install("anthropic>=0.39.0", "python-dotenv")
)

# Import all function modules to register them with the app
# This is needed for deployment
try:
    from src.modal_functions import parallel_teaching, background_analytics
except ImportError:
    # Functions may not be available during initial setup
    pass

# Export all components
__all__ = ["app", "image", "anthropic_secret", "elevenlabs_secret"]
