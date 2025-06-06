from flask import Blueprint, request, jsonify, render_template_string, current_app, send_from_directory
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from datetime import datetime, timedelta
from . import data_access
import os
from pathlib import Path

# 创建蓝图
auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('users', __name__)
station_bp = Blueprint('stations', __name__)
order_bp = Blueprint('orders', __name__)
system_bp = Blueprint('system', __name__)
robot_bp = Blueprint('robots', __name__)  # 机器人蓝图
energy_efficiency_bp = Blueprint('energy_efficiency', __name__)  # 能效分析蓝图

# 认证相关路由
@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    print(f"接收到的登录请求数据: {data}")
    username = data.get('username')
    password = data.get('password')

    user = data_access.get_user_by_username(username)
    print(f"从数据库查找用户: {user}")

    if user and data_access.check_password(user, password):
        print("密码验证成功")
        # 确保用户ID是字符串类型
        user_id = str(user['id'])
        print(f"创建令牌，用户ID: {user_id}, 类型: {type(user_id)}")
        
        # 创建JWT令牌，使用额外参数
        access_token = create_access_token(
            identity=user_id,
            additional_claims={
                'username': user['username'],
                'role': user['role']
            }
        )
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'role': user['role']
            }
        })

    print("密码验证失败")
    return jsonify({'error': 'Invalid credentials'}), 401

@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    """获取当前登录用户信息"""
    user_id = get_jwt_identity()
    # 确保用户ID是整数类型，因为数据库中存储的是整数ID
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        return jsonify({'error': '无效的用户ID'}), 401
        
    user = data_access.get_user_by_id(user_id)
    
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    return jsonify({
        'id': user['id'],
        'username': user['username'],
        'role': user['role']
    })

# 添加登录页面路由 (GET)
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>登录 - 充电桩管理系统</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
                .login-container { max-width: 400px; margin: 100px auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                h1 { text-align: center; color: #333; }
                .form-group { margin-bottom: 15px; }
                label { display: block; margin-bottom: 5px; color: #666; }
                input { width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
                button { width: 100%; padding: 10px; background: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
                button:hover { background: #45a049; }
                .error { color: red; margin-top: 10px; text-align: center; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h1>充电桩管理系统</h1>
                <form id="loginForm">
                    <div class="form-group">
                        <label for="username">用户名：</label>
                        <input type="text" id="username" name="username" required>
                    </div>
                    <div class="form-group">
                        <label for="password">密码：</label>
                        <input type="password" id="password" name="password" required>
                    </div>
                    <button type="submit">登录</button>
                    <div id="error" class="error"></div>
                </form>
            </div>
            <script>
                document.getElementById('loginForm').onsubmit = async (e) => {
                    e.preventDefault();
                    const username = document.getElementById('username').value;
                    const password = document.getElementById('password').value;
                    
                    try {
                        const response = await fetch('/api/auth/login', {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({ username, password })
                        });
                        
                        const data = await response.json();
                        
                        if (response.ok) {
                            // 登录成功，保存 token
                            localStorage.setItem('token', data.access_token);
                            // 跳转到首页
                            window.location.href = '/'; // 或者其他首页路由
                        } else {
                            // 显示错误信息
                            document.getElementById('error').textContent = data.error || '登录失败';
                        }
                    } catch (error) {
                        document.getElementById('error').textContent = '网络错误，请重试';
                    }
                };
            </script>
        </body>
        </html>
    ''')

# 用户管理路由
@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_users():
    users = data_access.get_users()
    return jsonify([{
        'id': user['id'],
        'username': user['username'],
        'role': user['role'],
        'created_at': user['created_at']
    } for user in users])

@user_bp.route('/', methods=['POST'])
@jwt_required()
def create_user():
    # 在实际应用中，这里应该将新用户添加到数据库中
    # 但为了简化示例，我们只返回成功消息
    return jsonify({'message': 'User created successfully (Demo Mode)'})

# 充电桩管理路由 - 移除JWT认证以便测试
@station_bp.route('/', methods=['GET'], strict_slashes=False)
def get_stations():
    try:
        stations = data_access.get_charging_stations()
        print(f"获取到的充电站数据: {len(stations)} 条")
        result = [{
            'id': station['id'],
            'name': station['name'],
            'location': station['location'],
            'status': station['status'],
            'power_rating': station.get('power_rating', station.get('power_output', 0)),
            'efficiency': station.get('efficiency', 100)
        } for station in stations]
        return jsonify(result)
    except Exception as e:
        print(f"获取充电站数据出错: {str(e)}")
        # 返回空数组而不是错误对象
        return jsonify([])

@station_bp.route('/', methods=['POST'], strict_slashes=False)
# 暂时注释掉JWT认证，方便测试
# @jwt_required()
def create_station():
    """添加新的充电站"""
    try:
        # 检查用户角色 - 暂时注释掉，方便测试
        # user_id = get_jwt_identity()
        # # 确保用户ID是整数类型
        # try:
        #     user_id = int(user_id)
        # except (ValueError, TypeError):
        #     return jsonify({'error': '无效的用户ID'}), 401
            
        # user = data_access.get_user_by_id(user_id)
        
        # if not user or user['role'] != 'admin':
        #     return jsonify({'error': '无权限执行此操作'}), 403
            
        # 获取请求数据
        data = request.get_json()
        print(f"接收到添加充电站请求: {data}")
        
        # 验证必要字段
        if not data or not isinstance(data, dict):
            print("请求数据无效")
            return jsonify({'error': '请求数据无效'}), 400
        
        # 验证必填字段
        required_fields = ['name', 'location']
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        
        if missing_fields:
            error_msg = f"缺少必填字段: {', '.join(missing_fields)}"
            print(error_msg)
            return jsonify({'error': error_msg}), 422
            
        # 验证数值字段
        if 'power_rating' in data:
            try:
                data['power_rating'] = float(data['power_rating'])
            except (ValueError, TypeError):
                print("功率值无效")
                return jsonify({'error': '功率值必须是有效的数字'}), 422
                
        if 'efficiency' in data:
            try:
                data['efficiency'] = float(data['efficiency'])
                if data['efficiency'] < 0 or data['efficiency'] > 100:
                    raise ValueError("效率值必须在0-100之间")
            except (ValueError, TypeError) as e:
                print(f"效率值无效: {str(e)}")
                return jsonify({'error': '效率值必须是0-100之间的有效数字'}), 422
        
        # 调用数据访问函数添加充电站
        new_station = data_access.add_charging_station(data)
        
        if new_station:
            print(f"成功添加充电站: {new_station}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify(new_station), 201
        else:
            print("添加充电站失败")
            return jsonify({'error': '添加充电站失败，可能是数据存储问题'}), 500
    except Exception as e:
        print(f"添加充电站出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@station_bp.route('/<int:station_id>/', methods=['PUT'], strict_slashes=False)
@station_bp.route('/<int:station_id>', methods=['PUT'], strict_slashes=False)
@jwt_required()
def update_station(station_id):
    """更新充电站信息"""
    try:
        # 检查用户角色
        user_id = get_jwt_identity()
        # 确保用户ID是整数类型
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 401
            
        user = data_access.get_user_by_id(user_id)
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
            
        # 获取请求数据
        data = request.get_json()
        print(f"接收到更新充电站请求: ID={station_id}, 数据={data}")
        
        # 验证必要字段
        if not data or not isinstance(data, dict):
            print("请求数据无效")
            return jsonify({'error': '请求数据无效'}), 400
        
        # 调用数据访问函数更新充电站
        updated_station = data_access.update_charging_station(station_id, data)
        
        if updated_station:
            print(f"成功更新充电站: {updated_station}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify(updated_station)
        else:
            print(f"更新充电站失败: ID={station_id}")
            return jsonify({'error': '更新充电站失败，可能未找到指定ID的充电站'}), 404
    except Exception as e:
        print(f"更新充电站出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

@station_bp.route('/<int:station_id>/', methods=['DELETE'], strict_slashes=False)
@station_bp.route('/<int:station_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required()
def delete_station(station_id):
    """删除充电站"""
    try:
        # 检查用户角色
        user_id = get_jwt_identity()
        # 确保用户ID是整数类型
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            return jsonify({'error': '无效的用户ID'}), 401
            
        user = data_access.get_user_by_id(user_id)
        
        if not user or user['role'] != 'admin':
            return jsonify({'error': '无权限执行此操作'}), 403
            
        print(f"接收到删除充电站请求: ID={station_id}")
        
        # 调用数据访问函数删除充电站
        success = data_access.delete_charging_station(station_id)
        
        if success:
            print(f"成功删除充电站: ID={station_id}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify({'message': f'成功删除充电站: ID={station_id}'})
        else:
            print(f"删除充电站失败: ID={station_id}")
            return jsonify({'error': '删除充电站失败，可能未找到指定ID的充电站'}), 404
    except Exception as e:
        print(f"删除充电站出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 机器人管理路由 - 移除JWT认证以便测试
@robot_bp.route('/', methods=['GET'])
def get_robots():
    try:
        robots = data_access.get_robots()
        print(f"获取到的机器人数据: {len(robots)} 条")
        print(f"机器人数据类型: {type(robots)}")
        
        # 确保robots是列表
        if not isinstance(robots, list):
            print(f"警告: 机器人数据不是列表，而是 {type(robots)}")
            robots = []
        
        result = []
        for robot in robots:
            try:
                robot_item = {
                    'id': robot['id'],
                    'name': robot['name'],
                    'battery_level': robot['battery_level'],
                    'status': robot['status'],
                    'last_charging': robot.get('last_charging', None),
                    'station_id': robot.get('station_id', None)  # 添加充电桩ID字段
                }
                result.append(robot_item)
            except Exception as e:
                print(f"处理机器人数据时出错: {str(e)}, 机器人数据: {robot}")
        
        print(f"处理后的机器人数据: {len(result)} 条")
        
        # 明确设置响应的内容类型
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"获取机器人数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 返回空数组而不是错误对象
        response = jsonify([])
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

# 新增：更新机器人信息
@robot_bp.route('/<int:robot_id>', methods=['PUT'])
def update_robot(robot_id):
    """更新机器人信息"""
    try:
        # 获取请求数据
        data = request.get_json()
        print(f"接收到更新机器人请求: ID={robot_id}, 数据={data}")
        
        # 验证必要字段
        if not data or not isinstance(data, dict):
            print("请求数据无效")
            return jsonify({'error': '请求数据无效'}), 400
        
        # 调用数据访问函数更新机器人
        updated_robot = data_access.update_robot(robot_id, data)
        
        if updated_robot:
            print(f"成功更新机器人: {updated_robot}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify(updated_robot)
        else:
            print(f"更新机器人失败: ID={robot_id}")
            return jsonify({'error': '更新机器人失败，可能未找到指定ID的机器人'}), 404
    except Exception as e:
        print(f"更新机器人出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 新增：将机器人分配到充电桩
@robot_bp.route('/<int:robot_id>/assign/<int:station_id>', methods=['POST'])
def assign_robot_to_station(robot_id, station_id):
    """将机器人分配到充电桩"""
    try:
        print(f"接收到分配机器人请求: 机器人ID={robot_id}, 充电桩ID={station_id}")
        
        # 调用数据访问函数分配机器人到充电桩
        success, message = data_access.assign_robot_to_station(robot_id, station_id)
        
        if success:
            print(f"成功分配机器人: {message}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify({'message': message})
        else:
            print(f"分配机器人失败: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"分配机器人出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 新增：开始充电
@robot_bp.route('/<int:robot_id>/start-charging', methods=['POST'])
def start_charging(robot_id):
    """开始给机器人充电"""
    try:
        print(f"接收到开始充电请求: 机器人ID={robot_id}")
        
        # 调用数据访问函数开始充电
        success, message = data_access.start_charging(robot_id)
        
        if success:
            print(f"成功开始充电: {message}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify({'message': message})
        else:
            print(f"开始充电失败: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"开始充电出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 新增：完成充电
@robot_bp.route('/<int:robot_id>/complete-charging', methods=['POST'])
def complete_charging(robot_id):
    """完成机器人充电"""
    try:
        print(f"接收到完成充电请求: 机器人ID={robot_id}")
        
        # 调用数据访问函数完成充电
        success, message = data_access.complete_charging(robot_id)
        
        if success:
            print(f"成功完成充电: {message}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify({'message': message})
        else:
            print(f"完成充电失败: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"完成充电出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 新增：检查低电量机器人并自动充电
@robot_bp.route('/check-low-battery', methods=['GET'])
def check_low_battery_robots():
    """检查低电量机器人并自动安排充电"""
    try:
        print("接收到检查低电量机器人请求")
        
        # 调用数据访问函数检查低电量机器人
        results = data_access.check_low_battery_robots()
        
        print(f"检查结果: {len(results)} 条记录")
        # 清除缓存，确保下次获取最新数据
        data_access.clear_cache()
        return jsonify(results)
    except Exception as e:
        print(f"检查低电量机器人出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500

# 订单管理路由 - 移除JWT认证以便测试
@order_bp.route('/', methods=['GET'])
def get_orders():
    try:
        orders = data_access.get_charging_orders()
        print(f"获取到的订单数据: {len(orders)} 条")
        
        result = []
        for order in orders:
            try:
                order_item = {
                    'id': order['id'],
                    'robot_id': order['robot_id'],
                    'station_id': order['station_id'],
                    'start_time': order['start_time'],
                    'status': order['status']
                }
                
                # 处理可能的NaN值
                if 'end_time' in order and order['end_time'] is not None:
                    order_item['end_time'] = order['end_time']
                else:
                    order_item['end_time'] = None
                
                # 处理金额，避免NaN值
                amount = order.get('amount', order.get('charge_amount', None))
                if amount is not None and not isinstance(amount, str):
                    try:
                        float(amount)  # 尝试转换为浮点数，检查是否是NaN
                        order_item['amount'] = amount
                    except (ValueError, TypeError):
                        order_item['amount'] = None
                else:
                    order_item['amount'] = amount
                    
                result.append(order_item)
            except Exception as e:
                print(f"处理订单数据时出错: {str(e)}, 订单数据: {order}")
        
        print(f"处理后的订单数据: {len(result)} 条")
        
        # 明确设置响应的内容类型
        response = jsonify(result)
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response
    except Exception as e:
        print(f"获取订单数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 返回空数组而不是错误对象
        response = jsonify([])
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response

@order_bp.route('/', methods=['POST'])
@jwt_required()
def create_order():
    # 在实际应用中，这里应该将新订单添加到数据库中
    # 但为了简化示例，我们只返回成功消息
    return jsonify({'message': 'Order created successfully (Demo Mode)'})

# 系统管理路由
@system_bp.route('/logs', methods=['GET'])
@jwt_required()
def get_logs():
    logs = data_access.get_system_logs()
    return jsonify([{
        'id': log['id'],
        'user_id': log['user_id'],
        'action': log['action'],
        'details': log.get('details', None),
        'created_at': log['created_at']
    } for log in logs])

@system_bp.route('/alerts', methods=['GET'])
def get_alerts():
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 7, type=int)
        
        # 获取所有告警
        alerts = data_access.get_system_alerts()
        
        # 按时间倒序排序
        alerts = sorted(alerts, key=lambda x: x['time'], reverse=True)
        
        # 计算总页数
        total_items = len(alerts)
        total_pages = (total_items + per_page - 1) // per_page  # 向上取整
        
        # 分页
        start_idx = (page - 1) * per_page
        end_idx = min(start_idx + per_page, total_items)
        paged_alerts = alerts[start_idx:end_idx]
        
        # 格式化响应数据
        result = {
            'items': [{
                'id': alert['id'],
                'type': alert['type'],
                'message': alert['message'],
                'created_at': alert['time'],
                'is_read': alert.get('is_read', False)
            } for alert in paged_alerts],
            'pagination': {
                'total_items': total_items,
                'total_pages': total_pages,
                'current_page': page,
                'per_page': per_page
            }
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取系统告警数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'items': [],
            'pagination': {
                'total_items': 0,
                'total_pages': 0,
                'current_page': 1,
                'per_page': 7
            }
        })

@system_bp.route('/settings', methods=['GET'])
@jwt_required()
def get_settings():
    settings = data_access.get_system_settings()
    result = {}
    for setting in settings:
        result[setting['setting_key']] = setting['setting_value']
    return jsonify(result)

@system_bp.route('/efficiency', methods=['GET'])
@jwt_required()
def get_efficiency_logs():
    logs = data_access.get_charging_efficiency_logs()
    return jsonify(logs)

# 仪表盘数据路由 - 移除JWT认证以便测试
@system_bp.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘所需的统计数据"""
    try:
        # 清除缓存以确保获取最新数据
        data_access.clear_cache()
        
        # 获取数据，每个步骤单独处理异常
        try:
            stations = data_access.get_charging_stations()
            print(f"成功获取充电站数据: {len(stations)}个")
        except Exception as e:
            print(f"获取充电站数据出错: {e}")
            stations = []
            
        try:
            robots = data_access.get_robots()
            print(f"成功获取机器人数据: {len(robots)}个")
        except Exception as e:
            print(f"获取机器人数据出错: {e}")
            robots = []
            
        try:
            orders = data_access.get_charging_orders()
            print(f"成功获取订单数据: {len(orders)}个")
        except Exception as e:
            print(f"获取订单数据出错: {e}")
            orders = []
        
        # 计算充电桩统计数据
        total_stations = len(stations)
        online_stations = sum(1 for s in stations if s.get('status') in ['idle', 'charging'])
        offline_stations = total_stations - online_stations
        
        # 计算机器人统计数据
        total_robots = len(robots)
        charging_robots = sum(1 for r in robots if r.get('status') == 'charging')
        waiting_robots = sum(1 for r in robots if r.get('battery_level', 100) < 30 and r.get('status') != 'charging')
        
        # 计算今日充电次数
        today = datetime.now().strftime('%Y-%m-%d')
        today_orders = 0
        for o in orders:
            start_time = o.get('start_time')
            if start_time and isinstance(start_time, str) and start_time.startswith(today):
                today_orders += 1
        
        # 计算同比增长率（模拟数据）
        # 在实际应用中，这应该与昨日数据比较
        order_change_rate = 12  # 示例数据：12%的增长率
        
        # 确定系统状态
        system_status = '正常'
        system_message = '所有系统运行正常'
        
        # 如果有错误状态的充电站或机器人，系统状态为警告
        error_stations = sum(1 for s in stations if s.get('status') == 'error')
        error_robots = sum(1 for r in robots if r.get('status') == 'error')
        
        if error_stations > 0 or error_robots > 0:
            system_status = '警告'
            system_message = f'发现异常: {error_stations}个充电站, {error_robots}个机器人处于错误状态'
        
        result = {
            'stationCount': total_stations,
            'onlineStations': online_stations,
            'offlineStations': offline_stations,
            'robotCount': total_robots,
            'chargingRobots': charging_robots,
            'waitingRobots': waiting_robots,
            'todayOrders': today_orders,
            'orderChangeRate': order_change_rate,
            'systemStatus': system_status,
            'systemMessage': system_message
        }
        
        print(f"获取到的仪表盘数据: {result}")
        return jsonify(result)
    except Exception as e:
        print(f"获取仪表盘数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        # 返回一个默认的仪表盘数据结构
        default_result = {
            'stationCount': 0,
            'onlineStations': 0,
            'offlineStations': 0,
            'robotCount': 0,
            'chargingRobots': 0,
            'waitingRobots': 0,
            'todayOrders': 0,
            'orderChangeRate': 0,
            'systemStatus': '错误',
            'systemMessage': '数据加载失败: ' + str(e)
        }
        return jsonify(default_result)

@system_bp.route('/charging-efficiency', methods=['GET'])
# 移除JWT认证要求，确保前端可以获取数据
# @jwt_required()
def get_charging_efficiency():
    """获取充电效率趋势数据，用于系统概览页面"""
    try:
        # 获取所有充电站
        stations = data_access.get_charging_stations()
        
        # 创建结果列表
        result = []
        
        # 直接使用充电站表中的efficiency字段
        for station in stations:
            result.append({
                'id': station['id'],
                'name': station['name'],
                'efficiency': station.get('efficiency', 90)  # 使用数据库中的efficiency字段
            })
        
        # 按充电站ID排序
        result.sort(key=lambda x: x['id'])
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电效率趋势数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500

# 添加一个测试路由，用于检查Excel数据是否正确加载
@auth_bp.route('/test-data', methods=['GET'])
def test_data():
    try:
        # 检查数据文件是否存在
        import os
        
        # 尝试不同的数据文件路径
        possible_paths = [
            str(Path(__file__).parent.parent.parent / 'data' / 'charging_system_data.xlsx'),
            str(Path(__file__).parent.parent.parent / 'data' / '数据表.xlsx'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data', 'charging_system_data.xlsx'),
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'data', '数据表.xlsx')
        ]
        
        # 记录检查结果
        file_check = {path: os.path.exists(path) for path in possible_paths}
        data_file_exists = any(file_check.values())
        
        # 清空缓存，确保读取最新数据
        data_access.clear_cache()
        
        # 尝试获取各类数据
        try:
            users_count = len(data_access.get_users())
        except Exception as e:
            users_count = f"错误: {str(e)}"
            
        try:
            stations_count = len(data_access.get_charging_stations())
        except Exception as e:
            stations_count = f"错误: {str(e)}"
            
        try:
            robots_count = len(data_access.get_robots())
        except Exception as e:
            robots_count = f"错误: {str(e)}"
            
        try:
            orders_count = len(data_access.get_charging_orders())
        except Exception as e:
            orders_count = f"错误: {str(e)}"
            
        try:
            alerts_count = len(data_access.get_system_alerts())
        except Exception as e:
            alerts_count = f"错误: {str(e)}"
            
        try:
            logs_count = len(data_access.get_system_logs())
        except Exception as e:
            logs_count = f"错误: {str(e)}"
            
        try:
            settings_count = len(data_access.get_system_settings())
        except Exception as e:
            settings_count = f"错误: {str(e)}"
            
        try:
            efficiency_logs_count = len(data_access.get_charging_efficiency_logs())
        except Exception as e:
            efficiency_logs_count = f"错误: {str(e)}"
        
        result = {
            'data_file_exists': data_file_exists,
            'file_check': file_check,
            'excel_path_used': getattr(data_access, 'EXCEL_PATH', 'Unknown'),
            'users_count': users_count,
            'stations_count': stations_count,
            'robots_count': robots_count,
            'orders_count': orders_count,
            'alerts_count': alerts_count,
            'logs_count': logs_count,
            'settings_count': settings_count,
            'efficiency_logs_count': efficiency_logs_count
        }
        
        print(f"测试数据结果: {result}")
        return jsonify(result)
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        print(f"测试数据路由出错: {str(e)}")
        print(error_traceback)
        return jsonify({
            'error': str(e),
            'traceback': error_traceback,
            'success': False
        }), 500

# 添加一个HTML页面用于测试API
@auth_bp.route('/test-api-page', methods=['GET'])
def test_api_page():
    templates_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates')
    return send_from_directory(templates_dir, 'test_api.html')

# 能效分析相关路由
@energy_efficiency_bp.route('/kpi', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/kpi/', methods=['GET', 'OPTIONS'])
def get_kpi_data():
    """获取能效分析KPI指标数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
        
    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 根据筛选条件过滤
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 计算比较期间的数据（前一个相同时间段）
        if start_date and end_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # 计算时间跨度
            delta = end - start
            
            # 前一个相同时间段
            prev_end = start
            prev_start = prev_end - delta
            
            # 获取前一个时间段的订单
            prev_filtered_orders = filter_orders(
                orders, 
                prev_start.isoformat(), 
                prev_end.isoformat(), 
                station_ids, 
                robot_ids
            )
        else:
            prev_filtered_orders = []
        
        # 计算KPI指标
        # 1. 平均充电效率
        current_efficiency_values = []
        for order in filtered_orders:
            if order.get('status') == 'completed':
                # 优先使用订单中的充电效率字段
                if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                    current_efficiency_values.append(order.get('charging_efficiency'))
                # 如果没有充电效率字段，则计算
                elif order.get('charge_amount') and order.get('end_time'):
                    efficiency = (
                        order.get('charge_amount', 0) / 
                        ((parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 3600) / 
                        get_station_power(order.get('station_id')) * 100
                    )
                    current_efficiency_values.append(efficiency)
        
        avg_efficiency = sum(current_efficiency_values) / len(current_efficiency_values) if current_efficiency_values else 0
        
        prev_efficiency_values = []
        for order in prev_filtered_orders:
            if order.get('status') == 'completed':
                # 优先使用订单中的充电效率字段
                if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                    prev_efficiency_values.append(order.get('charging_efficiency'))
                # 如果没有充电效率字段，则计算
                elif order.get('charge_amount') and order.get('end_time'):
                    efficiency = (
                        order.get('charge_amount', 0) / 
                        ((parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 3600) / 
                        get_station_power(order.get('station_id')) * 100
                    )
                    prev_efficiency_values.append(efficiency)
        
        prev_avg_efficiency = sum(prev_efficiency_values) / len(prev_efficiency_values) if prev_efficiency_values else 0
        
        efficiency_change = ((avg_efficiency - prev_avg_efficiency) / prev_avg_efficiency * 100) if prev_avg_efficiency else 0
        
        # 2. 总能耗
        total_energy = sum([order.get('charge_amount', 0) for order in filtered_orders if order.get('status') == 'completed'])
        prev_total_energy = sum([order.get('charge_amount', 0) for order in prev_filtered_orders if order.get('status') == 'completed'])
        
        energy_change = ((total_energy - prev_total_energy) / prev_total_energy * 100) if prev_total_energy else 0
        
        # 3. 充电器利用率
        # 获取充电站数据
        stations = data_access.get_charging_stations()
        
        # 筛选充电站
        if station_ids:
            filtered_stations = [s for s in stations if s['id'] in station_ids]
        else:
            filtered_stations = stations
        
        # 计算总可用时间（站点数 * 时间段小时数）
        if start_date and end_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            hours_in_period = (end - start).total_seconds() / 3600
        else:
            hours_in_period = 24 * 30  # 默认为30天
        
        total_available_hours = len(filtered_stations) * hours_in_period
        
        # 计算充电时间总和
        total_charging_hours = sum([
            (parse_datetime(order.get('end_time', datetime.now().isoformat())) - parse_datetime(order.get('start_time'))).total_seconds() / 3600
            for order in filtered_orders
        ])
        
        utilization = (total_charging_hours / total_available_hours * 100) if total_available_hours else 0
        
        # 计算前一时段的利用率
        prev_total_charging_hours = sum([
            (parse_datetime(order.get('end_time', datetime.now().isoformat())) - parse_datetime(order.get('start_time'))).total_seconds() / 3600
            for order in prev_filtered_orders
        ])
        
        prev_utilization = (prev_total_charging_hours / total_available_hours * 100) if total_available_hours else 0
        utilization_change = ((utilization - prev_utilization) / prev_utilization * 100) if prev_utilization else 0
        
        # 4. 平均等待时间 (这里用订单创建时间到开始充电时间的差值作为等待时间)
        wait_times = [
            (parse_datetime(order.get('start_time')) - parse_datetime(order.get('created_at'))).total_seconds() / 60
            for order in filtered_orders
            if order.get('start_time') and order.get('created_at') and 
            parse_datetime(order.get('start_time')) > parse_datetime(order.get('created_at'))
        ]
        
        avg_wait_time = sum(wait_times) / len(wait_times) if wait_times else 0
        
        prev_wait_times = [
            (parse_datetime(order.get('start_time')) - parse_datetime(order.get('created_at'))).total_seconds() / 60
            for order in prev_filtered_orders
            if order.get('start_time') and order.get('created_at') and 
            parse_datetime(order.get('start_time')) > parse_datetime(order.get('created_at'))
        ]
        
        prev_avg_wait_time = sum(prev_wait_times) / len(prev_wait_times) if prev_wait_times else 0
        wait_time_change = ((avg_wait_time - prev_avg_wait_time) / prev_avg_wait_time * 100) if prev_avg_wait_time else 0
        
        # 5. 充电成功率
        total_orders = len([order for order in filtered_orders if order.get('status') in ['completed', 'failed']])
        successful_orders = len([order for order in filtered_orders if order.get('status') == 'completed'])
        
        success_rate = (successful_orders / total_orders * 100) if total_orders else 0
        
        prev_total_orders = len([order for order in prev_filtered_orders if order.get('status') in ['completed', 'failed']])
        prev_successful_orders = len([order for order in prev_filtered_orders if order.get('status') == 'completed'])
        
        prev_success_rate = (prev_successful_orders / prev_total_orders * 100) if prev_total_orders else 0
        success_rate_change = ((success_rate - prev_success_rate) / prev_success_rate * 100) if prev_success_rate else 0
        
        # 6. 总充电次数
        total_charging_orders = len([order for order in filtered_orders if order.get('status') == 'completed'])
        prev_total_charging_orders = len([order for order in prev_filtered_orders if order.get('status') == 'completed'])
        
        orders_change = ((total_charging_orders - prev_total_charging_orders) / prev_total_charging_orders * 100) if prev_total_charging_orders else 0
        
        # 构建返回数据
        result = {
            'avgEfficiency': avg_efficiency,
            'efficiencyChange': efficiency_change,
            'totalEnergy': total_energy,
            'energyChange': energy_change,
            'utilization': utilization,
            'utilizationChange': utilization_change,
            'avgWaitTime': avg_wait_time,
            'waitTimeChange': wait_time_change,
            'successRate': success_rate,
            'successRateChange': success_rate_change,
            'totalOrders': total_charging_orders,
            'ordersChange': orders_change
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取KPI数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'avgEfficiency': 0,
            'efficiencyChange': 0,
            'totalEnergy': 0,
            'energyChange': 0,
            'utilization': 0,
            'utilizationChange': 0,
            'avgWaitTime': 0,
            'waitTimeChange': 0,
            'successRate': 0,
            'successRateChange': 0,
            'totalOrders': 0,
            'ordersChange': 0
        })

@energy_efficiency_bp.route('/efficiency-trend', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/efficiency-trend/', methods=['GET', 'OPTIONS'])
def get_efficiency_trend():
    """获取充电效率趋势数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电站数据
        stations_data = data_access.get_charging_stations()
        
        # 筛选充电站
        if station_ids:
            stations_data = [s for s in stations_data if s['id'] in station_ids]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 生成时间轴（每天一个点）
        if start_date and end_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        else:
            # 默认最近30天
            end = datetime.now()
            start = end - timedelta(days=30)
        
        # 生成日期序列
        delta = end - start
        dates = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
        
        # 为每个充电站计算每日效率
        station_efficiencies = []
        
        for station in stations_data:
            station_id = station['id']
            station_name = station['name']
            daily_efficiencies = []
            
            for date in dates:
                # 获取当天该充电站的订单
                day_start = f"{date} 00:00:00"
                day_end = f"{date} 23:59:59"
                
                day_orders = [
                    order for order in filtered_orders
                    if order.get('station_id') == station_id and
                    order.get('status') == 'completed' and
                    parse_datetime(order.get('start_time')).strftime('%Y-%m-%d') == date
                ]
                
                # 计算平均效率
                if day_orders:
                    efficiencies = []
                    for order in day_orders:
                        # 优先使用订单中的充电效率字段
                        if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                            efficiencies.append(order.get('charging_efficiency'))
                        # 如果没有充电效率字段，则计算
                        elif order.get('charge_amount') and order.get('end_time'):
                            efficiency = (
                                order.get('charge_amount', 0) / 
                                ((parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 3600) / 
                                get_station_power(station_id) * 100
                            )
                            efficiencies.append(efficiency)
                    
                    avg_efficiency = sum(efficiencies) / len(efficiencies) if efficiencies else round(station.get('efficiency', 90), 2)
                    daily_efficiencies.append(round(avg_efficiency, 2))
                else:
                    # 如果当天没有订单，使用前一天的效率或默认值
                    if daily_efficiencies:
                        daily_efficiencies.append(daily_efficiencies[-1])
                    else:
                        daily_efficiencies.append(round(station.get('efficiency', 90), 2))
            
            station_efficiencies.append({
                'id': station_id,
                'name': station_name,
                'efficiencyData': daily_efficiencies
            })
        
        result = {
            'timeline': dates,
            'stations': station_efficiencies
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电效率趋势数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'timeline': [],
            'stations': []
        })

@energy_efficiency_bp.route('/energy-distribution', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/energy-distribution/', methods=['GET', 'OPTIONS'])
def get_energy_distribution():
    """获取能耗分布数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 调试信息
        print(f"能耗分布热力图请求参数: startDate={start_date}, endDate={end_date}, stationIds={station_ids}, robotIds={robot_ids}")
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        print(f"获取到的订单总数: {len(orders)}")
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        print(f"筛选后的订单数: {len(filtered_orders)}")
        
        # 检查筛选后的订单中有多少完成状态的订单
        completed_orders = [order for order in filtered_orders if order.get('status') == 'completed']
        print(f"筛选后的已完成订单数: {len(completed_orders)}")
        
        # 生成日期序列
        if start_date and end_date:
            start = parse_datetime(start_date)
            end = parse_datetime(end_date)
        else:
            # 默认最近7天
            end = datetime.now()
            start = end - timedelta(days=7)
        
        # 生成日期序列
        delta = end - start
        dates = [(start + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(delta.days + 1)]
        print(f"生成的日期序列: {dates}")
        
        # 初始化热力图数据
        heatmap_data = []
        max_value = 0
        
        # 计算每个时间点的能耗
        for date in dates:
            for hour in range(24):
                # 当前小时的开始和结束
                hour_start = f"{date} {hour:02d}:00:00"
                hour_end = f"{date} {hour:02d}:59:59"
                
                # 获取该小时内的订单
                hour_orders = [
                    order for order in filtered_orders
                    if order.get('status') == 'completed' and
                    parse_datetime(order.get('start_time')) <= parse_datetime(hour_end) and
                    (not order.get('end_time') or parse_datetime(order.get('end_time')) >= parse_datetime(hour_start))
                ]
                
                # 计算总能耗
                if hour_orders:
                    # 对于跨越多个小时的订单，按时间比例分配能耗
                    total_energy = 0
                    
                    for order in hour_orders:
                        # 如果订单没有充电量数据，则使用估算值
                        charge_amount = order.get('charge_amount')
                        if charge_amount is None:
                            # 使用充电效率和充电时间估算充电量
                            if order.get('charging_efficiency') and order.get('end_time'):
                                station_id = order.get('station_id')
                                station_power = get_station_power(station_id)
                                duration_hours = (parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 3600
                                charge_amount = (station_power * duration_hours * order.get('charging_efficiency', 85)) / 100
                            else:
                                # 如果无法估算，使用平均值 5 kWh
                                charge_amount = 5.0
                        else:
                            # 确保是浮点数
                            try:
                                charge_amount = float(charge_amount)
                            except (ValueError, TypeError):
                                charge_amount = 5.0  # 转换失败时使用默认值
                        
                        start_time = max(parse_datetime(order.get('start_time')), parse_datetime(hour_start))
                        end_time = min(parse_datetime(order.get('end_time', datetime.now().isoformat())), parse_datetime(hour_end))
                        
                        # 计算在当前小时内的时间比例
                        total_duration = (parse_datetime(order.get('end_time', datetime.now().isoformat())) - parse_datetime(order.get('start_time'))).total_seconds()
                        hour_duration = (end_time - start_time).total_seconds()
                        
                        if total_duration > 0:
                            proportion = hour_duration / total_duration
                            energy = charge_amount * proportion
                            total_energy += energy
                    
                    # 确保数据格式正确 - 使用字符串表示小时
                    data_point = [date, str(hour), round(total_energy, 2)]
                    heatmap_data.append(data_point)
                    max_value = max(max_value, total_energy)
                else:
                    # 即使没有数据，也添加零值点，确保热力图完整
                    heatmap_data.append([date, str(hour), 0])
        
        print(f"生成的热力图数据点数: {len(heatmap_data)}")
        print(f"最大能耗值: {max_value}")
        
        # 确保最大值不为0，避免热力图显示异常
        if max_value == 0:
            max_value = 1.0
        
        # 检查数据格式
        for i, point in enumerate(heatmap_data[:5]):
            print(f"示例数据点 {i}: {point}")
        
        # 固定最大值为120，与前端保持一致
        max_value = 120
        
        result = {
            'days': dates,
            'data': heatmap_data,
            'maxValue': max_value
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取能耗分布数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'days': [],
            'data': [],
            'maxValue': 0
        })

@energy_efficiency_bp.route('/station-utilization', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/station-utilization/', methods=['GET', 'OPTIONS'])
def get_station_utilization():
    """获取充电站利用率数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        
        # 获取充电站数据
        stations = data_access.get_charging_stations()
        
        # 筛选充电站
        if station_ids:
            stations = [s for s in stations if s['id'] in station_ids]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 计算时间范围（小时）
        if start_date and end_date:
            start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            total_hours = (end - start).total_seconds() / 3600
        else:
            # 默认24小时
            total_hours = 24
        
        # 计算每个充电站的利用情况
        result = []
        
        for station in stations:
            station_id = station['id']
            station_name = station['name']
            
            # 获取该充电站的订单
            station_orders = [order for order in filtered_orders if order.get('station_id') == station_id]
            
            # 计算充电时间（忙碌时间）
            busy_hours = sum([
                (parse_datetime(order.get('end_time', datetime.now().isoformat())) - parse_datetime(order.get('start_time'))).total_seconds() / 3600
                for order in station_orders
            ])
            
            # 根据状态计算其他时间
            station_status = station.get('status', 'idle')
            
            if station_status == 'maintenance':
                maintenance_hours = total_hours - busy_hours
                idle_hours = 0
                error_hours = 0
            elif station_status == 'error':
                maintenance_hours = 0
                idle_hours = 0
                error_hours = total_hours - busy_hours
            else:
                maintenance_hours = 0
                idle_hours = total_hours - busy_hours
                error_hours = 0
            
            result.append({
                'stationId': station_id,
                'stationName': station_name,
                'busyHours': round(busy_hours, 2),
                'idleHours': round(idle_hours, 2),
                'maintenanceHours': round(maintenance_hours, 2),
                'errorHours': round(error_hours, 2)
            })
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电站利用率数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])

@energy_efficiency_bp.route('/robot-charging-behavior', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/robot-charging-behavior/', methods=['GET', 'OPTIONS'])
def get_robot_charging_behavior():
    """获取机器人充电行为分析数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取机器人数据
        robots_data = data_access.get_robots()
        
        # 筛选机器人
        if robot_ids:
            robots_data = [r for r in robots_data if r['id'] in robot_ids]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 为每个机器人分析充电行为
        robot_analysis = []
        
        for robot in robots_data:
            robot_id = robot['id']
            robot_name = robot['name']
            
            # 获取该机器人的订单
            robot_orders = [order for order in filtered_orders if order.get('robot_id') == robot_id]
            
            # 充电次数
            charging_count = len(robot_orders)
            
            # 平均充电时长（分钟）
            charging_durations = [
                (parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 60
                for order in robot_orders
                if order.get('status') == 'completed' and order.get('end_time')
            ]
            
            avg_charging_duration = sum(charging_durations) / len(charging_durations) if charging_durations else 0
            
            # 平均等待时间（分钟）
            waiting_times = [
                (parse_datetime(order.get('start_time')) - parse_datetime(order.get('created_at'))).total_seconds() / 60
                for order in robot_orders
                if order.get('created_at') and 
                parse_datetime(order.get('start_time')) > parse_datetime(order.get('created_at'))
            ]
            
            avg_waiting_time = sum(waiting_times) / len(waiting_times) if waiting_times else 0
            
            robot_analysis.append({
                'id': robot_id,
                'name': robot_name,
                'chargingCount': charging_count,
                'avgChargingDuration': round(avg_charging_duration, 2),
                'avgWaitingTime': round(avg_waiting_time, 2)
            })
        
        result = {
            'robots': robot_analysis
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取机器人充电行为数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'robots': []
        })

@energy_efficiency_bp.route('/peak-analysis', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/peak-analysis/', methods=['GET', 'OPTIONS'])
def get_charging_peak_analysis():
    """获取充电高峰期分析数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response

    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 初始化数据结构
        hour_slots = ['0-2', '2-4', '4-6', '6-8', '8-10', '10-12', '12-14', '14-16', '16-18', '18-20', '20-22', '22-24']
        request_counts = [0] * 12
        waiting_times = [[] for _ in range(12)]
        
        # 分析每个订单
        for order in filtered_orders:
            created_time = parse_datetime(order.get('created_at'))
            hour = created_time.hour
            
            # 确定时间段
            slot_index = hour // 2
            request_counts[slot_index] += 1
            
            # 计算等待时间
            if order.get('start_time'):
                start_time = parse_datetime(order.get('start_time'))
                if start_time > created_time:
                    wait_time = (start_time - created_time).total_seconds() / 60
                    waiting_times[slot_index].append(wait_time)
        
        # 计算平均等待时间
        avg_waiting_times = [
            round(sum(times) / len(times), 2) if times else 0
            for times in waiting_times
        ]
        
        result = {
            'timeSlots': hour_slots,
            'requestCounts': request_counts,
            'avgWaitingTimes': avg_waiting_times
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电高峰期分析数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'timeSlots': [],
            'requestCounts': [],
            'avgWaitingTimes': []
        })

@energy_efficiency_bp.route('/charging-events', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/charging-events/', methods=['GET', 'OPTIONS'])
def get_charging_events():
    """获取充电事件列表数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('pageSize', 20, type=int)
        query = request.args.get('query', '')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 获取机器人和充电站数据用于名称映射
        robots = {r['id']: r['name'] for r in data_access.get_robots()}
        stations = {s['id']: s['name'] for s in data_access.get_charging_stations()}
        
        # 转换为前端所需格式
        events = []
        for order in filtered_orders:
            try:
                robot_id = order.get('robot_id')
                station_id = order.get('station_id')
                
                # 优先使用订单中的充电效率字段，如果不存在则计算
                efficiency = None
                if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                    efficiency = order.get('charging_efficiency')
                elif order.get('status') == 'completed' and order.get('charge_amount') and order.get('end_time'):
                    duration_hours = (parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds() / 3600
                    station_power = get_station_power(station_id)
                    if duration_hours > 0 and station_power > 0:
                        efficiency = (order.get('charge_amount', 0) / (duration_hours * station_power)) * 100
                
                # 创建事件数据
                event = {
                    'id': order.get('id'),
                    'robotId': robot_id,
                    'robotName': robots.get(robot_id, f'机器人 {robot_id}'),
                    'stationId': station_id,
                    'stationName': stations.get(station_id, f'充电站 {station_id}'),
                    'startTime': order.get('start_time'),
                    'endTime': order.get('end_time'),
                    'energyConsumed': order.get('charge_amount'),
                    'efficiency': efficiency,
                    'status': order.get('status', 'unknown')
                }
                
                # 搜索过滤
                if query:
                    query = query.lower()
                    if (str(event['id']).lower().find(query) >= 0 or
                        event['robotName'].lower().find(query) >= 0 or
                        event['stationName'].lower().find(query) >= 0 or
                        event['status'].lower().find(query) >= 0):
                        events.append(event)
                else:
                    events.append(event)
            except Exception as e:
                print(f"处理订单数据失败: {str(e)}, 订单: {order}")
        
        # 按开始时间倒序排序
        events = sorted(events, key=lambda x: parse_datetime(x['startTime']), reverse=True)
        
        # 分页
        total_items = len(events)
        total_pages = (total_items + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_items)
        paged_events = events[start_idx:end_idx]
        
        result = {
            'items': paged_events,
            'pagination': {
                'totalItems': total_items,
                'totalPages': total_pages,
                'currentPage': page,
                'pageSize': page_size
            }
        }
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电事件列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'items': [],
            'pagination': {
                'totalItems': 0,
                'totalPages': 0,
                'currentPage': 1,
                'pageSize': 20
            }
        })

@energy_efficiency_bp.route('/export', methods=['GET', 'OPTIONS'])
@energy_efficiency_bp.route('/export/', methods=['GET', 'OPTIONS'])
def export_energy_data():
    """导出能效分析数据"""
    # 处理OPTIONS请求
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET, OPTIONS')
        return response
    
    try:
        # 获取筛选参数
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        station_ids = request.args.get('stationIds')
        robot_ids = request.args.get('robotIds')
        export_type = request.args.get('exportType', 'csv')
        
        # 转换参数格式
        if station_ids:
            station_ids = [int(id) for id in station_ids.split(',')]
        if robot_ids:
            robot_ids = [int(id) for id in robot_ids.split(',')]
        
        # 获取充电订单数据
        orders = data_access.get_charging_orders()
        
        # 筛选订单
        filtered_orders = filter_orders(orders, start_date, end_date, station_ids, robot_ids)
        
        # 获取机器人和充电站数据用于名称映射
        robots = {r['id']: r['name'] for r in data_access.get_robots()}
        stations = {s['id']: s['name'] for s in data_access.get_charging_stations()}
        
        # 转换为导出格式
        export_data = []
        for order in filtered_orders:
            try:
                robot_id = order.get('robot_id')
                station_id = order.get('station_id')
                
                # 计算效率和充电时长
                efficiency = None
                duration = None
                if order.get('end_time'):
                    duration_seconds = (parse_datetime(order.get('end_time')) - parse_datetime(order.get('start_time'))).total_seconds()
                    duration = duration_seconds / 60  # 转换为分钟
                    
                    # 优先使用订单中的充电效率字段，如果不存在则计算
                    if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                        efficiency = order.get('charging_efficiency')
                    elif order.get('status') == 'completed' and order.get('charge_amount'):
                        station_power = get_station_power(station_id)
                        if station_power > 0:
                            efficiency = (order.get('charge_amount', 0) / (duration_seconds / 3600 * station_power)) * 100
                
                # 计算等待时间
                wait_time = None
                if order.get('created_at') and order.get('start_time'):
                    created_time = parse_datetime(order.get('created_at'))
                    start_time = parse_datetime(order.get('start_time'))
                    if start_time > created_time:
                        wait_time = (start_time - created_time).total_seconds() / 60  # 转换为分钟
                
                # 创建导出数据行
                export_row = {
                    '订单ID': order.get('id'),
                    '机器人ID': robot_id,
                    '机器人名称': robots.get(robot_id, f'机器人 {robot_id}'),
                    '充电站ID': station_id,
                    '充电站名称': stations.get(station_id, f'充电站 {station_id}'),
                    '创建时间': order.get('created_at'),
                    '开始时间': order.get('start_time'),
                    '结束时间': order.get('end_time'),
                    '充电时长(分钟)': round(duration, 2) if duration is not None else None,
                    '等待时间(分钟)': round(wait_time, 2) if wait_time is not None else None,
                    '能耗(kWh)': order.get('charge_amount'),
                    '充电效率(%)': round(efficiency, 2) if efficiency is not None else None,
                    '状态': order.get('status', 'unknown')
                }
                
                export_data.append(export_row)
            except Exception as e:
                print(f"处理导出数据失败: {str(e)}, 订单: {order}")
        
        # 生成CSV或Excel文件
        if export_type == 'csv':
            # 生成CSV
            import csv
            import io
            
            output = io.StringIO()
            if export_data:
                writer = csv.DictWriter(output, fieldnames=export_data[0].keys())
                writer.writeheader()
                writer.writerows(export_data)
                
            response = current_app.response_class(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment;filename=energy_efficiency_data_{datetime.now().strftime("%Y%m%d")}.csv'}
            )
            return response
        else:
            # 生成Excel
            import xlsxwriter
            import io
            
            output = io.BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet('能效分析数据')
            
            # 添加标题行
            if export_data:
                for col, field in enumerate(export_data[0].keys()):
                    worksheet.write(0, col, field)
                
                # 添加数据行
                for row, data in enumerate(export_data, start=1):
                    for col, field in enumerate(data.keys()):
                        worksheet.write(row, col, data[field])
            
            workbook.close()
            output.seek(0)
            
            response = current_app.response_class(
                output.getvalue(),
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                headers={'Content-Disposition': f'attachment;filename=energy_efficiency_data_{datetime.now().strftime("%Y%m%d")}.xlsx'}
            )
            return response
    except Exception as e:
        print(f"导出能效分析数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': '导出数据失败'}), 500

# 辅助函数

def parse_datetime(datetime_str):
    """解析日期时间字符串"""
    if not datetime_str:
        return datetime.now().replace(tzinfo=None)
    
    try:
        # 尝试解析ISO格式
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        # 去除时区信息，确保所有日期时间都是offset-naive的
        return dt.replace(tzinfo=None)
    except:
        try:
            # 尝试解析其他格式
            return datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')
        except:
            return datetime.now().replace(tzinfo=None)

def get_station_power(station_id):
    """获取充电站的功率"""
    stations = data_access.get_charging_stations()
    for station in stations:
        if station['id'] == station_id:
            return station.get('power_output', station.get('power_rating', 10))
    return 10  # 默认值

def filter_orders(orders, start_date=None, end_date=None, station_ids=None, robot_ids=None):
    """根据条件筛选订单"""
    filtered = orders.copy()
    
    # 按时间筛选
    if start_date:
        # 确保start是无时区的
        start = parse_datetime(start_date)
        filtered = [order for order in filtered if parse_datetime(order.get('start_time')) >= start]
    
    if end_date:
        # 确保end是无时区的
        end = parse_datetime(end_date)
        filtered = [order for order in filtered if parse_datetime(order.get('start_time')) <= end]
    
    # 按充电站筛选
    if station_ids:
        filtered = [order for order in filtered if order.get('station_id') in station_ids]
    
    # 按机器人筛选
    if robot_ids:
        filtered = [order for order in filtered if order.get('robot_id') in robot_ids]
    
    return filtered

# 处理OPTIONS请求的通用函数
@energy_efficiency_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options_requests(path):
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# 处理根路径的OPTIONS请求
@energy_efficiency_bp.route('/', methods=['OPTIONS'])
def handle_root_options_requests():
    response = jsonify({})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', '*')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response 

# 新增：解除机器人与充电桩的关联
@robot_bp.route('/<int:robot_id>/release', methods=['POST'])
def release_robot_from_station(robot_id):
    """解除机器人与充电桩的关联"""
    try:
        print(f"接收到解除机器人关联请求: 机器人ID={robot_id}")
        
        # 调用数据访问函数解除机器人与充电桩的关联
        success, message = data_access.release_robot_from_station(robot_id)
        
        if success:
            print(f"成功解除机器人关联: {message}")
            # 清除缓存，确保下次获取最新数据
            data_access.clear_cache()
            return jsonify({'message': message})
        else:
            print(f"解除机器人关联失败: {message}")
            return jsonify({'error': message}), 400
    except Exception as e:
        print(f"解除机器人关联出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'服务器错误: {str(e)}'}), 500