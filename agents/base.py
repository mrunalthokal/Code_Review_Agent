class BaseAgent:
    """Every agent receives a Submission and returns a list[Finding]."""
    name = "base"

    def __init__(self, use_llm: bool = False):
        self.use_llm = use_llm
        self.notes = []   # status messages shown in the UI

    def analyze(self, sub):
        raise NotImplementedError
