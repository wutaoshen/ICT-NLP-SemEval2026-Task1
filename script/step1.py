#step1.py 实现根据新闻标题搜索新闻内容并总结的功能
import os
from openai import OpenAI
import json
from opencc import OpenCC
import time

# 配置 DashScope 的 OpenAI 兼容端点
DASHSCOPE_API_KEY = ""  # 替换为你的 DashScope API Key
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"  # 固定兼容端点

# 初始化 OpenAI 客户端
client = OpenAI(
    api_key=DASHSCOPE_API_KEY,
    base_url=BASE_URL  # 指向 DashScope 的兼容端点
)

cc = OpenCC('s2tw')  # 简体到繁体中文转换

def news_content_summary(input_file, output_file):
    """
    适用于输入文件是JSON数组格式：[{...}, {...}, ...]
    """
    # 读取原始JSON文件
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    system_content = """你是一个专业的新闻摘要助手。请将新闻内容总结为200字左右的摘要。
    要求:
    1. 字数控制在180-220字之间
    2. 提取核心信息:何人、何事、何时、何地、为何、如何
    3. 保持客观中立,不添加主观评论
    4. 保留关键数据、时间、人名等重要信息
    5. 按重要性排序,最重要的信息放在开头
    6. 语言简洁流畅,避免冗余
    输出格式:
    直接输出摘要正文,无需标题或分段。"""
    #print(cc.convert(system_content))
    # 处理每条数据
    processed_data = []
    for item in data:
        item_type = item.get('word_type','')
        print(item_type)
        if item.get('input_type','') != "新闻标题":
            processed_data.append(item)
            continue
        prompt = f"搜索新闻“{item.get('news_headline', '')}”，并使用200字左右总结其中的核心内容。"
        
        max_retries = 3
        retry_delay = 2
        api_response = None
        api_success = False
        for attempt in range(max_retries):
            try:
                print(f"第 {attempt + 1} 次尝试调用API...")
                response = client.chat.completions.create(
                    model="qwen-max",  # 可选：qwen-plus, qwen-turbo
                    messages=[
                        {"role": "system", "content": system_content},
                        {"role": "user", "content": prompt}
                    ],
                    extra_body={"enable_search": True,"enable_thinking": True,"top_k" :40,},
                    temperature= 0.3,  # 低温度保证稳定性和准确性
                    top_p=0.9,       # 适度的采样范围
                    max_tokens=500,
                )
                api_response = response
                print("API调用成功!")
                api_success = True
                break  # 成功则跳出重试循环
            except Exception as e:
                error_message = str(e)
                print(f"第 {attempt + 1} 次调用失败: {error_message}")
                
                # 检查是否是内容审核错误
                if "data_inspection_failed" in error_message or "inappropriate content" in error_message:
                    print("检测到内容审核失败，准备重试...")
                    
                    if attempt < max_retries - 1:
                        print(f"等待 {retry_delay} 秒后重试...")
                        time.sleep(retry_delay)
                    else:
                        print(f"已达到最大重试次数({max_retries})，放弃重试")
                        break
                else:
                    # 其他类型错误直接抛出
                    print("遇到非内容审核错误，停止重试")
                    break

        if api_success:
            if item_type == "traditional":
                news_summary = cc.convert(api_response.choices[0].message.content.strip())
            else:
                news_summary = api_response.choices[0].message.content.strip()
            print(news_summary)
            new_item = {
                'id': item.get('id', ''),
                'news_headline': item.get('news_headline', ''),
                'keyword1': item.get('keyword1', ''),
                'keyword2': item.get('keyword2', ''),
                'input_type': item.get('input_type', ''),
                'word_type': item.get('word_type', ''),
                'news_summary': news_summary,
            }
            processed_data.append(new_item)
        else:
            processed_data.append(item)
    
    # 写入新的JSON文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)
    
    print(f"成功处理 {len(processed_data)} 条数据")

if __name__ == "__main__":
    input_file = "../data/eval.json"
    output_file = "../output/step1.json"
    news_content_summary(input_file, output_file)