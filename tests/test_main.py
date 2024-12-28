import pytest
from app.main import greet

def test_greet():
    assert greet("World") == "Hello, World!"
