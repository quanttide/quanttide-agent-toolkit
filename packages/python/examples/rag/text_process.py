"""
文本处理函数
对文本分别进行向量化
"""

import numpy as np
from embedding import Embedding,ZhipuEmbedding,QwenEmbedding,OpenAIEmbedding
from config import load_api_key,embedding_settings
from models import ChunkedText, ProcessedText

class TextProcessor:
    def __init__(self, embedding_scheme: str = 'qwen') -> None:
        """
        file_path: questions.json文件的路径
        embedding_scheme: 选择向量化方案，'zhipu', 'openai',或'qwen'
        """
        self.embedding_scheme = embedding_scheme
        if self.embedding_scheme != 'debug':
            self.embedding = self.get_embedding_model()

    def get_embedding_model(self) -> Embedding:
        if self.embedding_scheme == 'zhipu':
            return ZhipuEmbedding(load_api_key('zhipu'))
        elif self.embedding_scheme == 'openai':
            return OpenAIEmbedding(load_api_key('openai'))
        elif self.embedding_scheme == 'qwen':
            return QwenEmbedding(load_api_key('qwen'))
        else:
            raise ValueError("Unsupported embedding scheme")
        
    def process_model(self,chunked_model: ChunkedText) ->ProcessedText:
        texts = chunked_model.file_contents
        res_embedding, tokens = self.embedding.encode(texts)

        # 将文本段与它们的嵌入向量对应起来
        file_contents_with_vector = {text: vector for text, vector in zip(texts, res_embedding)}
        
        return ProcessedText(file_id=chunked_model.file_id,
                             file_path=chunked_model.file_path,
                             file_name=chunked_model.file_name,
                             file_contents_with_vector=file_contents_with_vector
                             )
    
    def process_text(self,text:str) ->ProcessedText:
        
        res_embedding = self.embedding.encode(text)
        return ProcessedText(file_id=None,
                             file_path=None,
                             file_name=None,
                             file_contents_with_vector={text: res_embedding}
                             )