import os
from datetime import timedelta, datetime

# 创建应用实例
from app import create_app, db
from app.models import User, Robot, ChargingStation, ChargingOrder
import random
    
# 创建应用实例
app = create_app()

# 打印JWT配置信息
print("JWT配置信息:")
print(f"JWT_SECRET_KEY: {'已设置' if app.config.get('JWT_SECRET_KEY') else '未设置'}")
print(f"JWT_IDENTITY_CLAIM: {app.config.get('JWT_IDENTITY_CLAIM')}")
print(f"JWT_ERROR_MESSAGE_KEY: {app.config.get('JWT_ERROR_MESSAGE_KEY')}")
print(f"JWT_ACCESS_TOKEN_EXPIRES: {app.config.get('JWT_ACCESS_TOKEN_EXPIRES')}")

# # 配置 (Configuration is loaded within create_app)
# # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://whale:20020608@localhost/charging_station'
# # app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# # app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'your-secret-key')
# # app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

# # 初始化扩展 (Extensions are initialized within create_app)
# # CORS(app)
# # jwt = JWTManager(app)
# # db.init_app(app)

# # 注册蓝图 (Blueprints are registered within create_app)
# # app.register_blueprint(api, url_prefix='/api')

# 主程序入口
if __name__ == '__main__':
    # 恢复数据库初始化代码
    with app.app_context():
        # 强制重新创建所有表，确保结构与模型一致
        # db.drop_all()
        # db.create_all()
        
        # 检查是否已存在管理员用户
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            # 创建管理员用户
            admin = User(username='admin', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print('管理员用户创建成功！')
        else:
            print('管理员用户已存在！')
            
        # 添加测试数据 - 充电站
        if ChargingStation.query.count() == 0:
            for i in range(1, 13):
                station = ChargingStation(
                    name=f'充电站-{i:03d}',
                    location=f'位置-{i}',
                    status='idle',
                    power_rating=random.choice([5, 7.5, 10, 12]),
                    efficiency=random.uniform(85, 98),
                    last_maintenance=datetime.utcnow() - timedelta(days=random.randint(1, 60))
                )
                db.session.add(station)
            db.session.commit()
            print(f'添加了 {ChargingStation.query.count()} 个充电站')
            
        # 添加测试数据 - 机器人
        if Robot.query.count() == 0:
            stations = ChargingStation.query.all()
            for i in range(1, 21):
                # 随机状态
                status = random.choice(['idle', 'working', 'charging', 'error'])
                # 根据状态设置电量
                if status == 'charging':
                    battery = random.uniform(10, 40)
                elif status == 'idle':
                    battery = random.uniform(60, 100)
                else:
                    battery = random.uniform(20, 90)
                
                # 随机分配充电站（30%的机器人有充电站）
                station_id = None
                if status == 'charging' or random.random() < 0.3:
                    station = random.choice(stations)
                    if station.status == 'idle':
                        station_id = station.id
                        if status == 'charging':
                            station.status = 'charging'
                
                robot = Robot(
                    name=f'机器人-{i:03d}',
                    battery_level=battery,
                    status=status,
                    station_id=station_id,
                    last_charging=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                db.session.add(robot)
            db.session.commit()
            print(f'添加了 {Robot.query.count()} 个机器人')
            
        # 添加测试数据 - 充电订单
        if ChargingOrder.query.count() == 0:
            robots = Robot.query.all()
            stations = ChargingStation.query.all()
            
            # 为每个机器人创建1-5个历史充电记录
            for robot in robots:
                for _ in range(random.randint(1, 5)):
                    station = random.choice(stations)
                    
                    # 创建一个随机的开始时间（过去30天内）
                    start_time = datetime.utcnow() - timedelta(
                        days=random.randint(1, 30),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59)
                    )
                    
                    # 充电时间1-4小时
                    charging_hours = random.uniform(1, 4)
                    end_time = start_time + timedelta(hours=charging_hours)
                    
                    # 计算充电量和效率
                    station_power = station.power_rating
                    efficiency = random.uniform(80, 98)
                    charge_amount = station_power * charging_hours * (efficiency / 100)
                    
                    order = ChargingOrder(
                        robot_id=robot.id,
                        station_id=station.id,
                        start_time=start_time,
                        end_time=end_time,
                        status='completed',
                        charge_amount=charge_amount,
                        charging_efficiency=efficiency
                    )
                    db.session.add(order)
            
            db.session.commit()
            print(f'添加了 {ChargingOrder.query.count()} 个充电订单')
            
    # 运行应用
    app.run(debug=True, host='0.0.0.0', port=5000) 