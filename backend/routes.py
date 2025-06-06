from flask import Blueprint, request, jsonify, render_template_string
from flask_jwt_extended import jwt_required, get_jwt_identity, create_access_token
from models import db, ChargingStation, User

api = Blueprint('api', __name__)

# 添加根路径路由
@api.route('/')
def index():
    return jsonify({"message": "欢迎使用充电桩管理系统 API"})

# 充电站相关路由
@api.route('/stations', methods=['GET'])
@jwt_required()
def get_stations():
    stations = ChargingStation.query.all()
    return jsonify([{
        'id': station.id,
        'name': station.name,
        'location': station.location,
        'status': station.status,
        'power_output': station.power_output,
        'efficiency': station.efficiency,
        'created_at': station.created_at.isoformat(),
        'updated_at': station.updated_at.isoformat()
    } for station in stations])

@api.route('/stations/<int:id>', methods=['GET'])
@jwt_required()
def get_station(id):
    station = ChargingStation.query.get_or_404(id)
    return jsonify({
        'id': station.id,
        'name': station.name,
        'location': station.location,
        'status': station.status,
        'power_output': station.power_output,
        'efficiency': station.efficiency,
        'created_at': station.created_at.isoformat(),
        'updated_at': station.updated_at.isoformat()
    })

@api.route('/stations', methods=['POST'])
@jwt_required()
def create_station():
    data = request.get_json()
    station = ChargingStation(
        name=data['name'],
        location=data.get('location', ''),
        power_output=data.get('power_output', 0.0)
    )
    db.session.add(station)
    db.session.commit()
    return jsonify({
        'id': station.id,
        'name': station.name,
        'location': station.location,
        'status': station.status,
        'power_output': station.power_output,
        'efficiency': station.efficiency
    }), 201

@api.route('/stations/<int:id>', methods=['PUT'])
@jwt_required()
def update_station(id):
    station = ChargingStation.query.get_or_404(id)
    data = request.get_json()
    
    station.name = data.get('name', station.name)
    station.location = data.get('location', station.location)
    station.power_output = data.get('power_output', station.power_output)
    
    db.session.commit()
    return jsonify({
        'id': station.id,
        'name': station.name,
        'location': station.location,
        'status': station.status,
        'power_output': station.power_output,
        'efficiency': station.efficiency
    })

@api.route('/stations/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_station(id):
    station = ChargingStation.query.get_or_404(id)
    db.session.delete(station)
    db.session.commit()
    return '', 204

# 添加登录页面路由
@api.route('/login', methods=['GET'])
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
                            window.location.href = '/';
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

# 登录 API 路由
# @api.route('/login', methods=['POST'])
# def login():
#     data = request.get_json()
#     print(f"Received login data: {data}")
#     username = data.get('username')
#     password = data.get('password')

#     user = User.query.filter_by(username=username).first()
#     print(f"User found in DB: {user}")

#     if user and user.check_password(password):
#         print("Password check successful")
#         access_token = create_access_token(identity=user.id)
#         return jsonify({
#             'access_token': access_token,
#             'user': {
#                 'id': user.id,
#                 'username': user.username,
#                 'role': user.role
#             }
#         })
    
#     return jsonify({'error': '用户名或密码错误'}), 401 

@api.route('/dashboard', methods=['GET'])
def get_dashboard_data():
    """获取仪表盘所需的统计数据"""
    try:
        # ... existing code ...
        
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
        return jsonify({'error': '获取仪表盘数据失败'})

@api.route('/charging-efficiency', methods=['GET'])
def get_charging_efficiency():
    """获取充电效率趋势数据，用于系统概览页面"""
    try:
        # 获取所有充电订单
        orders = get_charging_orders()
        
        # 获取所有充电站
        stations = get_charging_stations()
        
        # 创建充电站ID到名称的映射
        station_map = {station['id']: station['name'] for station in stations}
        
        # 获取每个充电站最新的充电效率数据
        station_efficiency = {}
        
        for order in orders:
            # 只考虑已完成的订单
            if order.get('status') != 'completed':
                continue
                
            station_id = order.get('station_id')
            if not station_id:
                continue
                
            # 获取充电效率数据
            efficiency = None
            # 优先使用订单中的充电效率字段
            if 'charging_efficiency' in order and order.get('charging_efficiency') is not None:
                efficiency = order.get('charging_efficiency')
            # 如果没有充电效率字段，则尝试计算
            elif order.get('charge_amount') and order.get('end_time') and order.get('start_time'):
                try:
                    start_time = parse_datetime(order.get('start_time'))
                    end_time = parse_datetime(order.get('end_time'))
                    duration_hours = (end_time - start_time).total_seconds() / 3600
                    
                    # 获取充电站功率
                    station_power = None
                    for station in stations:
                        if station['id'] == station_id:
                            station_power = station.get('power_output')
                            break
                    
                    if duration_hours > 0 and station_power and station_power > 0:
                        efficiency = (order.get('charge_amount', 0) / (duration_hours * station_power)) * 100
                except Exception as e:
                    print(f"计算充电效率出错: {str(e)}")
            
            # 如果成功获取到效率数据，更新该充电站的最新效率
            if efficiency is not None:
                if station_id not in station_efficiency:
                    station_efficiency[station_id] = {
                        'id': station_id,
                        'name': station_map.get(station_id, f'充电站 {station_id}'),
                        'efficiency': efficiency,
                        'timestamp': order.get('end_time')
                    }
                else:
                    # 比较时间戳，保留最新的数据
                    current_timestamp = station_efficiency[station_id]['timestamp']
                    new_timestamp = order.get('end_time')
                    
                    if new_timestamp and current_timestamp:
                        if parse_datetime(new_timestamp) > parse_datetime(current_timestamp):
                            station_efficiency[station_id]['efficiency'] = efficiency
                            station_efficiency[station_id]['timestamp'] = new_timestamp
        
        # 转换为列表格式
        result = list(station_efficiency.values())
        
        # 按充电站ID排序
        result.sort(key=lambda x: x['id'])
        
        return jsonify(result)
    except Exception as e:
        print(f"获取充电效率趋势数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([]), 500 