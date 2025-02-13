#!/usr/bin/env python
# coding=utf-8

# Copyright 2024 The HuggingFace Inc. team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from copy import deepcopy
from enum import Enum
import json
from typing import Dict, List, Optional
import logging


from ..smolagents.tools import Tool
from ..smolagents.models import Model
from ..smolagents.models import get_clean_message_list
from ..smolagents.models import tool_role_conversions
from ..smolagents.models import get_json_schema

logger = logging.getLogger(__name__)

class OpenAIModel(Model):
    def __init__(
        self,
        model_id="gpt-4-turbo-preview",
        base_url=None,
        api_key=None,
    ):
        super().__init__()
        self.model_id = model_id
        import openai
        self.client = openai.OpenAI(
            base_url=base_url,
            api_key=api_key
        )

    def __call__(
        self,
        messages: List[Dict[str, str]],
        stop_sequences: Optional[List[str]] = None,
        grammar: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> str:
        messages = get_clean_message_list(
            messages, role_conversions=tool_role_conversions
        )

        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            stop=stop_sequences,
            max_tokens=max_tokens,
        )
        self.last_input_token_count = response.usage.prompt_tokens
        self.last_output_token_count = response.usage.completion_tokens
        return response.choices[0].message.content

    def get_tool_call(
        self,
        messages: List[Dict[str, str]],
        available_tools: List[Tool],
        stop_sequences: Optional[List[str]] = None,
        max_tokens: int = 1500,
    ):
        messages = get_clean_message_list(
            messages, role_conversions=tool_role_conversions
        )
        response = self.client.chat.completions.create(
            model=self.model_id,
            messages=messages,
            tools=[get_json_schema(tool) for tool in available_tools],
            tool_choice="auto",
            stop=stop_sequences,
            max_tokens=max_tokens,
        )
        tool_calls = response.choices[0].message.tool_calls[0]
        self.last_input_token_count = response.usage.prompt_tokens
        self.last_output_token_count = response.usage.completion_tokens
        arguments = json.loads(tool_calls.function.arguments)
        return tool_calls.function.name, arguments, tool_calls.id
