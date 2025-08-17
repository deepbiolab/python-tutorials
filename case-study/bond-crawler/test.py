from tqdm import tqdm
import ast
import requests
import pandas as pd
import time

def get_headers():
    """生成随机请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://fund.eastmoney.com/data/fundranking.html'
    }


def get_total_pages():
    """
    获取数据总页数
    提示：
    1. 构造请求URL和参数
    2. 发送请求获取响应
    3. 提取并解析响应提取总页数
    """
    url = "https://fund.eastmoney.com/data/rankhandler.aspx"
    payload = {
        "op":"ph",
        "sc":"1nzf",
        "st":"desc",
        "pi":"1", # page index
        "pn":"50",
        "dx":"1",
        "v":"0.1792452691132982"
    }
    response = requests.get(url, params=payload, headers=get_headers())
    long_str = response.text
    tot_pages = int(long_str.split('allPages:')[1].split(',')[0].strip())
    return tot_pages


def parse_fund_data(text):
    """
    解析返回的文本数据
    提示：
    1. 分割文本提取数据部分
    2. 遍历每条基金记录
    3. 提取所需字段
    4. 处理特殊格式（如百分比）
    """
    str_list = text.split('datas:')[1].split(',allRecords')[0]
    data_list = ast.literal_eval(str_list)
    
    fund_series_list = []
    for item in data_list:
        fields = item.split(',')
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
        fund_series_list.append(pd.Series(fund))
    df = pd.DataFrame(fund_series_list)
    return df

def get_single_page(page):
    """
    获取指定页码的数据
    提示：
    1. 构造请求参数
    2. 发送请求
    3. 调用解析函数处理响应
    4. 处理可能的异常
    """
    url = "https://fund.eastmoney.com/data/rankhandler.aspx"

    params = {
        "op":"ph",
        "sc":"1nzf",
        "st":"desc",
        "pi": page,
        "pn":"50",
        "dx":"1",
        "v":"0.1792452691132982"
    }

    response = requests.get(url, params=params, headers=get_headers())
    df = parse_fund_data(response.text)
    return df

def save_to_csv(data, filename='fund_data.csv'):
    """
    将数据保存为CSV文件
    提示：
    1. 使用pandas DataFrame处理数据
    2. 注意中文编码问题
    """
    data.to_csv(filename, index=False)
    return

def main():
    """
    主函数：协调各个功能模块
    提示：
    1. 获取总页数
    2. 循环获取每页数据
    3. 添加进度显示
    4. 实现延时机制
    5. 保存最终数据
    """
    tot_pages = get_total_pages()

    df_list = []
    for i in tqdm(range(1, tot_pages+1)):
        df = get_single_page(page=i)
        df_list.append(df)
        save_to_csv(df, filename=f'results/fund_data_{i}.csv')

    # combine multiple dfs into one
    data = pd.concat(df_list, ignore_index=True)
    save_to_csv(data, filename='fund_data.csv')
    return
    

if __name__ == '__main__':
    main()