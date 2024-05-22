# Modified from ChatCompletionsApi.py in the original project based on Streamlit
# Modified by rgzz666

from OpenAIApi import OpenAIApi
from OpenAIConfig import OpenAIConfig

class ChatCompletionsApi(OpenAIApi):
    def __init__(self, api_key: str, organization: str = None) -> None:
        super().__init__(api_key, organization)

    def create_chat_completions(self,config:OpenAIConfig,message_placeholder,msglist=None):
        full_response = ""
        for response in self.client.chat.completions.create(
            model=config.model,
            messages=config.messages,
            stream=True
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.set_content(full_response + "▌")
            if msglist!=None:
                msglist.scroll_to(percent=1)
        return full_response
