import os
import sys
import pandas as pd
from pathlib import Path

def check_robots_data():
    """专门检查机器人表格的数据"""
    # 获取 Excel 文件的绝对路径
    excel_path = str(Path(__file__).parent.parent / 'data' / 'charging_system_data.xlsx')
    print(f"检查 Excel 文件: {excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        print(f"错误: Excel 文件不存在: {excel_path}")
        return False
    
    # 检查机器人表格
    try:
        # 首先检查表格是否存在
        xls = pd.ExcelFile(excel_path)
        if 'robots' not in xls.sheet_names:
            print(f"错误: Excel 文件中不存在 'robots' 表格")
            print(f"可用的表格: {xls.sheet_names}")
            return False
        
        # 读取机器人表格
        df = pd.read_excel(excel_path, sheet_name='robots')
        print(f"机器人表格读取成功，共 {len(df)} 条记录")
        
        # 检查必要的列是否存在
        required_columns = ['id', 'name', 'battery_level', 'status']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"错误: 机器人表格缺少必要的列: {missing_columns}")
            print(f"现有列: {df.columns.tolist()}")
            return False
        
        # 打印所有数据
        print("机器人表格的所有数据:")
        print(df)
        
        # 检查数据类型
        print("\n数据类型检查:")
        print(df.dtypes)
        
        # 检查是否有空值
        print("\n空值检查:")
        print(df.isnull().sum())
        
        return True
    except Exception as e:
        print(f"错误: 检查机器人表格失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if check_robots_data():
        print("机器人表格检查通过")
        sys.exit(0)
    else:
        print("机器人表格检查失败")
        sys.exit(1) 