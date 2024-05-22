# Modified from the original project

class OpenAIConfig:
    # gpt-3.5-turbo
    def __init__(self,messages:list,model='gpt-3.5-turbo',stream=True):
        self.model = model
        self.messages = messages
        self.stream = stream
