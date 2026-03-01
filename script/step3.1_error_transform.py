import json
import re

def parse_raw_response(raw_response):
    """从raw_response中提取reason和joke"""
    try:
        # 移除markdown代码块标记
        cleaned = raw_response.strip()
        cleaned = re.sub(r'^```json\s*', '', cleaned)
        cleaned = re.sub(r'\s*```$', '', cleaned)
        
        # 解析JSON
        parsed = json.loads(cleaned)
        return parsed.get('reason', ''), parsed.get('joke', '')
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
        return '', ''
    except Exception as e:
        print(f"处理失败: {e}")
        return '', ''

def process_json_file(input_file, output_file):
    """处理JSON文件，更新joke_result"""
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果是单个对象，转换为列表
        if isinstance(data, dict):
            data = [data]
        
        updated_count = 0
        
        # 处理每条记录
        for item in data:
            if 'joke_result' in item and 'raw_response' in item['joke_result']:
                raw_response = item['joke_result']['raw_response']
                
                if raw_response:
                    reason, joke = parse_raw_response(raw_response)
                    
                    if reason or joke:
                        item['joke_result']['reason'] = reason
                        item['joke_result']['joke'] = joke
                        item['joke_result']['error'] = ''  # 清空error字段
                        updated_count += 1
                        print(f"已更新记录 {item.get('id', 'unknown')}")
        
        # 保存更新后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成！共更新 {updated_count} 条记录")
        print(f"结果已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误：{input_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

# 使用示例
if __name__ == "__main__":
    input_file = "../output/step3_qwen-max.json"  # 输入文件名
    output_file = "../output/step3_qwen-max-new.json"  # 输出文件名
    
    process_json_file(input_file, output_file)