import json
import os
import csv
import re
from opencc import OpenCC

def load_json(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_tsv(data, file_path):
    """保存为TSV文件"""
    with open(file_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        # 写入表头
        writer.writerow(['id', 'text'])
        # 写入数据
        for item in data:
            writer.writerow([item['id'], item['text']])
def remove_format_chars(text):
    """删除文本中的换行符、回车符等格式符号"""
    if not text:
        return text
    # 删除所有换行符、回车符、制表符等
    text = text.replace('\n', '').replace('\r', '').replace('\t', '')
    # 删除多余空格
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def convert_to_traditional(text):
    """将文本转换为繁体中文"""
    if not text:
        return text
    cc = OpenCC('s2t')  # Simplified to Traditional
    return cc.convert(text)

def extract_id_and_joke(step5_data):
    """提取id和final_best_joke"""
    results = []
    for item in step5_data:
        # 获取笑话文本并清理格式
        text = remove_format_chars(item.get('final_best_joke', ''))
        
        # 判断word_type是否为traditional，如果是则转换为繁体
        word_type = item.get('word_type', '')
        if word_type == 'traditional':
            text = convert_to_traditional(text)
        
        result = {
            'id': item.get('id', ''),
            'text': text
        }
        results.append(result)
    return results

def main():
    # 文件路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    step5_path = os.path.join(base_dir, 'output', 'step5_final_results.json')
    output_path = os.path.join(base_dir, 'output', 'step5_submit.tsv')
    
    print("开始处理数据...")
    print(f"读取step5_final_results.json: {step5_path}")
    
    # 加载数据
    step5_data = load_json(step5_path)
    print(f"共有 {len(step5_data)} 条数据")
    
    # 提取id和final_best_joke
    results = extract_id_and_joke(step5_data)
    
    # 保存为TSV文件
    print(f"保存TSV文件到: {output_path}")
    save_tsv(results, output_path)
    
    print(f"\n处理完成！")
    print(f"已提取 {len(results)} 条数据")
    print(f"输出文件: {output_path}")

if __name__ == '__main__':
    main()
