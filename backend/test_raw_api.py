import requests
import json

def test_raw_robots_api():
    """测试机器人API的原始响应内容"""
    try:
        print("测试机器人API原始响应...")
        # 发送请求
        response = requests.get('http://localhost:5000/api/robots')
        
        # 打印响应头
        print("响应头:")
        for key, value in response.headers.items():
            print(f"  {key}: {value}")
        
        # 打印状态码
        print(f"\n状态码: {response.status_code}")
        
        # 打印原始响应内容
        print("\n原始响应内容:")
        raw_content = response.content
        print(f"类型: {type(raw_content)}")
        print(f"长度: {len(raw_content)}")
        print(f"内容: {raw_content[:500]}...")
        
        # 尝试解析为JSON
        print("\n尝试解析为JSON:")
        try:
            data = response.json()
            print(f"JSON类型: {type(data)}")
            print(f"是否为数组: {isinstance(data, list)}")
            print(f"长度: {len(data) if isinstance(data, list) else 'N/A'}")
            print(f"内容: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}...")
            return True
        except Exception as e:
            print(f"解析JSON失败: {str(e)}")
            # 尝试手动解析
            try:
                text = response.text
                print(f"响应文本: {text[:500]}...")
                # 尝试手动解析JSON
                manual_data = json.loads(text)
                print(f"手动解析后的类型: {type(manual_data)}")
                print(f"手动解析后是否为数组: {isinstance(manual_data, list)}")
            except Exception as e2:
                print(f"手动解析JSON失败: {str(e2)}")
            return False
    except Exception as e:
        print(f"测试出错: {str(e)}")
        return False

if __name__ == "__main__":
    print("开始测试API原始响应...")
    test_raw_robots_api()
    print("\n测试完成") 