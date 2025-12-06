# hierarchical-equity-factors

hierarchical-equity-factors/
├── data/                  # 自动生成的 Parquet 文件存放处
│   └── parquet/
├── src/
│   ├── factors/
│   │   ├── __init__.py
│   │   ├── base.py        # 上面的 FactorBase 代码
│   │   ├── L0_data.py     # 原始数据读取类 (Read from CSV/SQL)
│   │   ├── L1_features.py # 基础特征 (LogReturn, Volume, etc.)
│   │   └── L2_alpha.py    # 复杂因子 (Momentum, Volatility)
│   └── utils/
│       └── dataloader.py  # 数据库连接工具
├── run_backtest.py        # 入口脚本
└── README.md