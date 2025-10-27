import os
import json
import yaml

import openai

with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)
def get_today():
    return config['today']

API_KEY = config['api_key']  # 请填写你的API key
API_BASE = 'https://yunwu.ai/v1'
MODEL = 'deepseek-v3'  # 可根据实际模型调整
client = openai.OpenAI(
    api_key=API_KEY,
    base_url=API_BASE
)
CHARACTER_DIR = './character'
LOG_DIR = './log'
LOG_FILE = os.path.join(LOG_DIR, 'log.md')
AGENT_JSON_FILES = [f for f in os.listdir(CHARACTER_DIR) if f.startswith('agent_') and f.endswith('.json')]
GOD_MD_FILE = os.path.join(CHARACTER_DIR, 'god_agent.md')
GOD_JSON_FILE = os.path.join(CHARACTER_DIR, 'god_agent.json')

def call_llm(prompt, agent_name):
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": f"你是{agent_name}，请根据人设和历史生成今天的行动。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"API调用失败: {e}")
        return ""

def generate_today_event():
    # 读取god_agent.md内容，调用LLM生成今日大事件
    if os.path.exists(GOD_MD_FILE):
        with open(GOD_MD_FILE, 'r', encoding='utf-8') as f:
            prompt = f.read()
    else:
        prompt = "请生成今日大事件。"
    event = call_llm(prompt, 'god_agent')
    # 保存到god_agent.json
    today = get_today()
    god_event = {
        "time": today,
        "event": event[:20],
        "details": event
    }
    with open(GOD_JSON_FILE, 'a', encoding='utf-8') as f:
        json.dump(god_event, f, ensure_ascii=False, indent=2)
    return god_event

def generate_agent_action(agent_name):
    # 读取人设和历史，调用LLM生成行动
    md_file = os.path.join(CHARACTER_DIR, f"{agent_name}.md")
    json_file = os.path.join(CHARACTER_DIR, f"{agent_name}.json")
    prompt = ""
    if os.path.exists(md_file):
        with open(md_file, 'r', encoding='utf-8') as f:
            prompt += f.read()
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            prompt += '\n历史：' + f.read()
    action = call_llm(prompt, agent_name)
    today = get_today()
    agent_event = {
        "time": today,
        "event": action[:20],
        "details": action
    }
    with open(json_file, 'a', encoding='utf-8') as f:
        json.dump(agent_event, f, ensure_ascii=False, indent=2)
    return agent_event

def write_log(god_event, agent_events):
    today = get_today()
    with open(LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f"\n## {today} 日志\n")
        f.write(f"- 大事件: {god_event['event']}\n  详细: {god_event['details']}\n")
        for agent, event in agent_events.items():
            f.write(f"- {agent} 行动: {event['event']}\n  详细: {event['details']}\n")

def renew_day():
    # 更新config.yaml中的today为下一天
    from datetime import datetime, timedelta
    today_str = get_today()
    today_date = datetime.strptime(today_str, '%Y-%m-%d')
    next_date = today_date + timedelta(days=1)
    next_str = next_date.strftime('%Y-%m-%d')
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    config['today'] = next_str
    with open('config.yaml', 'w', encoding='utf-8') as f:
        yaml.dump(config, f)

def main():
    for i in range(5):  # 模拟5天
        print('==== infinite_fortune 世界观模拟器 ===')
        god_event = generate_today_event()
        print('今日大事件:', god_event['event'])
        agent_events = {}
        for agent_file in AGENT_JSON_FILES:
            agent_name = agent_file.replace('.json', '')
            agent_events[agent_name] = generate_agent_action(agent_name)
            print(f"{agent_name} 行动: {agent_events[agent_name]['event']}")
        write_log(god_event, agent_events)
        print('今日流程已记录到日志。')
        renew_day()

if __name__ == '__main__':
    main()
