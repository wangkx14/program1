import os
import sys
import pandas as pd
from pathlib import Path

def check_excel_file():
    """检查 Excel 文件是否存在以及表格是否正确"""
    # 获取 Excel 文件的绝对路径
    excel_path = str(Path(__file__).parent.parent / 'data' / 'charging_system_data.xlsx')
    print(f"检查 Excel 文件: {excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        print(f"错误: Excel 文件不存在: {excel_path}")
        return False
    
    # 检查文件是否可读
    try:
        xls = pd.ExcelFile(excel_path)
        print(f"Excel 文件可读，包含以下表格: {xls.sheet_names}")
        
        # 预期的表格列表
        expected_sheets = [
            'users', 
            'charging_stations', 
            'robots', 
            'charging_orders', 
            'system_alerts', 
            'system_settings', 
            'system_logs', 
            'efficiency_logs'
        ]
        
        # 检查是否所有预期的表格都存在
        missing_sheets = [sheet for sheet in expected_sheets if sheet not in xls.sheet_names]
        if missing_sheets:
            print(f"警告: 以下预期的表格不存在: {missing_sheets}")
        
        # 读取每个表格的数据，并检查行数
        for sheet in xls.sheet_names:
            try:
                df = pd.read_excel(excel_path, sheet_name=sheet)
                print(f"表格 '{sheet}' 读取成功，共 {len(df)} 条记录")
                
                # 打印前 3 行数据的列名，用于调试
                if len(df) > 0:
                    print(f"列名: {df.columns.tolist()}")
                    print(f"前 3 行数据示例:")
                    print(df.head(3))
                else:
                    print(f"警告: 表格 '{sheet}' 没有数据")
            except Exception as e:
                print(f"错误: 读取表格 '{sheet}' 失败: {str(e)}")
        
        return True
    except Exception as e:
        print(f"错误: 无法读取 Excel 文件: {str(e)}")
        return False

if __name__ == "__main__":
    if check_excel_file():
        print("Excel 文件检查通过")
        sys.exit(0)
    else:
        print("Excel 文件检查失败")
        sys.exit(1)