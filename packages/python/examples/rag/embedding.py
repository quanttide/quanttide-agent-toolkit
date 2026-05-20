"""
Embedding with `sentence-transformers`

Ref:
  - https://www.sbert.net
  - https://mp.weixin.qq.com/s/gBgTIHdAIMlxacxQBVkI8w
"""

"""
词嵌入，向量化
"""
from abc import ABC
from typing import List, Tuple
import dashscope
import numpy as np
from zhipuai import ZhipuAI
import os
from openai import OpenAI

#Embedding类



class QwenEmbedding():
    def __init__(self, 
                 key, 
                 model_name="text-embedding-v2", 
                 **kwargs) -> None:
        dashscope.api_key = key
        self.model_name = model_name

    def encode(self, texts: list, batch_size=10) -> Tuple[np.ndarray, int]:
        try:
            res = []
            token_count = 0
            for i in range(0, len(texts), batch_size):
                resp = dashscope.TextEmbedding.call(
                    model=self.model_name,
                    input=texts[i:i + batch_size],
                    text_type="document"
                )
                embds = [[] for _ in range(len(resp["output"]["embeddings"]))]
                for e in resp["output"]["embeddings"]:
                    embds[e["text_index"]] = e["embedding"]
                res.extend(embds)
                token_count += resp["usage"]["total_tokens"]
            return np.array(res), token_count
        except Exception as e:
            raise Exception("Account abnormal. Please ensure it's on good standing to use QWen's "+self.model_name)


class OpenAIEmbedding():
    
    def __init__(self, 
                 key, 
                 model_name="text-embedding-ada-002",
                 base_url="https://api.openai.com/v1"):
        self.client = OpenAI(api_key=key, base_url=base_url)
        self.model_name = model_name

    
    def encode(self, texts: list, batch_size=32) -> Tuple[np.ndarray, int]:
        res = self.client.embeddings.create(input=texts,
                                            model=self.model_name)
        return np.array([d.embedding for d in res.data]
                        ), res.usage.total_tokens




class ZhipuEmbedding():

    def __init__(self, path:str=''):
        client = ZhipuAI(api_key=os.getenv("ZHIPUAI_API_KEY")) 
        self.embedding_model=client


    def encode(self, texts: list, batch_size=32) -> Tuple[np.ndarray, int]:
        arr = []
        tks_num = 0
        for txt in texts:
            res = self.client.embeddings.create(input=txt,
                                                model=self.model_name)
            arr.append(res.data[0].embedding)
            tks_num += res.usage.total_tokens
        return np.array(arr), tks_num


