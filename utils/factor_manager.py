import sqlite3
import pandas as pd
import os

class FactorManager:
    def __init__(self, db_path='quant_meta.db', data_dir='./data_parquet'):
        self.conn = sqlite3.connect(db_path)
        self.data_dir = data_dir
        self._init_db()

    def _init_db(self):
        # 初始化元数据表
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS factor_registry (
                factor_name TEXT PRIMARY KEY,
                category TEXT,
                description TEXT,
                file_path TEXT,
                last_updated TIMESTAMP
            )
        ''')
        self.conn.commit()

    def register_factor(self, name, category, df_data):
        """
        1. 把大张的数据存为 Parquet (重资产)
        2. 把因子的信息存入 SQLite (轻资产)
        """
        # A. 存 Parquet
        file_name = f"{name}.parquet"
        full_path = os.path.join(self.data_dir, file_name)
        
        # (这里复用之前的 Long Format 存储逻辑)
        df_long = df_data.stack().reset_index()
        df_long.columns = ['date', 'asset', 'value']
        df_long.to_parquet(full_path)

        # B. 写数据库索引
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO factor_registry (factor_name, category, file_path, last_updated)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ''', (name, category, file_name))
        self.conn.commit()
        print(f"因子 {name} 已注册并落盘。")

    def get_factor(self, name):
        """
        1. 问数据库：文件在哪？
        2. 读 Parquet：拿数据。
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM factor_registry WHERE factor_name = ?", (name,))
        result = cursor.fetchone()
        
        if not result:
            raise ValueError(f"因子 {name} 不存在于注册表中！")
            
        file_path = os.path.join(self.data_dir, result[0])
        
        # 读数据并透视为宽表
        df = pd.read_parquet(file_path)
        return df.pivot(index='date', columns='asset', values='value')

    def list_factors(self, category=None):
        """
        利用数据库的查询能力，快速筛选因子
        """
        query = "SELECT factor_name, last_updated FROM factor_registry"
        if category:
            query += f" WHERE category = '{category}'"
        return pd.read_sql(query, self.conn)

# --- 使用示例 ---
fm = FactorManager()

# 1. 只有 SQLite 才能做这种快速筛选
print("当前所有的动量因子：")
print(fm.list_factors(category="Momentum"))

# 2. 确定要读取后，再加载 Parquet
df_mom = fm.get_factor("Momentum_10d")