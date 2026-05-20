"""
文本分割

Token分割器		基于Token进行文本分割。存在一些不同的Token计量方法。
字符分割器		基于用户定义的字符进行文本分割。这是较为简单的分割方法之一。
语义分块器		首先基于句子进行分割。然后，如果它们在语义上足够相似，就将相邻的句子组合在一起。

"""

import tiktoken

# 用于数据切分时，判断字块的token长度，速度比较快
enc = tiktoken.get_encoding("cl100k_base")

class Chunker:

    def __init__(self,pattern:str):
        """
        传入分割模式
        'chunk_by_paragraph'
        'chunk_by_token'
        'chunk_by_sentences'
        """
        self.pattern = pattern

    # 切分数据，传入一个字符串，返回一个字块列表
    @classmethod
    def chunk_by_token(cls, text: str, max_token_len: int = 600, cover_content: int = 150) ->list[str]:
        chunk_text = []
        curr_len = 0
        curr_chunk = ''
        lines = text.split('\n')
        for line in lines:
            line = line.replace(' ', '')
            line_len = len(enc.encode(line))
            if curr_len + line_len <= max_token_len:
                curr_chunk += line
                curr_chunk += '\n'
                curr_len += line_len
                curr_len += 1
            else:
                chunk_text.append(curr_chunk)
                curr_chunk = curr_chunk[-cover_content:]+line
                curr_len = line_len + cover_content
        if curr_chunk:
            chunk_text.append(curr_chunk)
        return chunk_text
    
    def chunk(self, text: str, max_token_len: int = 600, cover_content: int = 150) ->list[str]:
        if self.pattern == 'chunk_by_paragraph':
            return self.chunk_by_paragraph(text,max_token_len)
        elif self.pattern == 'chunk_by_token':
            return self.chunk_by_token(text,max_token_len,cover_content)
        elif self.pattern == 'chunk_by_sentences':
            return self.chunk_by_sentences(text,max_token_len)

    @classmethod
    def chunk_by_paragraph(cls, text:str, max_token_len: int = 600) ->list[str]:
        chunk_text = []  # 存储分割后的文本块
        paragraphs = text.split('\n\n')  # 将文本按段落分割
        for para in paragraphs:
            lines = para.split('\n')  # 将段落按行分割
            curr_chunk = ''  # 当前块的内容
            curr_len = 0  # 当前块的长度
        
            for line in lines:
                line = line.replace(' ', '')  # 去除行中的空格
                line_len = len(enc.encode(line))  # 编码行并计算长度
            
                if curr_len + line_len <= max_token_len:
                    # 如果当前块加上这行后的长度不超过最大长度
                    curr_chunk += line + '\n'
                    curr_len += line_len + 1  # 加上换行符的长度
                else:
                    # 当前块加上这行后的长度超过最大长度
                    # 先把当前块加入结果
                    chunk_text.append(curr_chunk)
                    # 重新开始一个新块
                    curr_chunk = line + '\n'
                    curr_len = line_len + 1
        
            # 检查当前段落是否超过最大长度，如果超过则进一步分割
            while curr_len > max_token_len:
                chunk_text.append(curr_chunk[:max_token_len])
                curr_chunk = curr_chunk[max_token_len:]
                curr_len = len(enc.encode(curr_chunk))
        
            # 将处理完的块加入结果
            if curr_chunk:
                chunk_text.append(curr_chunk)
    
        return chunk_text
    
    @classmethod
    def chunk_by_sentences(cls,text:str, max_token_len:int):
        chunk_text = []  # 存储分割后的文本块
        sentences = text.split('。')  # 将文本按句子分割，使用句号作为分隔符
        curr_chunk = ''  # 当前块的内容
        curr_len = 0  # 当前块的长度

        for sentence in sentences:
            sentence = sentence.replace(' ', '')  # 去除句子中的空格
            sentence_len = len(enc.encode(sentence))  # 编码句子并计算长度
        
            if curr_len + sentence_len + 1 <= max_token_len:  # 加1是因为要补上句号
                # 如果当前块加上这句后的长度不超过最大长度
                curr_chunk += sentence + '。'
                curr_len += sentence_len + 1
            else:
                # 当前块加上这句后的长度超过最大长度
                chunk_text.append(curr_chunk)  # 先把当前块加入结果
                curr_chunk = sentence + '。'
                curr_len = sentence_len + 1
            
                # 检查当前句子是否超过最大长度，如果超过则进一步分割
                while curr_len > max_token_len:
                    chunk_text.append(curr_chunk[:max_token_len])
                    curr_chunk = curr_chunk[max_token_len:]
                    curr_len = len(enc.encode(curr_chunk))
    
        if curr_chunk:
            chunk_text.append(curr_chunk)  # 将最后一个块加入结果
    
        return chunk_text