"""
向量比较，寻找最合适文本块

文本多路召回与重排序

"""
from typing import List
import numpy as np
from models import ProcessedText,BestMatch

class Comparator:

    def rank(self, processed_text:ProcessedText) ->BestMatch:
        """
        针对处理后的向量文本进行比较，同时进行倒排索引，
        综合两者获得排名后，再次进行重排序
        获得最终排名
        """

    #对两个向量进行相似度求值，余弦相似度求值 
    def compare_v(cls, vector1: List[float], vector2: List[float]) -> float:
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)
        if not magnitude:
            return 0
        return dot_product / magnitude
    
    def compare(self, question:ProcessedText, vector_model: ProcessedText,k:int = 3) ->BestMatch:
        file_contents_with_vector = vector_model.file_contents_with_vector
        question_contents_with_vector = question.file_contents_with_vector
        relevant_text = {}
        for key ,value in question_contents_with_vector.items():
            # 历史遗留问题，此处原本是用来给多个问题进行处理的
            # 所以用了循环，但现在问题只有一个
            query_vector = value['vector']
            front_k_text = self.query(query_vector,file_contents_with_vector,k)
            relevant_text = front_k_text

        return BestMatch(file_id=vector_model.file_id,
                         file_path=vector_model.file_path,
                         file_name=vector_model.file_name,
                         relevant_text=relevant_text,
                         )

    #求一个字符串和向量列表里的所有向量的相似度，表进行排序，返回相似度前k个的子块列表
    def query(self, query_vector,file_contents_with_vector:dict[str,np.ndarray], k:int) -> List[str]:
        similarities = {key: self.compare_v(query_vector, vector) for key, vector in file_contents_with_vector.items()}
        sorted_keys = sorted(similarities, key=similarities.get, reverse=True)[:k]
        return sorted_keys