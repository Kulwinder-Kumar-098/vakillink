import random
import string

def generate_bar_council_id(state_code: str = None) -> str:
    """
    Generates a realistic-looking Indian Bar Council ID.
    Format: {STATE}/{NUMBER}/{YEAR}
    Example: DEL/4512/2018
    """
    states = ["DEL", "MAH", "UP", "KA", "TN", "WB", "PB", "HR", "GUJ", "RAJ"]
    state = state_code or random.choice(states)
    number = random.randint(1000, 9999)
    year = random.randint(1990, 2023)
    
    return f"{state}/{number}/{year}"
