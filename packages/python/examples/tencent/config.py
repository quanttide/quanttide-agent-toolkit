import os

from dynaconf import Dynaconf


# 配置密钥文件
secret_file = os.path.join(os.path.dirname(__file__), '.secrets.yml')
if not os.path.exists(secret_file):
    raise Exception(f'secret file {secret_file} not found')

settings = Dynaconf(settings_files=[secret_file])
