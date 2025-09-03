"""
Test configuration.
"""
import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_config_import():
    """Test that config can be imported."""
    from src.core.config import settings
    assert settings.app_name == "Contract Intelligence Assistant"

def test_api_import():
    """Test that FastAPI app can be imported.""" 
    from src.api.main import app
    assert app.title == "Contract Intelligence Assistant"
