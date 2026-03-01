import json
import os
import time
import re
from openai import OpenAI

# API配置
API_KEY = ""


def load_json(file_path):
    """加载JSON文件"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_json(data, file_path):
    """保存JSON文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def parse_json_response(content):
    """
    解析API返回的JSON内容，支持markdown格式
    参考step4_evaluate.py的处理方式
    :param content: API返回的原始内容
    :return: 解析后的JSON对象
    """
    try:
        # 首先尝试直接解析JSON
        return json.loads(content)
    except json.JSONDecodeError:
        # 如果失败，尝试移除markdown代码块标记
        try:
            cleaned = content.strip()
            # 移除markdown代码块标记（```json 和 ```）
            cleaned = re.sub(r'^```json\s*', '', cleaned)
            cleaned = re.sub(r'\s*```$', '', cleaned)
            
            # 再次尝试解析
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            # 如果仍然失败，返回错误信息
            raise json.JSONDecodeError(f"JSON解析失败: {e.msg}", e.doc, e.pos)

def get_max_vote_score(vote_count):
    """获取最高票数"""
    if not vote_count:
        return 0
    return max(vote_count.values())

def call_gpt_for_evaluation(item_data, input_type, item_id):
    """调用GPT进行评估，支持深度思考和重试机制"""
    client = OpenAI(api_key=API_KEY)
    
    # 构建提示词
#1. 基于新闻标题和摘要重新构思一则趣味性、创意性俱存且不含有冒犯与毒性的笑话
    if input_type == "新闻标题":
        prompt = f"""你是一位专业的幽默创作专家。请根据以下信息评估候选笑话：

新闻标题：{item_data.get('news_headline', '')}
新闻摘要：{item_data.get('news_summary', '')}

候选笑话：
{json.dumps(item_data['jokes'], ensure_ascii=False, indent=2)}

投票统计：
{json.dumps(item_data['vote_count'], ensure_ascii=False, indent=2)}

当前最佳笑话：{item_data['final_best_joke']}

任务：
1. 评估候选笑话的质量（趣味性、创意性、与新闻的相关性），为每条现有笑话的幽默度打分（0–10）
2. 若候选笑话中存在笑话得分大于等于6分的笑话，选择候选笑话中得分最高的一个
3. 若候选笑话中所有笑话得分均小于6分，则重新根据新闻标题和新闻摘要构思一则笑话

请以JSON格式输出：
{{
  "reason": "你的评价理由（100-200字）",
  "final_best_joke": "最终选择的笑话内容（如果选择现有笑话，直接写笑话内容；如果新创作，写你创作的笑话）"
}}
"""
    else:  # 关键词类型
        prompt = f"""你是一位专业的幽默创作专家。请根据以下信息评估候选笑话：

关键词1：{item_data.get('keyword1', '')}
关键词2：{item_data.get('keyword2', '')}

候选笑话：
{json.dumps(item_data['jokes'], ensure_ascii=False, indent=2)}

投票统计：
{json.dumps(item_data['vote_count'], ensure_ascii=False, indent=2)}

当前最佳笑话：{item_data['final_best_joke']}

任务：
1. 评估候选笑话的质量（趣味性、创意性、对关键词的运用），为每条现有笑话的幽默度打分（0–10）
2. 若候选笑话中存在笑话得分大于等于6分的笑话，选择候选笑话中得分最高的一个
3. 若候选笑话中所有笑话得分均小于6分，则重新根据关键词1和关键词2构思一则笑话，要求笑话中同时包含这两个关键词

请以JSON格式输出：
{{
  "reason": "你的评价理由（100-200字）",
  "final_best_joke": "最终选择的笑话内容（如果选择现有笑话，直接写笑话内容；如果新创作，写你创作的笑话）"
}}
"""
    
    # 重试机制
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 调用API，启用深度思考
            response = client.chat.completions.create(
                model="gpt-5.2",
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )
            
            content = response.choices[0].message.content.strip()
            result = parse_json_response(content)
            
            # 验证必要字段
            if 'reason' in result and 'final_best_joke' in result:
                return result
            else:
                raise ValueError("返回的JSON缺少必要字段")
                
        except json.JSONDecodeError as json_error:
            if attempt < max_retries - 1:
                print(f"  [{item_id}] JSON解析失败 (尝试 {attempt + 1}/{max_retries}): {str(json_error)}")
                time.sleep(retry_delay)
                continue
            else:
                print(f"  [{item_id}] JSON解析失败，已达最大重试次数")
                return None
                
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"  [{item_id}] API调用失败 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                continue
            else:
                print(f"  [{item_id}] API调用失败，已达最大重试次数: {str(e)}")
                return None
    
    return None

def process_data(step1_data, step4_data):
    """处理数据"""
    results = []
    
    for step4_item in step4_data:
        item_id = step4_item['id']
        
        # 查找对应的step1数据
        step1_item = next((item for item in step1_data if item['id'] == item_id), None)
        if not step1_item:
            print(f"警告: ID {item_id} 在step1.json中未找到")
            continue
        
        # 获取最高票数
        max_score = get_max_vote_score(step4_item.get('vote_count', {}))
        final_best_model = step4_item.get('final_best_joke', '')
        
        # 初始化结果项
        result_item = {
            "id": item_id,
            "input_type": step4_item.get('input_type', ''),
            "word_type": step1_item.get('word_type', ''),
            "news_headline": step1_item.get('news_headline', ''),
            "keyword1": step1_item.get('keyword1', ''),
            "keyword2": step1_item.get('keyword2', ''),
            "jokes": step4_item.get('jokes', {}),
            "vote_count": step4_item.get('vote_count', {}),
            "final_best_from_gpt": False,
            "final_best_joke_model": final_best_model,
            "final_best_joke": "",
            "gpt_reason": ""  # 添加gpt_reason字段，默认为空字符串
        }
        
        # 判断是否需要GPT评估
        if max_score >= 3:
            # 3分以上，直接选择最佳笑话
            result_item['final_best_from_gpt'] = False
            result_item['final_best_joke'] = step4_item['jokes'].get(final_best_model, '')
            result_item['gpt_reason'] = ''  # 未使用GPT评估，reason为空
            print(f"ID {item_id}: 最高分{max_score}分，直接采用 {final_best_model}")
        else:
            # 2分及以下，调用GPT评估
            print(f"ID {item_id}: 最高分{max_score}分，调用GPT评估...")
            
            # 准备GPT评估所需数据
            gpt_input = {
                'jokes': step4_item.get('jokes', {}),
                'vote_count': step4_item.get('vote_count', {}),
                'final_best_joke': final_best_model
            }
            
            if step4_item.get('input_type') == '新闻标题':
                gpt_input['news_headline'] = step1_item.get('news_headline', '')
                gpt_input['news_summary'] = step1_item.get('news_summary', '')
            else:
                gpt_input['keyword1'] = step1_item.get('keyword1', '')
                gpt_input['keyword2'] = step1_item.get('keyword2', '')
            
            gpt_result = call_gpt_for_evaluation(gpt_input, step4_item.get('input_type', ''), item_id)
            
            if gpt_result:
                final_joke = gpt_result['final_best_joke']
                
                # 判断是否为新创作的笑话（不在原有jokes中）
                is_from_gpt = True
                for model_name, joke_text in step4_item['jokes'].items():
                    if joke_text == final_joke:
                        is_from_gpt = False
                        result_item['final_best_joke_model'] = model_name
                        break
                
                if is_from_gpt:
                    result_item['final_best_joke_model'] = 'gpt-5.2'
                
                result_item['final_best_from_gpt'] = is_from_gpt
                result_item['final_best_joke'] = final_joke
                result_item['gpt_reason'] = gpt_result.get('reason', '')
                print(f"  GPT评估完成，{'新创作' if is_from_gpt else '选择现有'}")
                print(f"评选理由：{gpt_result.get('reason', '无')}")
            else:
                # GPT调用失败，使用原最佳笑话
                result_item['final_best_from_gpt'] = False
                result_item['final_best_joke'] = step4_item['jokes'].get(final_best_model, '')
                result_item['gpt_reason'] = ''  # GPT调用失败，reason为空
                print(f"  GPT调用失败，使用原最佳笑话")
        
        results.append(result_item)
    
    return results

def main():
    # 文件路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    step1_path = os.path.join(base_dir, 'output', 'step1.json')
    step4_path = os.path.join(base_dir, 'output', 'step4_evaluation_results.json')
    output_path = os.path.join(base_dir, 'output', 'step5_final_results.json')
    
    print("开始处理数据...")
    print(f"读取step1.json: {step1_path}")
    step1_data = load_json(step1_path)
    print(f"读取step4_evaluation_results.json: {step4_path}")
    step4_data = load_json(step4_path)
    
    print(f"\n共有 {len(step4_data)} 条数据需要处理\n")
    
    # 处理数据
    results = process_data(step1_data, step4_data)
    
    # 保存结果
    print(f"\n保存结果到: {output_path}")
    save_json(results, output_path)
    
    # 统计信息
    gpt_count = sum(1 for item in results if item['final_best_from_gpt'])
    print(f"\n处理完成！")
    print(f"总计: {len(results)} 条")
    print(f"直接采用: {len(results) - gpt_count} 条")
    print(f"GPT评估: {gpt_count} 条")

if __name__ == '__main__':
    main()
