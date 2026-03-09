"""BaseAgent with invoke(), mock mode, retry logic."""


class BaseAgent:
    def invoke(self, input_data):
        raise NotImplementedError

    def _execute(self, input_data):
        raise NotImplementedError

    def _load_mock_response(self, input_data):
        raise NotImplementedError
