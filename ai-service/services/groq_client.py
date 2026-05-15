# Mock Groq client for testing
class MockGroqClient:
    def __init__(self):
        self.api_key = None

# Create global instance
groq_client = MockGroqClient()
