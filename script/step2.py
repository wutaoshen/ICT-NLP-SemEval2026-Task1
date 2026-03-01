#step2.py 从新闻标题以及新闻内容中提取关键词并进行联想
import os
from openai import OpenAI
import json
from opencc import OpenCC

import dashscope
from dashscope import Generation
from typing import Dict, List, Any

# 配置您的API密钥（请替换为实际密钥）
dashscope.api_key = ""

def extract_humor_keywords(sentence1: str, sentence2: str) -> Dict[str, Any]:
    prompt = f"""
    你是一个专业喜剧编剧，擅长从新闻中发现幽默潜质。请严格按以下步骤操作：
    
    1. 从新闻标题中提取【一个】独特/荒诞/有双关潜力的关键词
       - 避免普通名词（如"人"、"东西"）
       - 优先选择：反常识组合、拟人化对象、意外属性、文化梗
       - 新闻标题：「{sentence1}」
    
    2. 从新闻内容总结中提取【一个】与第一个词不同但同样独特/荒诞/有双关潜力的关键词
       - 要求与第一个词形成反差（如：严肃vs幼稚、科技vs原始）
       - 新闻内容总结：「{sentence2}」
    
    3. 为每个关键词进行联想（各3个）：
       - 联想词应与关键词相关，但更具创意和幽默潜力
       - 例：关键词"咖啡" → ["茶", "打工人", "熬夜"]

    4. 【严格遵守】输出必须是纯JSON，包含以下字段：
       {{
         "sentence1_keyword": "字符串",
         "sentence2_keyword": "字符串",
         "associations1": ["字符串1", "字符串2", "字符串3"],
         "associations2": ["字符串1", "字符串2", "字符串3"]
       }}
    """
    
    try:
        # 调用API并强制JSON输出
        response = Generation.call(
            model="qwen-max",  # 推荐使用qwen-max保证质量
            prompt=prompt,
            response_format={"type": "json_object"},  # 关键：强制JSON格式
            temperature=0.85,  # 增加创意性
            top_p=0.9
        )
        
        # 验证API响应
        if response.status_code != 200:
            return {
                "sentence1_keyword": sentence1.split()[0] if sentence1 else "默认词1",
                "sentence2_keyword": sentence2.split()[0] if sentence2 else "默认词2",
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise Exception(f"API请求失败: {response.code} - {response.message}")
        
        # 解析JSON响应
        result = json.loads(response.output.text)
        
        # 验证关键字段存在
        required_keys = ["sentence1_keyword", "sentence2_keyword", 
                         "associations1", "associations2"]
        if not all(key in result for key in required_keys):
            return {
                "sentence1_keyword": sentence1.split()[0] if sentence1 else "默认词1",
                "sentence2_keyword": sentence2.split()[0] if sentence2 else "默认词2",
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise ValueError("响应缺少必要字段")
        
        # 验证联想词数量
        if len(result["associations1"]) != 3 or len(result["associations2"]) != 3:
            return {
                "sentence1_keyword": sentence1.split()[0] if sentence1 else "默认词1",
                "sentence2_keyword": sentence2.split()[0] if sentence2 else "默认词2",
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise ValueError("联想词数量不符合要求")
        
        return result
    
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # 失败时返回安全的默认结构（实际应用中可添加重试逻辑）
        print(f"解析错误: {str(e)}，使用备用方案")
        return {
            "sentence1_keyword": sentence1.split()[0] if sentence1 else "默认词1",
            "sentence2_keyword": sentence2.split()[0] if sentence2 else "默认词2",
            "associations1": ["意外转折", "夸张变形", "身份错位"],
            "associations2": ["逻辑反转", "时代错位", "动物拟人"]
        }

def keywords_associations(keyword1: str, keyword2: str) -> Dict[str, Any]:
    prompt = f"""
    你是一个专业喜剧编剧，擅长从词语中发现幽默潜质并进行联想。请严格按以下步骤操作：
    
    1. 为每个关键词进行联想（各3个）：
       - 联想词应与关键词相关，但更具创意和幽默潜力
       - 例：关键词"咖啡" → ["茶", "打工人", "熬夜"]
       - 关键词1：「{keyword1}」
       - 关键词2：「{keyword2}」

    2. 【严格遵守】输出必须是纯JSON，包含以下字段：
       {{
         "keyword1": "字符串",
         "keyword2": "字符串",
         "associations1": ["字符串1", "字符串2", "字符串3"],
         "associations2": ["字符串1", "字符串2", "字符串3"]
       }}
    """
    
    try:
        # 调用API并强制JSON输出
        response = Generation.call(
            model="qwen-max",  # 推荐使用qwen-max保证质量
            prompt=prompt,
            response_format={"type": "json_object"},  # 关键：强制JSON格式
            temperature=0.85,  # 增加创意性
            top_p=0.9
        )
        
        # 验证API响应
        if response.status_code != 200:
            return {
                "keyword1": keyword1,
                "keyword2": keyword2,
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise Exception(f"API请求失败: {response.code} - {response.message}")
        
        # 解析JSON响应
        result = json.loads(response.output.text)
        
        # 验证关键字段存在
        required_keys = ["keyword1", "keyword2", 
                         "associations1", "associations2"]
        if not all(key in result for key in required_keys):
            return {
                "keyword1": keyword1,
                "keyword2": keyword2,
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise ValueError("响应缺少必要字段")
        
        # 验证联想词数量
        if len(result["associations1"]) != 3 or len(result["associations2"]) != 3:
            return {
                "keyword1": keyword1,
                "keyword2": keyword2,
                "associations1": ["意外转折", "夸张变形", "身份错位"],
                "associations2": ["逻辑反转", "时代错位", "动物拟人"]
            }
            #raise ValueError("联想词数量不符合要求")
        
        return result
    
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        # 失败时返回安全的默认结构（实际应用中可添加重试逻辑）
        print(f"解析错误: {str(e)}，使用备用方案")
        return {
            "keyword1": keyword1,
            "keyword2": keyword2,
            "associations1": ["意外转折", "夸张变形", "身份错位"],
            "associations2": ["逻辑反转", "时代错位", "动物拟人"]
        }

def news_keywords(input_file, output_file):
    """
    适用于输入文件是JSON数组格式：[{...}, {...}, ...]
    """
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    processed_data = []
    for item in data:
        item_type = item.get('word_type','')
        print(item_type)
        if item.get('input_type','') == "新闻标题":
            humor_data = extract_humor_keywords(item.get('news_headline'), item.get('news_summary'))
            if item.get('word_type','') == 'traditional':
                cc = OpenCC('s2tw')
                humor_data['sentence1_keyword'] = cc.convert(humor_data['sentence1_keyword'])
                humor_data['sentence2_keyword'] = cc.convert(humor_data['sentence2_keyword'])
                humor_data['associations1'] = [cc.convert(word) for word in humor_data['associations1']]
                humor_data['associations2'] = [cc.convert(word) for word in humor_data['associations2']]
            print(humor_data)
            new_item = {
                    'id': item.get('id', ''),
                    'news_headline': item.get('news_headline', ''),
                    'keyword1': humor_data['sentence1_keyword'],
                    'keyword2': humor_data['sentence2_keyword'],
                    'input_type': item.get('input_type', ''),
                    'word_type': item.get('word_type', ''),
                    'news_summary': item.get('news_summary', ''),
                    'keyword1_associations': humor_data['associations1'],
                    'keyword2_associations': humor_data['associations2'],
            }
            processed_data.append(new_item)
        else:
            humor_data = keywords_associations(item.get('keyword1'), item.get('keyword2'))
            print(humor_data)
            new_item = {
                    'id': item.get('id', ''),
                    'news_headline': item.get('news_headline', ''),
                    'keyword1': humor_data['keyword1'],
                    'keyword2': humor_data['keyword2'],
                    'input_type': item.get('input_type', ''),
                    'word_type': item.get('word_type', ''),
                    'keyword1_associations': humor_data['associations1'],
                    'keyword2_associations': humor_data['associations2'],
            }
            processed_data.append(new_item)
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"成功处理 {len(processed_data)} 条数据")

# 示例使用
if __name__ == "__main__":
    input_file = "../output/step1.json"
    output_file = "../output/step2.json"
    news_keywords(input_file, output_file)