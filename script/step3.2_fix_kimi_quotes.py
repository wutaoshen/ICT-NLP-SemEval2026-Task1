import json
import os

def fix_quotes_in_kimi_file(input_file, output_file):
    """
    将kimi-k2-thinking输出文件中的 \" 转换为中文引号 " 和 "
    :param input_file: 输入文件路径
    :param output_file: 输出文件路径
    """
    try:
        # 读取JSON文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 如果是单个对象，转换为列表
        if isinstance(data, dict):
            data = [data]
        
        fixed_count = 0
        
        # 处理每条记录
        for item in data:
            if 'joke_result' in item:
                # 修复reason字段中的引号
                if 'reason' in item['joke_result'] and isinstance(item['joke_result']['reason'], str):
                    original = item['joke_result']['reason']
                    # 将 \" 替换为中文引号
                    # 策略：成对替换，第一个替换为左引号，第二个替换为右引号
                    fixed = replace_quotes_smartly(original)
                    if fixed != original:
                        item['joke_result']['reason'] = fixed
                        fixed_count += 1
                
                # 修复joke字段中的引号
                if 'joke' in item['joke_result'] and isinstance(item['joke_result']['joke'], str):
                    original = item['joke_result']['joke']
                    fixed = replace_quotes_smartly(original)
                    if fixed != original:
                        item['joke_result']['joke'] = fixed
                        fixed_count += 1
                
                print(f"已处理记录 {item.get('id', 'unknown')}")
        
        # 保存修复后的数据
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"\n处理完成！共修复 {fixed_count} 处引号")
        print(f"结果已保存到: {output_file}")
        
    except FileNotFoundError:
        print(f"错误：找不到文件 {input_file}")
    except json.JSONDecodeError:
        print(f"错误：{input_file} 不是有效的JSON文件")
    except Exception as e:
        print(f"处理过程中发生错误: {e}")

def replace_quotes_smartly(text):
    """
    智能替换引号：将 " 成对替换为 “ 和 ”
    :param text: 原始文本
    :return: 替换后的文本
    """
    result = []
    use_left_quote = True  # 标记下一个引号是否使用左引号
    
    i = 0
    while i < len(text):
        # 检查是否是双引号
        if text[i] == '"':
            if use_left_quote:
                result.append('“')  # 左引号
            else:
                result.append('”')  # 右引号
            use_left_quote = not use_left_quote  # 切换状态
            i += 1
        else:
            result.append(text[i])
            i += 1
    
    return ''.join(result)

# 使用示例
if __name__ == "__main__":
    # 获取当前脚本所在目录，确保路径在不同运行环境下都有效
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_file = os.path.join(script_dir, "../output/step3_kimi-k2-thinking.json")
    output_file = os.path.join(script_dir, "../output/step3_kimi-k2-thinking-fixed.json")
    
    fix_quotes_in_kimi_file(input_file, output_file)
