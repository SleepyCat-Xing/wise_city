from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self):
        self.engine = None
        self.async_session = None
        self._initialized = False
    
    async def initialize(self):
        """初始化数据库连接"""
        if self._initialized:
            return
            
        try:
            # 创建异步引擎
            self.engine = create_async_engine(
                settings.DATABASE_URL,
                echo=settings.LOG_LEVEL == "DEBUG",
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                pool_recycle=300
            ) if settings.DATABASE_URL else None
            
            if self.engine:
                # 创建异步会话工厂
                self.async_session = async_sessionmaker(
                    bind=self.engine,
                    class_=AsyncSession,
                    expire_on_commit=False
                )
                logger.info("数据库连接已初始化")
            else:
                logger.warning("未配置数据库URL，数据库功能将被禁用")
                
            self._initialized = True
            
        except Exception as e:
            logger.error(f"数据库初始化失败: {str(e)}")
            raise
    
    async def create_tables(self):
        """创建数据库表"""
        if not self.engine:
            logger.warning("数据库引擎未初始化，跳过表创建")
            return
            
        try:
            from app.models.database import Base
            async with self.engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建完成")
        except Exception as e:
            logger.error(f"创建数据库表失败: {str(e)}")
            raise
    
    async def get_session(self) -> AsyncSession:
        """获取数据库会话"""
        if not self.async_session:
            raise RuntimeError("数据库会话未初始化")
        return self.async_session()
    
    async def close(self):
        """关闭数据库连接"""
        if self.engine:
            await self.engine.dispose()
            logger.info("数据库连接已关闭")

# 全局数据库管理器实例
db_manager = DatabaseManager()

async def get_database():
    """获取数据库会话的依赖项"""
    if not db_manager._initialized:
        await db_manager.initialize()
    
    if not db_manager.async_session:
        # 如果数据库未配置，返回None
        yield None
        return
        
    async with db_manager.get_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def init_database():
    """初始化数据库（应用启动时调用）"""
    try:
        await db_manager.initialize()
        await db_manager.create_tables()
        logger.info("数据库初始化完成")
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        # 不抛出异常，允许应用在没有数据库的情况下运行

async def close_database():
    """关闭数据库连接（应用关闭时调用）"""
    await db_manager.close()