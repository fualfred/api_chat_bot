#!/usr/bin/python
# -*- coding: utf-8 -*-
from typing import TypedDict, List, Annotated
from langchain_core.messages import BaseMessage, AIMessage
from common.tf_idf_retriever import load_local
from config.settings import settings
from common.utils import query_api_info_by_api_number
import json
from common.utils import request_api


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], "对话历史"]
    context: dict


def where_to_go(state: AgentState):
    if state['messages'][-1].content == 'q':
        return 'reset_node'
    elif 'next_node' not in state['context']:
        return 'retriever_node'
    elif state['messages'][-1].content == "":
        return 'reset_node'
    else:
        return state['context']['next_node']


def reset_node(state: AgentState):
    state['context'] = {}
    state["messages"] = [AIMessage(content="流程已重置")]
    return state


def retriever_node(state: AgentState):
    user_input = state['messages'][-1].content
    retriever = load_local(settings.API_TF_IDF_PATH)
    docs = retriever.invoke(user_input)
    commands = []
    for doc in docs:
        commands.append(doc.page_content)
    state['context']['commands'] = commands
    state['context']['next_node'] = 'command_node'
    state['messages'] = [AIMessage(content=commands)]
    return state


def command_node(state: AgentState):
    user_input = state['messages'][-1].content
    try:
        command_seq = int(user_input)
        print(f"command_seq:{command_seq}")
        api_number_name = state['context']['commands'][command_seq - 1]
        api_number = api_number_name.split('_')[0]
        result = query_api_info_by_api_number(api_number)
        result_dict = result.to_dict()
        request_body = json.loads(result_dict['request_body'].replace("'", '"'))

        if result_dict['need_input_params'] != "":

            need_input_params = json.loads(result_dict['need_input_params'].replace("'", '"'))
            params_list = list(need_input_params.keys())
            current_params_key = params_list.pop()
            state['context']['api_info'] = result_dict
            state['context']['request_body'] = request_body
            state['context']['current_params_key'] = current_params_key
            state['context']['params_list'] = params_list
            state['context']['next_node'] = 'collection_params_node'
            state['context']['need_input_params'] = need_input_params
            state['messages'] = [AIMessage(content=f"请输入参数{current_params_key}")]
        else:
            state['context']['api_info'] = result_dict
            state['context']['request_body'] = request_body
            state['context']['next_node'] = 'http_node'
    except Exception as e:
        state['messages'] = [AIMessage(content="请输入一个数字或者输入正确的数字")]
        state['context']['next_node'] = 'command_node'
        state['context']['err'] = str(e)
    return state


def collection_params_node(state: AgentState):
    user_input = state['messages'][-1].content
    request_body = state['context']['request_body']
    current_params_key = state['context']['current_params_key']
    request_body[current_params_key] = user_input
    if len(state['context']['params_list']) == 0:
        state['context']['request_body'] = request_body
        state['context']['next_node'] = 'http_node'
    else:
        params_list = state['context']['params_list']
        current_params_key = params_list.pop()
        state['context']['request_body'] = request_body
        state['context']['current_params_key'] = current_params_key
        state['context']['params_list'] = params_list
        state['messages'] = [AIMessage(content=f"请输入参数{current_params_key}")]
    return state


def http_node(state: AgentState):
    api_info = state['context']['api_info']
    request_body = state['context']['request_body']
    url = api_info['url']
    method = api_info['method']
    content_type = api_info['content_type']
    result = request_api(url, method, request_body, content_type)
    # print(f"result:{result}")
    state['messages'] = [AIMessage(content=str(result))]
    state['context'] = {}
    return state


def collection_after(state: AgentState):
    next_node = state['context']['next_node']
    if next_node == 'http_node':
        return 'http_node'
    else:
        return '__end__'


def command_after(state: AgentState):
    next_node = state['context']['next_node']
    if next_node == 'http_node':
        return 'http_node'
    else:
        return '__end__'
