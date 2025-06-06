import os
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import bcrypt
from faker import Faker
import uuid

# 初始化Faker，用于生成假数据
fake = Faker('zh_CN')

# 确保data目录存在
if not os.path.exists('data'):
    os.makedirs('data')

# 设置随机种子，确保结果可重现
random.seed(42)
np.random.seed(42)

# 当前时间，用作基准时间
now = datetime.now()

def generate_users():
    """生成用户数据，只生成admin和user两种角色各一个账号"""
    users = []
    
    # 添加管理员用户
    admin_password = 'admin123'
    admin_password_hash = bcrypt.hashpw(admin_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users.append({
        'id': 1,
        'username': 'admin',
        'password': admin_password,  # 添加明文密码字段
        'password_hash': admin_password_hash,
        'role': 'admin',
        'created_at': (now - timedelta(days=30)).strftime('%Y-%m-%d %H:%M:%S')
    })
    
    # 添加普通用户
    user_password = 'user123'
    user_password_hash = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users.append({
        'id': 2,
        'username': 'user',
        'password': user_password,  # 添加明文密码字段
        'password_hash': user_password_hash,
        'role': 'user',
        'created_at': (now - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
    })
    
    return pd.DataFrame(users)

def generate_charging_stations():
    """生成充电站数据，总数为12条"""
    stations = []
    
    # 充电站状态选项
    statuses = ['idle', 'charging', 'maintenance', 'error']
    
    # 生成12条充电站记录
    for i in range(1, 13):
        # 随机选择状态，但大多数应该是idle或charging
        status_weights = [0.4, 0.4, 0.1, 0.1]  # 权重分配
        status = random.choices(statuses, weights=status_weights)[0]
        
        # 随机生成功率和效率
        power_output = round(random.uniform(5.0, 15.0), 2)  # 5kW到15kW之间
        efficiency = round(random.uniform(85.0, 100.0), 2) if status != 'error' else round(random.uniform(50.0, 85.0), 2)
        
        # 创建时间在1-60天之间随机
        created_days_ago = random.randint(1, 60)
        created_at = (now - timedelta(days=created_days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新时间在创建时间之后
        updated_days_ago = random.randint(0, created_days_ago)
        updated_at = (now - timedelta(days=updated_days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        stations.append({
            'id': i,
            'name': f'充电站-{i}',
            'location': fake.address(),
            'status': status,
            'power_output': power_output,
            'efficiency': efficiency,
            'created_at': created_at,
            'updated_at': updated_at
        })
    
    return pd.DataFrame(stations)

def generate_robots():
    """生成机器人数据，总数为50个"""
    robots = []
    
    # 机器人状态选项
    statuses = ['idle', 'working', 'charging', 'error']
    
    # 生成50条机器人记录
    for i in range(1, 51):
        # 随机选择状态
        status_weights = [0.3, 0.4, 0.2, 0.1]  # 权重分配
        status = random.choices(statuses, weights=status_weights)[0]
        
        # 随机生成电池电量
        battery_level = round(random.uniform(10.0, 100.0), 2)
        
        # 如果状态是charging，电量应该较低
        if status == 'charging':
            battery_level = round(random.uniform(10.0, 40.0), 2)
        # 如果状态是idle，电量应该较高
        elif status == 'idle':
            battery_level = round(random.uniform(60.0, 100.0), 2)
        
        # 创建时间在1-90天之间随机
        created_days_ago = random.randint(1, 90)
        created_at = (now - timedelta(days=created_days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 更新时间在创建时间之后
        updated_days_ago = random.randint(0, created_days_ago)
        updated_at = (now - timedelta(days=updated_days_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 上次充电时间，可能为空
        if random.random() > 0.1:  # 90%的机器人有上次充电记录
            last_charging_days_ago = random.randint(0, min(created_days_ago, 30))
            last_charging = (now - timedelta(days=last_charging_days_ago, 
                                           hours=random.randint(0, 23),
                                           minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        else:
            last_charging = None
        
        robots.append({
            'id': i,
            'name': f'机器人-{i:03d}',
            'battery_level': battery_level,
            'status': status,
            'last_charging': last_charging,
            'created_at': created_at,
            'updated_at': updated_at
        })
    
    return pd.DataFrame(robots)

def generate_charging_orders(robots_df, stations_df):
    """生成充电订单数据，总数为3000条，时间范围为当前时间往前推30天"""
    orders = []
    
    # 订单状态选项
    statuses = ['charging', 'completed', 'failed']
    
    # 生成3000条订单记录
    for order_id in range(1, 3001):
        # 随机选择一个机器人
        robot = robots_df.iloc[random.randint(0, len(robots_df)-1)]
        
        # 随机选择一个充电站
        station = stations_df.iloc[random.randint(0, len(stations_df)-1)]
        
        # 随机生成订单状态
        status_weights = [0.2, 0.7, 0.1]  # 大多数订单已完成
        status = random.choices(statuses, weights=status_weights)[0]
        
        # 订单开始时间在最近30天内
        start_minutes_ago = random.randint(0, 30 * 24 * 60)  # 30天内的分钟数
        start_time = (now - timedelta(minutes=start_minutes_ago)).strftime('%Y-%m-%d %H:%M:%S')
        
        # 如果订单已完成或失败，设置结束时间
        if status in ['completed', 'failed']:
            # 充电时间在30分钟到4小时之间
            charging_minutes = random.randint(30, 240)
            end_time = (datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S') + 
                       timedelta(minutes=charging_minutes)).strftime('%Y-%m-%d %H:%M:%S')
            
            # 如果是已完成的订单，计算充电量和充电效率
            if status == 'completed':
                # 获取充电站基础效率
                base_efficiency = station['efficiency']
                
                # 生成充电效率，在基础效率上下波动不超过5%
                charging_efficiency = round(base_efficiency + random.uniform(-5, 5), 2)
                # 确保效率在有效范围内
                charging_efficiency = max(50, min(100, charging_efficiency))
                
                # 获取充电站功率
                power_output = station['power_output']
                
                # 计算充电量 (kWh)，使用生成的充电效率
                charge_amount = round(power_output * (charging_minutes / 60) * charging_efficiency / 100, 2)
            else:
                charge_amount = None
                charging_efficiency = None
        else:
            end_time = None
            charge_amount = None
            charging_efficiency = None
        
        # 创建时间等于开始时间
        created_at = start_time
        
        # 更新时间等于结束时间（如果有），否则等于创建时间
        updated_at = end_time if end_time else created_at
        
        orders.append({
            'id': order_id,
            'robot_id': robot['id'],
            'station_id': station['id'],
            'start_time': start_time,
            'end_time': end_time,
            'status': status,
            'charge_amount': charge_amount,
            'charging_efficiency': charging_efficiency,  # 新增充电效率字段
            'created_at': created_at,
            'updated_at': updated_at
        })
    
    # 按开始时间排序
    orders_df = pd.DataFrame(orders)
    orders_df = orders_df.sort_values(by='start_time', ascending=False)
    
    # 重置索引
    orders_df = orders_df.reset_index(drop=True)
    
    return orders_df

def generate_system_alerts():
    """生成系统告警数据，总数控制在10条以内"""
    alerts = []
    
    # 告警类型
    alert_types = ['警告', '信息', '错误']
    
    # 告警消息模板
    alert_messages = [
        '充电站 #{} 充电效率低于阈值',
        '机器人 #{} 电量过低',
        '充电站 #{} 连接中断',
        '机器人 #{} 充电异常',
        '系统检测到网络波动',
        '数据库备份完成',
        '充电站 #{} 恢复正常',
        '机器人 #{} 完成充电',
        '系统更新可用'
    ]
    
    # 生成10条告警记录
    for i in range(1, 11):
        # 随机选择告警类型
        alert_type = random.choice(alert_types)
        
        # 随机选择一条消息并格式化
        message_template = random.choice(alert_messages)
        if '{}' in message_template:
            if '充电站' in message_template:
                message = message_template.format(random.randint(1, 12))
            else:  # 机器人
                message = message_template.format(random.randint(1, 50))
        else:
            message = message_template
        
        # 告警时间在最近7天内
        alert_days_ago = random.randint(0, 7)
        alert_time = (now - timedelta(days=alert_days_ago, 
                                     hours=random.randint(0, 23),
                                     minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        
        # 是否已读
        is_read = random.random() > 0.3  # 70%的告警已读
        
        alerts.append({
            'id': i,
            'time': alert_time,
            'type': alert_type,
            'message': message,
            'is_read': is_read,
            'created_at': alert_time
        })
    
    return pd.DataFrame(alerts)

def generate_charging_efficiency_logs(stations_df):
    """生成充电效率记录数据"""
    logs = []
    
    log_id = 1
    # 为每个充电站生成过去7天的效率记录，每天4条
    for _, station in stations_df.iterrows():
        for days_ago in range(7):
            for hour in [6, 12, 18, 23]:  # 每天4个时间点
                # 基于充电站当前效率生成历史效率，加入一些随机波动
                base_efficiency = station['efficiency']
                efficiency = max(50, min(100, base_efficiency + random.uniform(-5, 5)))
                
                # 记录时间
                log_time = (now - timedelta(days=days_ago, hours=now.hour-hour if now.hour > hour else 24+now.hour-hour)).strftime('%Y-%m-%d %H:%M:%S')
                
                logs.append({
                    'id': log_id,
                    'station_id': station['id'],
                    'efficiency': round(efficiency, 2),
                    'timestamp': log_time
                })
                
                log_id += 1
    
    return pd.DataFrame(logs)

def generate_system_settings():
    """生成系统设置数据"""
    settings = [
        {
            'id': 1,
            'setting_key': 'system_name',
            'setting_value': '货仓机器人激光充电和能效管理云平台',
            'description': '系统名称，显示在界面顶部',
            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 2,
            'setting_key': 'mqtt_server',
            'setting_value': 'localhost',
            'description': 'MQTT服务器地址，用于与充电站和机器人通信',
            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 3,
            'setting_key': 'mqtt_port',
            'setting_value': '1883',
            'description': 'MQTT服务器端口，标准端口为1883',
            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 4,
            'setting_key': 'refresh_interval',
            'setting_value': '5',
            'description': '数据刷新间隔（秒），控制前端自动刷新数据的频率',
            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        },
        {
            'id': 5,
            'setting_key': 'alert_threshold',
            'setting_value': '20',
            'description': '告警阈值（百分比），当充电效率低于此值时触发告警',
            'updated_at': now.strftime('%Y-%m-%d %H:%M:%S')
        }
    ]
    
    return pd.DataFrame(settings)

def generate_system_logs(users_df):
    """生成系统日志数据"""
    logs = []
    
    # 日志动作模板
    actions = [
        '登录系统',
        '添加充电站',
        '编辑充电站 #{}',
        '删除充电站 #{}',
        '查看机器人列表',
        '查看订单详情 #{}',
        '修改系统设置',
        '导出报表',
        '重启服务',
        '备份数据库'
    ]
    
    # 生成50条日志记录
    for i in range(1, 51):
        # 随机选择用户，有10%的日志是系统自动生成的（无用户）
        if random.random() > 0.1:
            user = users_df.iloc[random.randint(0, len(users_df)-1)]
            user_id = user['id']
        else:
            user_id = None
        
        # 随机选择一个动作
        action_template = random.choice(actions)
        if '{}' in action_template:
            if '充电站' in action_template:
                action = action_template.format(random.randint(1, 12))
            else:  # 订单
                action = action_template.format(random.randint(1, 100))
        else:
            action = action_template
        
        # 随机生成详细信息
        if action == '登录系统':
            details = f"IP地址: {fake.ipv4()}"
        elif '添加' in action or '编辑' in action:
            details = f"操作时间: {fake.date_time_this_month().strftime('%Y-%m-%d %H:%M:%S')}"
        elif '删除' in action:
            details = f"永久删除记录"
        elif '系统设置' in action:
            details = f"修改了 {random.choice(['mqtt_server', 'refresh_interval', 'alert_threshold'])}"
        else:
            details = None
        
        # 日志时间在最近30天内
        log_days_ago = random.randint(0, 30)
        created_at = (now - timedelta(days=log_days_ago, 
                                     hours=random.randint(0, 23),
                                     minutes=random.randint(0, 59))).strftime('%Y-%m-%d %H:%M:%S')
        
        logs.append({
            'id': i,
            'user_id': user_id,
            'action': action,
            'details': details,
            'created_at': created_at
        })
    
    return pd.DataFrame(logs)

def main():
    """主函数，生成所有数据并保存为Excel文件"""
    print("开始生成模拟数据...")
    
    # 生成各表数据
    users_df = generate_users()
    stations_df = generate_charging_stations()
    robots_df = generate_robots()
    orders_df = generate_charging_orders(robots_df, stations_df)
    alerts_df = generate_system_alerts()
    efficiency_logs_df = generate_charging_efficiency_logs(stations_df)
    settings_df = generate_system_settings()
    system_logs_df = generate_system_logs(users_df)
    
    # 创建Excel写入器
    excel_path = 'data/charging_system_data.xlsx'
    with pd.ExcelWriter(excel_path) as writer:
        users_df.to_excel(writer, sheet_name='users', index=False)
        stations_df.to_excel(writer, sheet_name='charging_stations', index=False)
        robots_df.to_excel(writer, sheet_name='robots', index=False)
        orders_df.to_excel(writer, sheet_name='charging_orders', index=False)
        alerts_df.to_excel(writer, sheet_name='system_alerts', index=False)
        efficiency_logs_df.to_excel(writer, sheet_name='efficiency_logs', index=False)
        settings_df.to_excel(writer, sheet_name='system_settings', index=False)
        system_logs_df.to_excel(writer, sheet_name='system_logs', index=False)
    
    print(f"模拟数据已生成并保存至: {os.path.abspath(excel_path)}")
    print(f"生成数据统计:")
    print(f"- 用户: {len(users_df)} 条记录")
    print(f"- 充电站: {len(stations_df)} 条记录")
    print(f"- 机器人: {len(robots_df)} 条记录")
    print(f"- 充电订单: {len(orders_df)} 条记录")
    print(f"- 系统告警: {len(alerts_df)} 条记录")
    print(f"- 效率日志: {len(efficiency_logs_df)} 条记录")
    print(f"- 系统设置: {len(settings_df)} 条记录")
    print(f"- 系统日志: {len(system_logs_df)} 条记录")

if __name__ == "__main__":
    main() 