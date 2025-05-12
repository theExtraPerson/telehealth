import uuid
from datetime import datetime, timedelta

def generate_telemedicine_link():
    return f"session_{uuid.uuid4().hex[:8]}"

def validate_telemedicine_link(link: str):
    # In a real implementation, you would check against a database
    # and verify expiration time
    return True