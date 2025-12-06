import pandas as pd
import numpy as np
import torch

def check_nan_inf(data, name="Data", max_print=5):
    """
    检查数据中的 NaN 和 Inf 值。
    支持类型: pd.DataFrame, pd.Series, np.ndarray, torch.Tensor
    
    参数:
        data: 输入数据
        name: 数据名称 (用于报错信息的标识)
        max_print: 对于数组/张量，最多打印多少个错误坐标
    """
    
    has_error = False
    
    # ---------------------------------------------------------
    # 1. 处理 Pandas DataFrame
    # ---------------------------------------------------------
    if isinstance(data, pd.DataFrame):
        # NaN Check
        nan_counts = data.isnull().sum()
        nan_cols = nan_counts[nan_counts > 0]
        if not nan_cols.empty:
            print(f"❌ [NaN] {name} (DataFrame): 发现 {len(nan_cols)} 个列存在缺失值:")
            for col, count in nan_cols.items():
                print(f"    - 列名: {col} (共 {count} 处)")
            has_error = True

        # Inf Check (只检查数值列)
        numeric_df = data.select_dtypes(include=np.number)
        if not numeric_df.empty:
            inf_counts = np.isinf(numeric_df).sum()
            inf_cols = inf_counts[inf_counts > 0]
            if not inf_cols.empty:
                print(f"❌ [Inf] {name} (DataFrame): 发现 {len(inf_cols)} 个列存在无穷值:")
                for col, count in inf_cols.items():
                    print(f"    - 列名: {col} (共 {count} 处)")
                has_error = True

    # ---------------------------------------------------------
    # 2. 处理 Pandas Series
    # ---------------------------------------------------------
    elif isinstance(data, pd.Series):
        # NaN Check
        if data.isnull().any():
            count = data.isnull().sum()
            print(f"❌ [NaN] {name} (Series): 发现 {count} 处缺失值")
            # 打印前几个索引
            inds = data[data.isnull()].index[:max_print].tolist()
            print(f"    - 示例索引: {inds} ...")
            has_error = True
            
        # Inf Check
        if np.issubdtype(data.dtype, np.number):
            if np.isinf(data).any():
                count = np.isinf(data).sum()
                print(f"❌ [Inf] {name} (Series): 发现 {count} 处无穷值")
                inds = data[np.isinf(data)].index[:max_print].tolist()
                print(f"    - 示例索引: {inds} ...")
                has_error = True

    # ---------------------------------------------------------
    # 3. 处理 Numpy Array
    # ---------------------------------------------------------
    elif isinstance(data, np.ndarray):
        # NaN Check
        if np.isnan(data).any():
            coords = np.argwhere(np.isnan(data))
            count = len(coords)
            print(f"❌ [NaN] {name} (ndarray): 发现 {count} 处缺失值")
            print(f"    - 坐标 (前 {max_print} 个):")
            for coord in coords[:max_print]:
                print(f"      {tuple(coord)}")
            has_error = True
            
        # Inf Check
        if np.isinf(data).any():
            coords = np.argwhere(np.isinf(data))
            count = len(coords)
            print(f"❌ [Inf] {name} (ndarray): 发现 {count} 处无穷值")
            print(f"    - 坐标 (前 {max_print} 个):")
            for coord in coords[:max_print]:
                print(f"      {tuple(coord)}")
            has_error = True

    # ---------------------------------------------------------
    # 4. 处理 PyTorch Tensor
    # ---------------------------------------------------------
    elif torch.is_tensor(data):
        # NaN Check
        if torch.isnan(data).any():
            coords = torch.nonzero(torch.isnan(data), as_tuple=False)
            count = coords.shape[0]
            print(f"❌ [NaN] {name} (Tensor): 发现 {count} 处缺失值")
            print(f"    - 坐标 (前 {max_print} 个):")
            for i in range(min(count, max_print)):
                print(f"      {tuple(coords[i].tolist())}")
            has_error = True
            
        # Inf Check
        if torch.isinf(data).any():
            coords = torch.nonzero(torch.isinf(data), as_tuple=False)
            count = coords.shape[0]
            print(f"❌ [Inf] {name} (Tensor): 发现 {count} 处无穷值")
            print(f"    - 坐标 (前 {max_print} 个):")
            for i in range(min(count, max_print)):
                print(f"      {tuple(coords[i].tolist())}")
            has_error = True

    else:
        print(f"⚠️ Warning: 不支持的数据类型 {type(data)}")
        return

    # 统一抛出异常
    if has_error:
        raise ValueError(f"Data check failed for '{name}'. Found NaN or Inf.")

# ==========================================
# 测试代码
# ==========================================
if __name__ == "__main__":
    print("--- Testing DataFrame ---")
    df = pd.DataFrame({'A': [1, 2, np.nan], 'B': [4, np.inf, 6], 'C': [1, 2, 3]})
    try: check_nan_inf(df, "MyDF")
    except ValueError as e: print(e)

    print("\n--- Testing Numpy Array ---")
    arr = np.array([[1, 2, 3], [4, np.nan, 6], [7, 8, np.inf]])
    try: check_nan_inf(arr, "MyArray")
    except ValueError as e: print(e)

    print("\n--- Testing PyTorch Tensor ---")
    try:
        ts = torch.tensor([[[1.0, 2.0], [np.nan, 4.0]], [[5.0, float('inf')], [7.0, 8.0]]])
        check_nan_inf(ts, "MyTensor")
    except ValueError as e: print(e)