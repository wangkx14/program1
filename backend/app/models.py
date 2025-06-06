from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ChargingStation(db.Model):
    __tablename__ = 'charging_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    status = db.Column(db.String(20), default='idle')  # idle, charging, maintenance, error
    power_output = db.Column(db.Float, default=0.0)
    efficiency = db.Column(db.Float, default=100.0)
    power_rating = db.Column(db.Float, default=0.0)  # 添加功率额定值字段
    last_maintenance = db.Column(db.DateTime)  # 添加最后维护时间字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Robot(db.Model):
    __tablename__ = 'robots'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    battery_level = db.Column(db.Float, default=100.0)
    status = db.Column(db.String(20), default='idle')  # idle, working, charging, error
    station_id = db.Column(db.Integer, db.ForeignKey('charging_stations.id'), nullable=True)  # 关联的充电桩ID
    last_charging = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 添加与充电桩的关系
    station = db.relationship('ChargingStation', backref='robots')

class ChargingOrder(db.Model):
    __tablename__ = 'charging_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    robot_id = db.Column(db.Integer, db.ForeignKey('robots.id'), nullable=False)
    station_id = db.Column(db.Integer, db.ForeignKey('charging_stations.id'), nullable=False)
    start_time = db.Column(db.DateTime, default=datetime.utcnow)
    end_time = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='charging')  # charging, completed, failed
    charge_amount = db.Column(db.Float, default=0.0)  # 充电量
    charging_efficiency = db.Column(db.Float, default=0.0)  # 充电效率
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    robot = db.relationship('Robot', backref='orders')
    station = db.relationship('ChargingStation', backref='orders')

class SystemAlert(db.Model):
    __tablename__ = 'system_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, default=datetime.utcnow)
    type = db.Column(db.String(50), nullable=False)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class EfficiencyLog(db.Model):
    __tablename__ = 'efficiency_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.Integer, db.ForeignKey('charging_stations.id'), nullable=False)
    efficiency = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    station = db.relationship('ChargingStation', backref='efficiency_logs')

class SystemSetting(db.Model):
    __tablename__ = 'system_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SystemLog(db.Model):
    __tablename__ = 'system_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    action = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='logs') 