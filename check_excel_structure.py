import pandas as pd
import os

def print_excel_structure(file_path):
    print(f"读取文件: {file_path}")
    try:
        # 获取所有工作表名称
        excel_file = pd.ExcelFile(file_path)
        sheet_names = excel_file.sheet_names
        print(f"工作表列表: {sheet_names}")
        
        # 读取每个工作表的结构
        for sheet_name in sheet_names:
            print(f"\n工作表: {sheet_name}")
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            print(f"行数: {len(df)}")
            print(f"列名: {list(df.columns)}")
            print("前5行数据:")
            print(df.head())
            print("-" * 80)
    except Exception as e:
        print(f"读取文件时出错: {e}")

if __name__ == "__main__":
    # 读取数据表结构
    schema_file = os.path.join("data", "数据表.xlsx")
    if os.path.exists(schema_file):
        print_excel_structure(schema_file)
    else:
        print(f"文件不存在: {schema_file}")
    
    # 读取数据文件结构
    data_file = os.path.join("data", "charging_system_data.xlsx")
    if os.path.exists(data_file):
        print_excel_structure(data_file)
    else:
        print(f"文件不存在: {data_file}") 