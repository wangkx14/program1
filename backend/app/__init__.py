from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os
from config import Config
from flask_sqlalchemy import SQLAlchemy

# 恢复数据库初始化
db = SQLAlchemy()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    
    # 配置
    app.config.from_object(Config)
    
    # 初始化扩展，恢复数据库初始化
    db.init_app(app)
    jwt.init_app(app)
    
    # 配置CORS，允许所有来源，所有方法和所有头部
    CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": "*"}})
    
    # JWT错误处理
    @jwt.invalid_token_loader
    def invalid_token_callback(error_string):
        return jsonify({
            'error': 'Invalid token',
            'description': error_string
        }), 401
    
    @jwt.unauthorized_loader
    def unauthorized_callback(error_string):
        return jsonify({
            'error': 'Missing Authorization Header',
            'description': error_string
        }), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'error': 'Token has expired',
            'description': 'Please log in again'
        }), 401
    
    # 注册蓝图
    from .routes import auth_bp, user_bp, station_bp, order_bp, system_bp, robot_bp, energy_efficiency_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(user_bp, url_prefix='/api/users')
    app.register_blueprint(station_bp, url_prefix='/api/stations')
    app.register_blueprint(order_bp, url_prefix='/api/orders')
    app.register_blueprint(system_bp, url_prefix='/api/system')
    app.register_blueprint(robot_bp, url_prefix='/api/robots')  # 注册机器人蓝图
    app.register_blueprint(energy_efficiency_bp, url_prefix='/api/energy-efficiency')  # 注册能效分析蓝图
    
    # 打印数据库连接信息
    with app.app_context():
        print(f"数据库连接URI: {app.config['SQLALCHEMY_DATABASE_URI']}")
        # 尝试从数据访问模块打印连接信息
        try:
            from .data_access import print_connection_info
            print_connection_info()
        except Exception as e:
            print(f"无法打印数据库连接信息: {e}")
    
    return app 