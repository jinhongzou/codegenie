from pathlib import Path
from typing import Optional
import os

from tavily import TavilyClient
# Correct the import path or provide an alternative if 'tool' is not in 'smolagents'
from ..smolagents import tool, LiteLLMModel,Tool,ToolCallingAgent

##os.environ['TAVILY_KEY']  = "tvly-XXX"
##os.environ['API_KEY'] = 'sk-XXX'
##os.environ['BASE_URL'] = 'https://api.siliconflow.cn/v1/'
##os.environ['MODEL_ID'] = 'openai/Qwen/Qwen2.5-7B-Instruct'

@tool
def general_search(query: str) -> str:
    """
    General search tool for various purposes.
             
    Example usage: ``` general_search(query=your_query) ```

    Args:
        query: The search query.

    Returns:
        Search results as a string.
    """
    # Initialize Tavily client
    tavily_client = TavilyClient(api_key=os.environ.get('TAVILY_KEY'))

    # Perform search
    if query:
        response = tavily_client.qna_search(query)
    else:
        response = "No results found"

    return response

class SearchAgent(Tool):
    name = "SearchAgent"
    description = "Performs a search query and returns the results. "
    inputs = {
        "query": {
            "type": "string",
            "description": "The search query string.",
        }
    }
    output_type = "string"

    def __init__(self, model_id, api_key, base_url, tavily_api_key, **kwargs):
        super().__init__(**kwargs)
        model = LiteLLMModel(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
        )

        @tool
        def general_search(query: str) -> str:
            """
            General search tool for various purposes.
             
            Example usage: ``` general_search(query=your_query) ```

            Args:
                query: The search query.

            Returns:
                Search results as a string.
            """
            # Initialize Tavily client
            tavily_client = TavilyClient(api_key=tavily_api_key)

            # Perform search
            if query:
                response = tavily_client.qna_search(query)
            else:
                response = "No results found"

            return response

        self.search_agent = ToolCallingAgent(
            tools=[general_search],
            model=model,
            max_steps=5,
            name="search_agent",
            description="Runs searches for you. Example usage: search_agent(task=your_query)",
        )

    def forward(self, query: str) -> str:
        result = self.search_agent(task=query)
        return result

if __name__ == "__main__":

    search_agent=SearchAgent(model_id = os.environ.get('MODEL_ID'), 
                            api_key  = os.environ.get('API_KEY'),
                            base_url = os.environ.get('BASE_URL'),
                            tavily_api_key=os.environ.get('TAVILY_KEY'),
                            )

    search_agent("海南农商银行成立日期什么时候？")
