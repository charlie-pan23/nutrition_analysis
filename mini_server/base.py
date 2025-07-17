from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 数据库连接字符串
DATABASE_URL = "mysql+pymysql://root:123456@localhost/nas"

# 创建引擎
engine = create_engine(DATABASE_URL)

# 创建基类
Base = declarative_base()

# 创建会话类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)