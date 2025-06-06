import os
from datetime import datetime
import bcrypt
import sys
import traceback
from flask import current_app
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker
import random

# 导入模型
from .models import User, ChargingStation, Robot, ChargingOrder, SystemAlert, EfficiencyLog, SystemSetting, SystemLog
from . import db

# 缓存数据，避免频繁查询数据库
_data_cache = {}
_cache_timeout = 60  # 缓存过期时间（秒）
_last_cache_time = {}  # 记录每种数据的最后缓存时间

def clear_cache():
    """清除数据缓存"""
    global _data_cache
    _data_cache = {}
    print("数据缓存已清除")

def _get_db_session():
    """获取数据库会话"""
    return db.session

def _to_dict(obj):
    """将SQLAlchemy对象转换为字典"""
    if obj is None:
        return None
    
    result = {}
    for column in obj.__table__.columns:
        value = getattr(obj, column.name)
        # 处理日期时间类型，转换为字符串
        if isinstance(value, datetime):
            value = value.strftime('%Y-%m-%d %H:%M:%S')
        result[column.name] = value
    
    return result

# 用户相关数据访问函数
def get_users():
    """获取所有用户"""
    try:
        session = _get_db_session()
        users = session.query(User).all()
        return [_to_dict(user) for user in users]
    except Exception as e:
        print(f"获取用户数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

def get_user_by_id(user_id):
    """根据ID获取用户"""
    try:
        session = _get_db_session()
        user = session.query(User).filter_by(id=user_id).first()
        return _to_dict(user)
    except Exception as e:
        print(f"根据ID获取用户时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

def get_user_by_username(username):
    """根据用户名获取用户"""
    try:
        session = _get_db_session()
        user = session.query(User).filter_by(username=username).first()
        return _to_dict(user)
    except Exception as e:
        print(f"根据用户名获取用户时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

def check_password(user, password):
    """检查密码是否正确"""
    if not user:
        return False
    
    # 从数据库中获取用户对象
    try:
        session = _get_db_session()
        db_user = session.query(User).filter_by(id=user['id']).first()
        
        if db_user:
            # 使用User模型的check_password方法验证密码
            return db_user.check_password(password)
        else:
            return False
    except Exception as e:
        print(f"密码验证错误: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        # 开发环境下，可以临时允许任何密码
        return True

# 充电站相关数据访问函数
def get_charging_stations():
    """获取所有充电站"""
    try:
        session = _get_db_session()
        stations = session.query(ChargingStation).all()
        result = [_to_dict(station) for station in stations]
        
        # 转换字段名称以匹配API期望
        for station in result:
            if 'power_output' in station:
                station['power_rating'] = station['power_output']
        
        return result
    except Exception as e:
        print(f"获取充电站数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

def get_station_by_id(station_id):
    """根据ID获取充电站"""
    try:
        session = _get_db_session()
        station = session.query(ChargingStation).filter_by(id=station_id).first()
        result = _to_dict(station)
        
        # 转换字段名称以匹配API期望
        if result and 'power_output' in result:
            result['power_rating'] = result['power_output']
        
        return result
    except Exception as e:
        print(f"根据ID获取充电站时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

def add_charging_station(station_data):
    """添加新的充电站"""
    try:
        session = _get_db_session()
        
        # 处理功率值
        power_rating = 0
        if 'power_rating' in station_data:
            try:
                power_rating = float(station_data.get('power_rating', 0))
            except (ValueError, TypeError):
                power_rating = 0
        
        # 创建新的充电站记录
        new_station = ChargingStation(
            name=station_data.get('name', '新充电站'),
            location=station_data.get('location', '未知位置'),
            status=station_data.get('status', 'idle'),
            power_output=power_rating,
            efficiency=station_data.get('efficiency', 80),
            power_rating=power_rating
        )
        
        # 添加到数据库
        session.add(new_station)
        session.commit()
        
        # 返回新创建的充电站
        return _to_dict(new_station)
    except Exception as e:
        session.rollback()
        print(f"添加充电站时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return None

def update_charging_station(station_id, station_data):
    """更新充电站信息"""
    try:
        session = _get_db_session()
        
        # 查找要更新的充电站
        station = session.query(ChargingStation).filter_by(id=station_id).first()
        if not station:
            print(f"未找到ID为{station_id}的充电站")
            return None
        
        # 处理功率值
        if 'power_rating' in station_data:
            try:
                power_rating = float(station_data.get('power_rating', 0))
                station_data['power_rating'] = power_rating
                station_data['power_output'] = power_rating  # 同时更新power_output字段
            except (ValueError, TypeError):
                # 如果转换失败，保留原值
                power_rating = station.power_rating or 0
                station_data['power_rating'] = power_rating
                station_data['power_output'] = power_rating
        
        # 更新字段
        for key, value in station_data.items():
            if key != 'id' and hasattr(station, key):  # 不允许更新ID，且属性必须存在
                setattr(station, key, value)
        
        # 保存到数据库
        session.commit()
        
        return _to_dict(station)
    except Exception as e:
        session.rollback()
        print(f"更新充电站时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return None

def delete_charging_station(station_id):
    """删除充电站"""
    try:
        session = _get_db_session()
        
        # 查找要删除的充电站
        station = session.query(ChargingStation).filter_by(id=station_id).first()
        if not station:
            print(f"未找到ID为{station_id}的充电站")
            return False
        
        # 删除充电站
        session.delete(station)
        session.commit()
        
        return True
    except Exception as e:
        session.rollback()
        print(f"删除充电站时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return False

# 机器人相关数据访问函数
def get_robots():
    """获取所有机器人"""
    try:
        session = _get_db_session()
        robots = session.query(Robot).all()
        return [_to_dict(robot) for robot in robots]
    except Exception as e:
        print(f"获取机器人数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

def get_robot_by_id(robot_id):
    """根据ID获取机器人"""
    try:
        session = _get_db_session()
        robot = session.query(Robot).filter_by(id=robot_id).first()
        return _to_dict(robot)
    except Exception as e:
        print(f"根据ID获取机器人时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

# 订单相关数据访问函数
def get_charging_orders():
    """获取所有充电订单"""
    try:
        session = _get_db_session()
        orders = session.query(ChargingOrder).all()
        result = [_to_dict(order) for order in orders]
        
        # 转换字段名称以匹配API期望
        for order in result:
            if 'charge_amount' in order:
                order['amount'] = order['charge_amount']
        
        return result
    except Exception as e:
        print(f"获取充电订单数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

def get_order_by_id(order_id):
    """根据ID获取订单"""
    try:
        session = _get_db_session()
        order = session.query(ChargingOrder).filter_by(id=order_id).first()
        result = _to_dict(order)
        
        # 转换字段名称以匹配API期望
        if result and 'charge_amount' in result:
            result['amount'] = result['charge_amount']
        
        return result
    except Exception as e:
        print(f"根据ID获取订单时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

# 系统告警相关数据访问函数
def get_system_alerts():
    """获取所有系统告警"""
    try:
        session = _get_db_session()
        alerts = session.query(SystemAlert).all()
        return [_to_dict(alert) for alert in alerts]
    except Exception as e:
        print(f"获取系统告警数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

# 充电效率记录相关数据访问函数
def get_charging_efficiency_logs():
    """获取所有充电效率记录"""
    try:
        session = _get_db_session()
        logs = session.query(EfficiencyLog).all()
        return [_to_dict(log) for log in logs]
    except Exception as e:
        print(f"获取充电效率记录数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

# 系统设置相关数据访问函数
def get_system_settings():
    """获取所有系统设置"""
    try:
        session = _get_db_session()
        settings = session.query(SystemSetting).all()
        return [_to_dict(setting) for setting in settings]
    except Exception as e:
        print(f"获取系统设置数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

def get_setting_by_key(key):
    """根据键名获取系统设置"""
    try:
        session = _get_db_session()
        setting = session.query(SystemSetting).filter_by(setting_key=key).first()
        return _to_dict(setting)
    except Exception as e:
        print(f"根据键名获取系统设置时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    return None

# 系统日志相关数据访问函数
def get_system_logs():
    """获取所有系统日志"""
    try:
        session = _get_db_session()
        logs = session.query(SystemLog).all()
        return [_to_dict(log) for log in logs]
    except Exception as e:
        print(f"获取系统日志数据时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

# 新增：检查低电量机器人并自动充电
def check_low_battery_robots():
    """检查低电量机器人并自动安排充电"""
    try:
        session = _get_db_session()
        
        # 查找电量低于20%的空闲机器人
        low_battery_robots = session.query(Robot).filter(
            Robot.battery_level < 20,
            Robot.status == 'idle'
        ).all()
        
        results = []
        
        for robot in low_battery_robots:
            # 如果机器人已经分配了充电桩
            if robot.station_id:
                station = session.query(ChargingStation).filter_by(id=robot.station_id).first()
                
                # 如果充电桩存在且空闲
                if station and station.status == 'idle':
                    # 开始充电
                    robot.status = 'charging'
                    station.status = 'charging'
                    
                    # 创建充电订单
                    now = datetime.utcnow()
                    order = ChargingOrder(
                        robot_id=robot.id,
                        station_id=station.id,
                        start_time=now,
                        status='charging'
                    )
                    
                    session.add(order)
                    results.append({
                        'robot_id': robot.id,
                        'robot_name': robot.name,
                        'station_id': station.id,
                        'station_name': station.name,
                        'action': 'start_charging',
                        'message': f"机器人 {robot.name} 开始在充电桩 {station.name} 充电"
                    })
            else:
                # 查找空闲的充电桩
                idle_station = session.query(ChargingStation).filter_by(status='idle').first()
                
                if idle_station:
                    # 分配充电桩并开始充电
                    robot.station_id = idle_station.id
                    robot.status = 'charging'
                    idle_station.status = 'charging'
                    
                    # 创建充电订单
                    now = datetime.utcnow()
                    order = ChargingOrder(
                        robot_id=robot.id,
                        station_id=idle_station.id,
                        start_time=now,
                        status='charging'
                    )
                    
                    session.add(order)
                    results.append({
                        'robot_id': robot.id,
                        'robot_name': robot.name,
                        'station_id': idle_station.id,
                        'station_name': idle_station.name,
                        'action': 'assign_and_start_charging',
                        'message': f"机器人 {robot.name} 被分配到充电桩 {idle_station.name} 并开始充电"
                    })
                else:
                    results.append({
                        'robot_id': robot.id,
                        'robot_name': robot.name,
                        'action': 'no_idle_station',
                        'message': f"机器人 {robot.name} 电量低但没有空闲充电桩"
                    })
        
        # 检查正在充电且电量已满的机器人，自动完成充电
        charging_robots = session.query(Robot).filter_by(status='charging').all()
        for robot in charging_robots:
            # 模拟充电进度，实际应用中可能需要更复杂的逻辑
            # 这里简单地随机增加电量，如果超过95%就认为充满了
            robot.battery_level += random.uniform(5, 15)  # 每次检查增加5-15%的电量
            
            if robot.battery_level >= 100:
                robot.battery_level = 100
                robot.status = 'idle'
                robot.last_charging = datetime.utcnow()
                
                # 找到对应的充电桩并释放
                if robot.station_id:
                    station = session.query(ChargingStation).filter_by(id=robot.station_id).first()
                    if station:
                        station.status = 'idle'
                
                # 找到未完成的充电订单并标记为完成
                order = session.query(ChargingOrder).filter_by(
                    robot_id=robot.id,
                    status='charging'
                ).order_by(ChargingOrder.start_time.desc()).first()
                
                if order:
                    order.status = 'completed'
                    order.end_time = datetime.utcnow()
                    # 计算充电量和充电效率
                    hours = (order.end_time - order.start_time).total_seconds() / 3600
                    station_power = 10  # 默认功率
                    if station:
                        station_power = station.power_output if hasattr(station, 'power_output') else station.power_rating
                    
                    order.charge_amount = station_power * hours * 0.9  # 假设90%的效率
                    order.charging_efficiency = 90  # 默认效率
                
                results.append({
                    'robot_id': robot.id,
                    'robot_name': robot.name,
                    'action': 'charging_completed',
                    'message': f"机器人 {robot.name} 充电完成，电量已满"
                })
        
        session.commit()
        return results
    except Exception as e:
        session.rollback()
        print(f"检查低电量机器人时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return []

# 新增：将机器人分配到充电桩
def assign_robot_to_station(robot_id, station_id):
    """将机器人分配到充电桩"""
    try:
        session = _get_db_session()
        
        print(f"开始分配机器人 {robot_id} 到充电桩 {station_id}")
        
        # 获取机器人和充电桩
        robot = session.query(Robot).filter_by(id=robot_id).first()
        station = session.query(ChargingStation).filter_by(id=station_id).first()
        
        # 验证机器人和充电桩是否存在
        if not robot:
            print(f"错误：机器人ID {robot_id} 不存在")
            return False, f"机器人ID {robot_id} 不存在"
        
        if not station:
            print(f"错误：充电桩ID {station_id} 不存在")
            return False, f"充电桩ID {station_id} 不存在"
        
        print(f"找到机器人：{robot.name}，状态：{robot.status}")
        print(f"找到充电桩：{station.name}，状态：{station.status}")
        
        # 验证充电桩是否空闲
        if station.status != 'idle':
            print(f"错误：充电桩 {station.name} 不是空闲状态，当前状态: {station.status}")
            return False, f"充电桩 {station.name} 不是空闲状态，当前状态: {station.status}"
        
        # 检查是否有其他机器人正在使用该充电桩
        other_robot = session.query(Robot).filter(Robot.station_id == station_id, Robot.id != robot_id).first()
        if other_robot:
            print(f"错误：充电桩 {station.name} 已被机器人 {other_robot.name} 占用")
            return False, f"充电桩 {station.name} 已被机器人 {other_robot.name} 占用"
        
        # 如果机器人之前分配了其他充电桩，先解除关联
        if robot.station_id and robot.station_id != station_id:
            print(f"机器人 {robot.name} 之前分配了充电桩ID {robot.station_id}，现在解除关联")
            old_station = session.query(ChargingStation).filter_by(id=robot.station_id).first()
            if old_station:
                print(f"找到旧充电桩：{old_station.name}，状态：{old_station.status}")
                if old_station.status == 'charging':
                    old_station.status = 'idle'
                    print(f"将旧充电桩 {old_station.name} 状态设置为空闲")
        
        # 更新机器人的充电桩ID和状态
        robot.station_id = station_id
        robot.status = 'charging'  # 始终将状态设为充电中
        station.status = 'charging'  # 更新充电桩状态为充电中
        
        print(f"已更新机器人 {robot.name} 状态为充电中，关联到充电桩 {station.name}")
        
        # 创建充电订单
        now = datetime.utcnow()
        order = ChargingOrder(
            robot_id=robot_id,
            station_id=station_id,
            start_time=now,
            status='charging'
        )
        session.add(order)
        print(f"已创建充电订单，订单ID: {order.id if hasattr(order, 'id') else '未知'}")
        
        session.commit()
        print(f"成功提交事务，机器人 {robot.name} 已分配到充电桩 {station.name}")
        return True, f"机器人 {robot.name} 已分配到充电桩 {station.name} 并开始充电"
            
    except Exception as e:
        session.rollback()
        print(f"分配机器人到充电桩出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return False, f"服务器错误: {str(e)}"

# 新增：解除机器人与充电桩的关联
def release_robot_from_station(robot_id):
    """解除机器人与充电桩的关联"""
    try:
        session = _get_db_session()
        
        # 获取机器人
        robot = session.query(Robot).filter_by(id=robot_id).first()
        
        # 验证机器人是否存在
        if not robot:
            return False, f"机器人ID {robot_id} 不存在"
        
        # 验证机器人是否关联了充电桩
        if not robot.station_id:
            return False, f"机器人 {robot.name} 未关联任何充电桩"
        
        # 获取关联的充电桩
        station = session.query(ChargingStation).filter_by(id=robot.station_id).first()
        
        # 解除关联
        old_station_id = robot.station_id
        old_station_name = station.name if station else f"充电桩 {old_station_id}"
        
        robot.station_id = None
        robot.status = 'idle'  # 更新机器人状态为空闲
        
        # 更新充电桩状态
        if station:
            station.status = 'idle'
        
        # 查找未完成的充电订单并标记为完成
        order = session.query(ChargingOrder).filter_by(
            robot_id=robot.id,
            status='charging'
        ).order_by(ChargingOrder.start_time.desc()).first()
        
        if order:
            order.status = 'completed'
            order.end_time = datetime.utcnow()
            # 计算充电量和充电效率
            hours = (order.end_time - order.start_time).total_seconds() / 3600
            station_power = 10  # 默认功率
            if station:
                station_power = station.power_output if hasattr(station, 'power_output') else station.power_rating
            
            order.charge_amount = station_power * hours * 0.9  # 假设90%的效率
            order.charging_efficiency = 90  # 默认效率
        
        # 更新机器人的最后充电时间
        robot.last_charging = datetime.utcnow()
        
        session.commit()
        return True, f"机器人 {robot.name} 已与充电桩 {old_station_name} 解除关联"
            
    except Exception as e:
        session.rollback()
        print(f"解除机器人与充电桩关联时出错: {str(e)}")
        traceback.print_exc(file=sys.stdout)
        return False, f"服务器错误: {str(e)}"

# 初始化时打印连接信息
def print_connection_info():
    """打印数据库连接信息"""
    try:
        print("数据访问模块已初始化，使用MySQL数据库连接")
        print(f"数据库URI: {current_app.config['SQLALCHEMY_DATABASE_URI'] if current_app else '未设置'}")
    except Exception as e:
        print(f"打印数据库连接信息时出错: {e}")

print("数据访问模块已加载，使用MySQL数据库连接") 