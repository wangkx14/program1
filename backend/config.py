import os

class Config:
    SECRET_KEY = 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@localhost/warehouse'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-key'
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1小时
    JWT_IDENTITY_CLAIM = 'sub'  # 默认的身份声明字段
    JWT_ERROR_MESSAGE_KEY = 'error'  # 错误消息的键名 