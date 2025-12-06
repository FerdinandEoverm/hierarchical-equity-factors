# 假设你已经定义了 L0 (ClosePrice)
from .base import FactorBase

class MomentumFactor(FactorBase):
    def __init__(self, price_factor: FactorBase, window: int = 20):
        # 1. 初始化元数据
        name = "Momentum"
        params = {"window": window}
        super().__init__(name, params)
        
        # 2. 注册依赖 (这一步至关重要，构建了计算图 DAG)
        self.add_dependency(price_factor)
        self.window = window

    def compute(self, inputs: Dict[str, pd.DataFrame]) -> pd.DataFrame:
        # 3. 获取依赖数据
        # inputs 的 key 是依赖因子的 name
        # 假设 price_factor 的 name 是 'ClosePrice'
        close_df = list(inputs.values())[0] # 或者 inputs['ClosePrice']
        
        # 4. 核心逻辑 (Pandas Vectorized Operation)
        # 动量 = (当前价格 / N天前价格) - 1
        mom = close_df.pct_change(self.window)
        
        return mom