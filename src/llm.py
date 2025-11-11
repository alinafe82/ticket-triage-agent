class MockLLM:
    def complete(self, prompt: str) -> str:
        return (
            "Thanks for reaching out. We'll handle this request.\n"
            "Questions: 1) When did this start? 2) Affected users?\n"
            "Next: We'll review logs and confirm access policies."
        )

def get_llm():
    return MockLLM()
