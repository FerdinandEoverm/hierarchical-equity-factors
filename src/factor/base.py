import pandas as pd
import os
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import hashlib

class FactorBase(ABC):
    """
    因子基类：所有具体因子都继承自此类。
    实现了依赖管理、自动缓存和统一计算接口。
    """
    
    # 全局配置：数据存储根目录
    DATA_ROOT = "./data/parquet" 

    def __init__(self, name: str, params: Dict[str, Any] = None):
        self.name = name
        self.params = params or {}
        self._dependencies: List['FactorBase'] = []
        
        # 自动生成唯一 ID (基于名字和参数)，用于缓存文件名
        self.factor_id = self._generate_id()

    def _generate_id(self) -> str:
        """生成因子的唯一标识符，防止参数不同但名字相同的冲突"""
        param_str = str(sorted(self.params.items()))
        # 使用哈希确保文件名安全且唯一
        param_hash = hashlib.md5(param_str.encode()).hexdigest()[:8]
        return f"{self.name}_{param_hash}"

    def add_dependency(self, factor: 'FactorBase'):
        """注册上游依赖因子"""
        self._dependencies.append(factor)
        return self  # 支持链式调用

    def get_file_path(self) -> str:
        """获取 Parquet 缓存文件的绝对路径"""
        os.makedirs(self.DATA_ROOT, exist_ok=True)
        return os.path.join(self.DATA_ROOT, f"{self.factor_id}.parquet")

    def load(self, start_date: str = None, end_date: str = None) -> pd.DataFrame:
        """
        [对外核心接口]
        1. 检查磁盘是否有缓存
        2. 有 -> 直接读取
        3. 无 -> 递归加载依赖 -> 计算 -> 落盘 -> 返回
        """
        path = self.get_file_path()
        
        # --- A. 尝试命中缓存 ---
        if os.path.exists(path):
            print(f"[Cache Hit] Loading {self.factor_id}...")
            df = pd.read_parquet(path)
            # 这里可以加入简单的切片逻辑
            # df = df.loc[...] 
            return df

        # --- B. 缓存未命中，触发计算 ---
        print(f"[Computing] {self.factor_id} (Dependencies: {len(self._dependencies)})...")
        
        # 1. 递归加载依赖数据 (Input Data)
        inputs = {}
        for dep in self._dependencies:
            inputs[dep.name] = dep.load(start_date, end_date)
            
        # 2. 执行核心计算逻辑 (由子类实现)
        result_df = self.compute(inputs)
        
        # 3. 自动落盘 (Persistence)
        # 建议使用我们讨论过的 'Long Format' (Date, Asset, Value) 以优化存储
        # 这里演示简单存取，实际需考虑 stack/unstack
        result_df.to_parquet(path)
        print(f"[Saved] {path}")
        
        return result_df

    @abstractmethod
    def compute(self, inputs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        """
        [子类必须实现]
        inputs: 包含所有上游数据的字典 {依赖名: DataFrame}
        return: 计算后的宽表 DataFrame (Index=Date, Columns=Asset)
        """
        pass