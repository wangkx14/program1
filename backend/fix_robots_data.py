import os
import pandas as pd
import numpy as np
from pathlib import Path
import random
from datetime import datetime, timedelta

def fix_robots_data():
    """修复和重新生成机器人数据"""
    # 获取 Excel 文件的绝对路径
    excel_path = str(Path(__file__).parent.parent / 'data' / 'charging_system_data.xlsx')
    print(f"Excel文件路径: {excel_path}")
    
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        print(f"错误: Excel文件不存在: {excel_path}")
        # 创建一个新的Excel文件
        create_new_excel_file(excel_path)
        return
    
    try:
        # 读取Excel文件
        xls = pd.ExcelFile(excel_path)
        sheet_names = xls.sheet_names
        print(f"现有表格: {sheet_names}")
        
        # 创建机器人数据
        robots_data = generate_robots_data(50)  # 生成50个机器人数据
        robots_df = pd.DataFrame(robots_data)
        
        # 读取原Excel文件中的所有数据
        dfs = {}
        for sheet_name in sheet_names:
            if sheet_name != 'robots':  # 跳过robots表格
                dfs[sheet_name] = pd.read_excel(excel_path, sheet_name=sheet_name)
        
        # 创建一个新的ExcelWriter对象
        with pd.ExcelWriter(excel_path) as writer:
            # 写入所有原有数据（除了robots表格）
            for sheet_name, df in dfs.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # 写入新的robots数据
            robots_df.to_excel(writer, sheet_name='robots', index=False)
        
        print(f"成功修复robots表格，生成了 {len(robots_data)} 条记录")
        return True
    except Exception as e:
        print(f"修复robots表格失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def create_new_excel_file(excel_path):
    """创建一个新的Excel文件，包含所有必要的表格"""
    print(f"创建新的Excel文件: {excel_path}")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(excel_path), exist_ok=True)
    
    # 创建所有必要的表格数据
    data = {
        'users': generate_users_data(10),
        'charging_stations': generate_stations_data(12),
        'robots': generate_robots_data(50),
        'charging_orders': generate_orders_data(100),
        'system_alerts': generate_alerts_data(20),
        'system_settings': generate_settings_data(),
        'system_logs': generate_logs_data(50),
        'efficiency_logs': generate_efficiency_logs_data(300)
    }
    
    # 转换为DataFrame
    dfs = {}
    for sheet_name, sheet_data in data.items():
        dfs[sheet_name] = pd.DataFrame(sheet_data)
    
    # 写入Excel文件
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"成功创建Excel文件: {excel_path}")

def generate_robots_data(count):
    """生成机器人数据"""
    robots = []
    statuses = ['idle', 'working', 'charging', 'error']
    
    now = datetime.now()
    
    for i in range(1, count + 1):
        # 随机生成数据
        robot = {
            'id': i,
            'name': f'机器人-{i:03d}',
            'battery_level': round(random.uniform(10, 100), 2),
            'status': random.choice(statuses),
            'created_at': (now - timedelta(days=random.randint(1, 60))).strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': (now - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 80%的概率有上次充电时间
        if random.random() < 0.8:
            robot['last_charging'] = (now - timedelta(days=random.randint(0, 20))).strftime('%Y-%m-%d %H:%M:%S')
        
        robots.append(robot)
    
    return robots

def generate_users_data(count):
    """生成用户数据"""
    users = []
    roles = ['admin', 'operator', 'viewer']
    
    for i in range(1, count + 1):
        users.append({
            'id': i,
            'username': f'user{i}',
            'password_hash': '$2b$12$M17H2agLx5jcXd4.mU08eOlfoeOFmopddcb1h7fvh3JQQvRV9Wjey',  # 默认密码: password
            'role': roles[i % len(roles)],
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return users

def generate_stations_data(count):
    """生成充电站数据"""
    stations = []
    statuses = ['idle', 'charging', 'maintenance', 'error']
    
    for i in range(1, count + 1):
        stations.append({
            'id': i,
            'name': f'充电站-{i}',
            'location': f'位置{i}',
            'status': random.choice(statuses),
            'power_output': round(random.uniform(5, 10), 2),
            'efficiency': round(random.uniform(80, 95), 2),
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return stations

def generate_orders_data(count):
    """生成充电订单数据"""
    orders = []
    statuses = ['charging', 'completed', 'failed']
    
    for i in range(1, count + 1):
        start_time = datetime.now() - timedelta(days=random.randint(0, 30), hours=random.randint(0, 24))
        status = random.choice(statuses)
        
        order = {
            'id': i,
            'robot_id': random.randint(1, 50),
            'station_id': random.randint(1, 12),
            'start_time': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'status': status,
            'created_at': start_time.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 如果状态是已完成，添加结束时间和充电量
        if status == 'completed':
            end_time = start_time + timedelta(hours=random.randint(1, 4))
            order['end_time'] = end_time.strftime('%Y-%m-%d %H:%M:%S')
            order['charge_amount'] = round(random.uniform(10, 50), 2)
        
        orders.append(order)
    
    return orders

def generate_alerts_data(count):
    """生成系统告警数据"""
    alerts = []
    types = ['warning', 'error', 'info']
    messages = ['充电站离线', '机器人电量低', '充电效率降低', '系统维护通知']
    
    for i in range(1, count + 1):
        alerts.append({
            'id': i,
            'time': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
            'type': random.choice(types),
            'message': random.choice(messages),
            'is_read': random.choice([True, False])
        })
    
    return alerts

def generate_settings_data():
    """生成系统设置数据"""
    settings = [
        {
            'id': 1,
            'setting_key': 'system_name',
            'setting_value': '充电站管理系统',
            'description': '系统名称',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 2,
            'setting_key': 'low_battery_threshold',
            'setting_value': '20',
            'description': '低电量阈值',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 3,
            'setting_key': 'high_efficiency_threshold',
            'setting_value': '90',
            'description': '高效率阈值',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 4,
            'setting_key': 'maintenance_interval',
            'setting_value': '30',
            'description': '维护间隔（天）',
            'updated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    return settings

def generate_logs_data(count):
    """生成系统日志数据"""
    logs = []
    actions = ['登录', '查看充电站', '查看机器人', '查看订单', '修改设置']
    
    for i in range(1, count + 1):
        logs.append({
            'id': i,
            'user_id': random.randint(1, 10),
            'action': random.choice(actions),
            'details': f'IP: 192.168.1.{random.randint(1, 255)}',
            'created_at': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return logs

def generate_efficiency_logs_data(count):
    """生成充电效率记录数据"""
    logs = []
    
    for i in range(1, count + 1):
        logs.append({
            'id': i,
            'station_id': random.randint(1, 12),
            'efficiency': round(random.uniform(80, 95), 2),
            'timestamp': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S')
        })
    
    return logs

if __name__ == "__main__":
    print("开始修复机器人数据...")
    if fix_robots_data():
        print("机器人数据修复成功")
    else:
        print("机器人数据修复失败") 