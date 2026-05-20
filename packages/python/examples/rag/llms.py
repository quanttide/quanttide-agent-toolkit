"""
大模型询问
"""

import random
import dashscope
from dashscope import Generation
from abc import ABC
from openai import OpenAI
import json
from config import llm_settins,load_api_key

#把api_key放在.secrets.yml中

class OpenaiModel():
    def __init__(self,model_name:str='gpt-3.5-turbo-instruct',temperature:float=0.9) -> None:
        super().__init__()
        self.model_name=model_name
        self.temperature=temperature
        self.model=OpenAI(model=model_name,temperature=temperature)

    #定义chat方法
    def chat(self,prompt:str):
        pass

class QWenModel():
    def __init__(self, model_name=Generation.Models.qwen_turbo, **kwargs):
        dashscope.api_key = load_api_key()
        self.model_name = model_name

    def chat_streamly(self, system, history, gen_conf):
        """
        流式传输，不是图形界面聊天用不到
        """
        from http import HTTPStatus
        if system:
            history.insert(0, {"role": "system", "content": system})
        ans = ""
        tk_count = 0
        try:
            response = Generation.call(
                self.model_name,
                messages=history,
                result_format='message',
                stream=True,
                **gen_conf
            )
            for resp in response:
                if resp.status_code == HTTPStatus.OK:
                    ans = resp.output.choices[0]['message']['content']
                    tk_count = resp.usage.total_tokens
                    if resp.output.choices[0].get("finish_reason", "") == "length":
                        ans += "...\nFor the content length reason, it stopped, continue?"
                    yield ans
                else:
                    yield ans + "\n**ERROR**: " + resp.message if str(resp.message).find("Access")<0 else "Out of credit. Please set the API key in **settings > Model providers.**"
        except Exception as e:
            yield ans + "\n**ERROR**: " + str(e)

        yield tk_count

    def get_response(self,messages:list[dict],tools:list[dict]):
        response = Generation.call(
            model='qwen-max',
            messages=messages,
            tools=tools,
            seed=random.randint(1, 10000),  # 设置随机数种子seed，如果没有设置，则随机数种子默认为1234
            result_format='message'  # 将输出设置为message形式
        )
        return response

    def function_call(self, tools: list[dict], prompt: str,text: str) -> dict:
        message = []
        dic = {}
        dic["content"] = prompt+text
        dic["role"] = "user"
        message.append(dic)
        return self.get_response(message,tools)
    
    def ask_llm(self, question, text:str) ->dict[str]:
        """
        用这个，这个是集成的
        """
        prompt = f"""
请你根据下面的资料回答用户问题，如果资料中的信息没有反应用户问题，则回答“不知道”

# 用户问题
{question}

# 资料
{text}
"""
        response = self.get_response([{"role": "user", "content": prompt}])
        parameter =  response["output"]["choices"][0]["message"]["tool_calls"][0]["function"]["arguments"]
        parameter = json.loads(parameter)
        return parameter["properties"]
