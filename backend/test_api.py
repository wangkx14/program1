import requests
import json
import sys

def test_robots_api():
    """测试机器人API接口"""
    try:
        print("测试机器人API...")
        response = requests.get('http://localhost:5000/api/robots')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"数据类型: {type(data)}")
            print(f"是否为数组: {isinstance(data, list)}")
            print(f"数据长度: {len(data) if isinstance(data, list) else '不适用'}")
            print(f"数据内容: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"测试出错: {str(e)}")
        return False

def test_stations_api():
    """测试充电站API接口"""
    try:
        print("\n测试充电站API...")
        response = requests.get('http://localhost:5000/api/stations')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"数据类型: {type(data)}")
            print(f"是否为数组: {isinstance(data, list)}")
            print(f"数据长度: {len(data) if isinstance(data, list) else '不适用'}")
            print(f"数据内容: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"测试出错: {str(e)}")
        return False

def test_orders_api():
    """测试订单API接口"""
    try:
        print("\n测试订单API...")
        response = requests.get('http://localhost:5000/api/orders')
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"数据类型: {type(data)}")
            print(f"是否为数组: {isinstance(data, list)}")
            print(f"数据长度: {len(data) if isinstance(data, list) else '不适用'}")
            print(f"数据内容: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            return True
        else:
            print(f"请求失败: {response.text}")
            return False
    except Exception as e:
        print(f"测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试API接口...")
    robots_result = test_robots_api()
    stations_result = test_stations_api()
    orders_result = test_orders_api()
    
    print("\n测试结果汇总:")
    print(f"机器人API: {'成功' if robots_result else '失败'}")
    print(f"充电站API: {'成功' if stations_result else '失败'}")
    print(f"订单API: {'成功' if orders_result else '失败'}")
    
    if robots_result and stations_result and orders_result:
        print("所有API测试通过")
        sys.exit(0)
    else:
        print("API测试失败")
        sys.exit(1) 