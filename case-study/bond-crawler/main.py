import requests
import pandas as pd
from time import sleep
from random import randint
from tqdm import tqdm  # 进度条显示

def get_headers():
    """生成随机请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://fund.eastmoney.com/data/fundranking.html'
    }

def get_total_pages():
    """获取总页数"""
    url = "https://fund.eastmoney.com/data/rankhandler.aspx"
    params = {
        'op': 'ph',
        'dt': 'kf',
        'ft': 'all',
        'rs': '',
        'gs': 0,
        'sc': '1nzf',
        'st': 'desc',
        'pi': 1,
        'pn': 50,
        'dx': 1
    }
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        response.encoding = 'utf-8'
        total = int(response.text.split('allPages:')[1].split(',')[0])
        return (total // 50) + 1
    except Exception as e:
        print(f"获取总页数失败: {e}")
        return 0

def parse_fund_data(text):
    """解析基金数据"""
    funds = []
    raw_data = text.split('datas:')[1].split(',allRecords')[0].strip('[]').split('","')
    
    for item in raw_data:
        fields = item.split(',')
        if len(fields) < 20:
            continue
            
        fund = {
            '基金代码': fields[0],
            '基金简称': fields[1],
            '日期': fields[3],
            '单位净值': fields[4],
            '累计净值': fields[5],
            '日增长率': fields[6].strip('%'),
            '近1周': fields[7].strip('%'),
            '近1月': fields[8].strip('%'),
            '近3月': fields[9].strip('%'),
            '近6月': fields[10].strip('%'),
            '近1年': fields[11].strip('%'),
            '近2年': fields[12].strip('%'),
            '近3年': fields[13].strip('%'),
            '今年来': fields[14].strip('%'),
            '成立来': fields[15].strip('%'),
            '手续费': fields[18]
        }
        funds.append(fund)
    
    return funds

def get_single_page(page):
    """获取单页数据"""
    url = "https://fund.eastmoney.com/data/rankhandler.aspx"
    params = {
        'op': 'ph',
        'dt': 'kf',
        'ft': 'all',
        'rs': '',
        'gs': 0,
        'sc': '1nzf',
        'st': 'desc',
        'pi': page,
        'pn': 50,
        'dx': 1
    }
    
    try:
        response = requests.get(url, params=params, headers=get_headers())
        response.encoding = 'utf-8'
        return parse_fund_data(response.text)
    except Exception as e:
        print(f"第{page}页抓取失败: {e}")
        return []

def save_to_csv(data, filename='fund_data.csv'):
    """保存数据到CSV"""
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False, encoding='utf_8_sig')
    print(f"数据已保存至 {filename}")

def main():
    # total_pages = get_total_pages()
    total_pages = 2
    if total_pages == 0:
        return
    
    all_data = []
    print(f"共发现 {total_pages} 页数据")
    
    for page in tqdm(range(1, total_pages + 1)):
        page_data = get_single_page(page)
        all_data.extend(page_data)
        sleep(randint(1, 3))  # 随机延迟防止封IP
    
    save_to_csv(all_data)

if __name__ == '__main__':
    main()
