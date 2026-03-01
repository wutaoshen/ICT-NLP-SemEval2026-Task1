# step4_evaluate.py 评估四个模型生成的笑话，选出最幽默的一个
import dashscope
from dashscope import Generation
import json
import time
import re

# 设置DashScope API密钥
dashscope.api_key = ""

def parse_json_response(content):
    """
    解析API返回的JSON内容，支持markdown格式
    参考error_transform.py的处理方式
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

def evaluate_jokes_news(news_id, news_headline, four_jokes, evaluator_model="qwen-max"):
    """
    评估基于新闻标题生成的笑话
    :param news_id: 新闻ID
    :param news_headline: 新闻标题
    :param four_jokes: 包含4个笑话的字典，格式 {model_name: joke_text}
    :param evaluator_model: 用于评估的模型名称
    :return: 评估结果的JSON对象
    """
    
    # 构建系统提示（新闻类型）
    system_prompt = """你是一位专业的幽默评审专家，精通中文笑话的鉴赏与评估。

你的任务是：
1. 阅读新闻标题和4个不同模型生成的笑话
2. 从以下七个维度综合评估每个笑话
3. 为每个笑话给出简短的评价（80字以内）
4. 最终选出你认为最幽默的一个笑话

评估维度（请综合考虑）：

【核心维度】
1. **可理解性**：判断文本是否能够被理解其基本含义。如果内容混乱、语义不清或完全无法理解，请在评价中说明原因并降低整体评分。

2. **冒犯性/适当性**：判断是否包含冒犯性内容（种族歧视、性别偏见、对弱势群体的刻板印象、低俗内容等）。如果内容健康积极则无需特别说明，如果存在冒犯性请明确指出。

3. **笑话识别**：判断这段文字是否明确意图作为笑话呈现（即使幽默效果不佳）。如果只是普通陈述或非幽默内容，请在评价中指出。

4. **趣味性**（核心权重）：在确认是笑话的前提下，评估其幽默程度：
   - 完全不好笑，毫无幽默感
   - 略显尴尬，勉强算笑话但效果很差
   - 一般水平，能引起轻微笑意
   - 较为有趣，能引发明显笑声
   - 极其有趣，令人捧腹大笑

5. **创意性**：评估笑话的原创性和新颖程度，包括构思是否巧妙、角度是否独特、是否有意想不到的转折或创新元素。

6. **相关性**：笑话内容是否与新闻主题保持合理关联。

7. **流畅性**：语言表达是否通顺自然，逻辑结构是否清晰完整。

【严格遵守】输出必须是纯JSON格式，包含以下字段：
{
  "evaluations": {
    "model1": "对笑话1的综合评价（需涵盖可理解性、适当性、是否为笑话、趣味性等关键维度）",
    "model2": "对笑话2的综合评价",
    "model3": "对笑话3的综合评价",
    "model4": "对笑话4的综合评价"
  },
  "best_joke": "最幽默的模型名称(model1/model2/model3/model4)",
  "reason": "选择该笑话的理由（需说明在趣味性、创意性等维度的突出表现，100字以内）"
}"""

    # 构建用户提示（隐藏模型来源，确保评估公正性）
    jokes_text = ""
    model_mapping = {}  # 用于映射 model1/2/3/4 到实际模型名
    for idx, (model_name, joke) in enumerate(four_jokes.items(), 1):
        model_key = f"model{idx}"
        model_mapping[model_key] = model_name
        # 不显示模型名称，避免评估偏见
        jokes_text += f"\n【笑话{idx}】\n{joke}\n"
    
    user_prompt = f"""新闻标题：{news_headline}

请评估以下4个笑话：
{jokes_text}

请按照系统提示的格式输出评估结果。"""

    return _call_evaluation_api(news_id, system_prompt, user_prompt, model_mapping, evaluator_model)

def evaluate_jokes_keywords(news_id, keyword1, keyword2, four_jokes, evaluator_model="qwen-max"):
    """
    评估基于关键词生成的笑话
    :param news_id: 数据ID
    :param keyword1: 关键词1
    :param keyword2: 关键词2
    :param four_jokes: 包含4个笑话的字典，格式 {model_name: joke_text}
    :param evaluator_model: 用于评估的模型名称
    :return: 评估结果的JSON对象
    """
    
    # 构建系统提示（关键词类型）
    system_prompt = f"""你是一位专业的幽默评审专家，精通中文笑话的鉴赏与评估。

你的任务是：
1. 阅读两个关键词（"{keyword1}"和"{keyword2}"）以及4个不同模型生成的笑话
2. 从以下八个维度综合评估每个笑话
3. 为每个笑话给出简短的评价（80字以内）
4. 最终选出你认为最幽默的一个笑话

评估维度（请综合考虑）：

【核心维度】
1. **可理解性**：判断文本是否能够被理解其基本含义。如果内容混乱、语义不清或完全无法理解，请在评价中说明原因并降低整体评分。

2. **冒犯性/适当性**：判断是否包含冒犯性内容（种族歧视、性别偏见、对弱势群体的刻板印象、低俗内容等）。如果内容健康积极则无需特别说明，如果存在冒犯性请明确指出。

3. **笑话识别**：判断这段文字是否明确意图作为笑话呈现（即使幽默效果不佳）。如果只是普通陈述或非幽默内容，请在评价中指出。

4. **趣味性**（核心权重）：在确认是笑话的前提下，评估其幽默程度：
   - 完全不好笑，毫无幽默感
   - 略显尴尬，勉强算笑话但效果很差
   - 一般水平，能引起轻微笑意
   - 较为有趣，能引发明显笑声
   - 极其有趣，令人捧腹大笑

5. **创意性**：评估笑话的原创性和新颖程度，包括构思是否巧妙、角度是否独特、是否有意想不到的转折或创新元素。

6. **关键词覆盖度**（重要）：笑话中是否明确包含两个指定关键词"{keyword1}"和"{keyword2}"。如果缺少任一关键词，请在评价中明确指出并大幅降低评分。

7. **关键词整合度**：两个关键词在笑话中的结合是否自然巧妙，是否形成有趣的关联或冲突。

8. **流畅性**：语言表达是否通顺自然，逻辑结构是否清晰完整。

【严格遵守】输出必须是纯JSON格式，包含以下字段：
{{
  "evaluations": {{
    "model1": "对笑话1的综合评价（需涵盖可理解性、适当性、是否为笑话、趣味性、关键词覆盖等关键维度）",
    "model2": "对笑话2的综合评价",
    "model3": "对笑话3的综合评价",
    "model4": "对笑话4的综合评价"
  }},
  "best_joke": "最幽默的模型名称(model1/model2/model3/model4)",
  "reason": "选择该笑话的理由（需说明在趣味性、创意性、关键词整合等维度的突出表现，100字以内）"
}}"""

    # 构建用户提示（隐藏模型来源，确保评估公正性）
    jokes_text = ""
    model_mapping = {}  # 用于映射 model1/2/3/4 到实际模型名
    for idx, (model_name, joke) in enumerate(four_jokes.items(), 1):
        model_key = f"model{idx}"
        model_mapping[model_key] = model_name
        # 不显示模型名称，避免评估偏见
        jokes_text += f"\n【笑话{idx}】\n{joke}\n"
    
    user_prompt = f"""关键词1：{keyword1}
关键词2：{keyword2}

请评估以下4个笑话（注意：笑话应该包含这两个关键词）：
{jokes_text}

请按照系统提示的格式输出评估结果。"""

    return _call_evaluation_api(news_id, system_prompt, user_prompt, model_mapping, evaluator_model)

def _call_evaluation_api(news_id, system_prompt, user_prompt, model_mapping, evaluator_model):
    """
    通用API调用函数，处理重试逻辑和结果映射
    """
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            # 调用API
            response = Generation.call(
                model=evaluator_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                extra_body={"enable_thinking": True},
                result_format="message",
                temperature=0.7,  # 适中的温度，保持评估的一致性
                top_p=0.9
            )
            
            # 解析API响应
            if response.status_code == 200:
                content = response.output.choices[0].message.content
                try:
                    # 使用增强的JSON解析函数，支持markdown格式
                    result = parse_json_response(content)
                    
                    # 将model1/2/3/4映射回实际模型名
                    if 'best_joke' in result:
                        best_model_key = result['best_joke']
                        result['best_joke'] = model_mapping.get(best_model_key, best_model_key)
                    
                    # 重新映射evaluations字段
                    if 'evaluations' in result:
                        new_evaluations = {}
                        for model_key, evaluation in result['evaluations'].items():
                            actual_model = model_mapping.get(model_key, model_key)
                            new_evaluations[actual_model] = evaluation
                        result['evaluations'] = new_evaluations
                    
                    return result
                    
                except json.JSONDecodeError as json_error:
                    if attempt < max_retries - 1:
                        print(f"[{news_id}] JSON解析失败 (尝试 {attempt + 1}/{max_retries}): {str(json_error)}")
                        time.sleep(retry_delay)
                        continue
                    else:
                        print(f"[{news_id}] JSON解析失败，已达最大重试次数")
                        return {
                            "error": "JSON解析失败",
                            "raw_response": content,
                            "attempts": max_retries
                        }
            else:
                if attempt < max_retries - 1:
                    print(f"[{news_id}] API调用失败 (尝试 {attempt + 1}/{max_retries}): {response.code}")
                    time.sleep(retry_delay)
                    continue
                else:
                    return {
                        "error": f"API调用失败: {response.code}",
                        "message": response.message,
                        "attempts": max_retries
                    }
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"[{news_id}] 处理异常 (尝试 {attempt + 1}/{max_retries}): {str(e)}")
                time.sleep(retry_delay)
                continue
            else:
                return {
                    "error": "处理异常",
                    "details": str(e),
                    "attempts": max_retries
                }

def load_jokes_from_files(file_paths):
    """
    从多个文件中加载笑话数据（支持新闻标题和关键词两种类型）
    :param file_paths: 文件路径字典 {model_name: file_path}
    :return: 按news_id组织的笑话数据
    """
    jokes_by_id = {}
    
    for model_name, file_path in file_paths.items():
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, dict):
                data = [data]
            
            for item in data:
                news_id = item.get('id', '')
                joke = item.get('joke_result', {}).get('joke', '')
                news_headline = item.get('news_headline', '')
                input_type = item.get('input_type', '')  # 获取输入类型
                keyword1 = item.get('keyword1', '')
                keyword2 = item.get('keyword2', '')
                
                if news_id not in jokes_by_id:
                    jokes_by_id[news_id] = {
                        'news_headline': news_headline,
                        'input_type': input_type,
                        'keyword1': keyword1,
                        'keyword2': keyword2,
                        'jokes': {}
                    }
                
                jokes_by_id[news_id]['jokes'][model_name] = joke
            
            print(f"成功加载 {model_name} 的笑话数据")
            
        except Exception as e:
            print(f"加载 {model_name} 数据失败: {e}")
    
    return jokes_by_id

def evaluate_all_jokes(jokes_by_id, evaluator_models, output_file):
    """
    对所有笑话进行评估（支持新闻标题和关键词两种类型）
    :param jokes_by_id: 按ID组织的笑话数据
    :param evaluator_models: 评估模型列表
    :param output_file: 输出文件路径
    """
    results = []
    
    for news_id, data in jokes_by_id.items():
        print(f"\n正在评估 {news_id}...")
        
        input_type = data.get('input_type', '')
        four_jokes = data['jokes']
        
        # 使用多个评估模型进行评估
        evaluations_by_model = {}
        
        for evaluator_model in evaluator_models:
            print(f"  使用 {evaluator_model} 进行评估（类型：{input_type}）...")
            
            # 根据输入类型选择不同的评估函数
            if input_type == "新闻标题":
                news_headline = data['news_headline']
                evaluation = evaluate_jokes_news(news_id, news_headline, four_jokes, evaluator_model)
            elif input_type == "关键词":
                keyword1 = data['keyword1']
                keyword2 = data['keyword2']
                evaluation = evaluate_jokes_keywords(news_id, keyword1, keyword2, four_jokes, evaluator_model)
            else:
                print(f"  未知的输入类型：{input_type}，跳过评估")
                continue
            
            evaluations_by_model[evaluator_model] = evaluation
            time.sleep(1)  # 避免请求过快
        
        # 统计每个笑话被选为最佳的次数
        vote_count = {}
        for model_name in four_jokes.keys():
            vote_count[model_name] = 0
        
        for evaluator_model, evaluation in evaluations_by_model.items():
            if 'best_joke' in evaluation:
                best = evaluation['best_joke']
                if best in vote_count:
                    vote_count[best] += 1
        
        # 选出得票最多的笑话
        final_best = max(vote_count, key=vote_count.get)
        
        result = {
            'id': news_id,
            'input_type': input_type,
            'news_headline': data.get('news_headline', ''),
            'keyword1': data.get('keyword1', ''),
            'keyword2': data.get('keyword2', ''),
            'jokes': four_jokes,
            'evaluations_by_model': evaluations_by_model,
            'vote_count': vote_count,
            'final_best_joke': final_best
        }
        
        results.append(result)
        
        print(f"  评估完成，最幽默的笑话：{final_best} (得票: {vote_count[final_best]}/{len(evaluator_models)})")
    
    # 保存结果
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n所有评估完成！结果已保存到 {output_file}")
    
    # 统计总体结果
    print("\n=== 总体统计 ===")
    total_votes = {}
    for result in results:
        for model_name, votes in result['vote_count'].items():
            if model_name not in total_votes:
                total_votes[model_name] = 0
            total_votes[model_name] += votes
    
    for model_name, votes in sorted(total_votes.items(), key=lambda x: x[1], reverse=True):
        print(f"{model_name}: {votes} 票")

# ================== 使用示例 ==================
if __name__ == "__main__":
    # 定义4个模型的输出文件路径
    file_paths = {
        "qwen-max": "../output/step3_qwen-max-new.json",
        "deepseek-v3.2": "../output/step3_deepseek-v3.2-new.json",
        "kimi-k2-thinking": "../output/step3_kimi-k2-thinking-fixed.json",  # 使用修复后的文件
        "glm-4.7": "../output/step3_glm-4.7-new.json"
    }
    
    # 加载所有笑话数据
    print("正在加载笑话数据...")
    jokes_by_id = load_jokes_from_files(file_paths)
    print(f"共加载 {len(jokes_by_id)} 条新闻的笑话数据\n")
    
    # 定义评估模型（可以使用多个模型进行投票）
    evaluator_models = [
        "qwen-max",
        "deepseek-v3.2",
        "glm-4.7",
        "kimi-k2-thinking"
    ]
    
    # 输出文件
    output_file = "../output/step4_evaluation_results.json"
    
    # 开始评估
    evaluate_all_jokes(jokes_by_id, evaluator_models, output_file)
