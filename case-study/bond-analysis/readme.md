# 📊 信用债发行数据分析入门教程

## 🎯 教程目标
通过分析2025年1-6月信用债发行数据，学习Python数据分析的基础技能：
- 数据清洗和预处理
- 探索性数据分析（EDA）
- 数据可视化
- 基础统计分析
- 金融数据的业务理解

## 📚 需要的Python库
```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体显示
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
sns.set_style("whitegrid")
```

## 1️⃣ 数据加载与初步探索

### 1.1 加载数据
```python
# 读取Excel文件
df = pd.read_excel('2025年1-6月信用债发行详情.xlsx')

# 查看数据基本信息
print("数据形状:", df.shape)
print("列名:", list(df.columns))
```

### 1.2 数据概览
```python
# 查看前几行数据
df.head()

# 查看数据类型和缺失值
df.info()

# 查看数值型列的统计描述
df.describe()
```

## 2️⃣ 数据清洗与预处理

### 2.1 处理发行量数据
```python
# 发行量列包含 "20/20" 这样的格式，我们需要提取实际发行量
def extract_issue_amount(amount_str):
    if pd.isna(amount_str):
        return np.nan
    if '/' in str(amount_str):
        # 取斜杠前的数字作为实际发行量
        return float(str(amount_str).split('/')[0])
    return float(amount_str)

df['实际发行量'] = df['发行量(亿)'].apply(extract_issue_amount)
```

### 2.2 处理发行利率数据
```python
# 发行利率可能包含缺失值，我们先查看一下
print("发行利率缺失值数量:", df['发行利率'].isna().sum())

# 将发行利率转换为数值型
df['发行利率_数值'] = pd.to_numeric(df['发行利率'], errors='coerce')
```

### 2.3 处理日期数据
```python
# 将发行日转换为日期格式
df['发行日期'] = pd.to_datetime(df['发行日'], errors='coerce')

# 提取月份信息
df['发行月份'] = df['发行日期'].dt.month
```

## 3️⃣ 探索性数据分析（EDA）

### 3.1 发行状态分析
```python
# 分析发行成功率
status_counts = df['标签'].value_counts()

plt.figure(figsize=(8, 6))
plt.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%')
plt.title('信用债发行状态分布')
plt.show()

print("发行成功率:", status_counts['成功'] / status_counts.sum() * 100, "%")
```

### 3.2 债券类型分析
```python
# 分析不同债券类型的发行情况
bond_types = df[df['标签'] == '成功']['债券类型'].value_counts().head(10)

plt.figure(figsize=(12, 6))
bond_types.plot(kind='bar')
plt.title('前10大债券类型发行数量')
plt.xlabel('债券类型')
plt.ylabel('发行数量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()
```

### 3.3 发行规模分析
```python
# 分析发行规模分布
successful_bonds = df[df['标签'] == '成功'].copy()

plt.figure(figsize=(12, 4))

# 发行规模直方图
plt.subplot(1, 2, 1)
plt.hist(successful_bonds['实际发行量'].dropna(), bins=30, alpha=0.7)
plt.title('发行规模分布')
plt.xlabel('发行量(亿元)')
plt.ylabel('频次')

# 发行规模箱线图
plt.subplot(1, 2, 2)
plt.boxplot(successful_bonds['实际发行量'].dropna())
plt.title('发行规模箱线图')
plt.ylabel('发行量(亿元)')

plt.tight_layout()
plt.show()

# 统计描述
print("发行规模统计:")
print(successful_bonds['实际发行量'].describe())
```

### 3.4 信用评级分析
```python
# 分析主体评级分布
def extract_main_rating(rating_str):
    if pd.isna(rating_str):
        return np.nan
    return rating_str.split('/')[0]  # 取主体评级

successful_bonds['主体评级'] = successful_bonds['主/债评级'].apply(extract_main_rating)
rating_counts = successful_bonds['主体评级'].value_counts()

plt.figure(figsize=(10, 6))
rating_counts.plot(kind='bar')
plt.title('主体评级分布')
plt.xlabel('评级')
plt.ylabel('发行数量')
plt.xticks(rotation=0)
plt.show()
```

### 3.5 发行利率分析
```python
# 分析发行利率分布
plt.figure(figsize=(12, 4))

# 发行利率直方图
plt.subplot(1, 2, 1)
plt.hist(successful_bonds['发行利率_数值'].dropna(), bins=30, alpha=0.7)
plt.title('发行利率分布')
plt.xlabel('发行利率(%)')
plt.ylabel('频次')

# 不同评级的发行利率对比
plt.subplot(1, 2, 2)
rating_groups = ['AAA', 'AA+', 'AA', 'AA-']
data_to_plot = []
labels = []

for rating in rating_groups:
    rates = successful_bonds[successful_bonds['主体评级'] == rating]['发行利率_数值'].dropna()
    if len(rates) > 0:
        data_to_plot.append(rates)
        labels.append(rating)

if data_to_plot:
    plt.boxplot(data_to_plot, labels=labels)
    plt.title('不同评级发行利率对比')
    plt.xlabel('主体评级')
    plt.ylabel('发行利率(%)')

plt.tight_layout()
plt.show()
```

### 3.6 地域分析
```python
# 分析各省份发行情况
province_counts = successful_bonds['省份'].value_counts().head(15)

plt.figure(figsize=(12, 6))
province_counts.plot(kind='bar')
plt.title('各省份信用债发行数量TOP15')
plt.xlabel('省份')
plt.ylabel('发行数量')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# 计算各省份平均发行规模
province_avg_amount = successful_bonds.groupby('省份')['实际发行量'].mean().sort_values(ascending=False).head(10)
print("各省份平均发行规模TOP10:")
print(province_avg_amount)
```

### 3.7 城投债分析
```python
# 分析城投债与非城投债的情况
chengtou_analysis = successful_bonds['是否城投'].value_counts()

plt.figure(figsize=(12, 4))

# 城投债占比
plt.subplot(1, 2, 1)
plt.pie(chengtou_analysis.values, labels=chengtou_analysis.index, autopct='%1.1f%%')
plt.title('城投债占比')

# 城投债与非城投债的平均发行规模对比
plt.subplot(1, 2, 2)
avg_amounts = successful_bonds.groupby('是否城投')['实际发行量'].mean()
avg_amounts.plot(kind='bar')
plt.title('城投债vs非城投债平均发行规模')
plt.xlabel('是否城投')
plt.ylabel('平均发行量(亿元)')
plt.xticks(rotation=0)

plt.tight_layout()
plt.show()
```

### 3.8 时间趋势分析
```python
# 分析月度发行趋势
monthly_trend = successful_bonds.groupby('发行月份').agg({
    '实际发行量': ['count', 'sum', 'mean']
}).round(2)

monthly_trend.columns = ['发行数量', '总发行量', '平均发行量']

plt.figure(figsize=(12, 4))

# 月度发行数量趋势
plt.subplot(1, 2, 1)
monthly_trend['发行数量'].plot(kind='line', marker='o')
plt.title('月度发行数量趋势')
plt.xlabel('月份')
plt.ylabel('发行数量')
plt.grid(True)

# 月度总发行量趋势
plt.subplot(1, 2, 2)
monthly_trend['总发行量'].plot(kind='line', marker='o', color='red')
plt.title('月度总发行量趋势')
plt.xlabel('月份')
plt.ylabel('总发行量(亿元)')
plt.grid(True)

plt.tight_layout()
plt.show()

print("月度发行统计:")
print(monthly_trend)
```

## 4️⃣ 深入分析：相关性探索

### 4.1 评级与发行利率的关系
```python
# 创建评级数值映射
rating_map = {'AAA': 9, 'AA+': 8, 'AA': 7, 'AA-': 6, 'A+': 5, 'A': 4, 'A-': 3}
successful_bonds['评级数值'] = successful_bonds['主体评级'].map(rating_map)

# 计算相关系数
correlation = successful_bonds[['评级数值', '发行利率_数值']].corr()
print("评级与发行利率相关系数:")
print(correlation)

# 散点图展示关系
plt.figure(figsize=(10, 6))
plt.scatter(successful_bonds['评级数值'], successful_bonds['发行利率_数值'], alpha=0.6)
plt.xlabel('评级数值(数值越大评级越高)')
plt.ylabel('发行利率(%)')
plt.title('信用评级与发行利率关系')
plt.grid(True)
plt.show()
```

### 4.2 发行规模与发行利率的关系
```python
# 分析发行规模对发行利率的影响
plt.figure(figsize=(10, 6))
plt.scatter(successful_bonds['实际发行量'], successful_bonds['发行利率_数值'], alpha=0.6)
plt.xlabel('发行规模(亿元)')
plt.ylabel('发行利率(%)')
plt.title('发行规模与发行利率关系')
plt.grid(True)
plt.show()

# 计算相关系数
size_rate_corr = successful_bonds[['实际发行量', '发行利率_数值']].corr()
print("发行规模与发行利率相关系数:")
print(size_rate_corr)
```

## 5️⃣ 业务洞察与总结

### 5.1 关键发现总结
```python
print("=== 信用债市场分析总结 ===")
print(f"1. 总发行数量: {len(successful_bonds)} 只")
print(f"2. 总发行规模: {successful_bonds['实际发行量'].sum():.1f} 亿元")
print(f"3. 平均发行规模: {successful_bonds['实际发行量'].mean():.1f} 亿元")
print(f"4. 平均发行利率: {successful_bonds['发行利率_数值'].mean():.2f}%")
print(f"5. 城投债占比: {(successful_bonds['是否城投'] == '是').mean()*100:.1f}%")
print(f"6. 最活跃省份: {successful_bonds['省份'].mode()[0]}")
print(f"7. 最常见债券类型: {successful_bonds['债券类型'].mode()[0]}")
```

### 5.2 投资建议框架
```python
# 基于数据分析的简单投资建议框架
def investment_suggestion(rating, province, bond_type, issue_amount):
    """
    基于历史数据给出简单的投资建议
    """
    suggestions = []
    
    # 评级建议
    if rating in ['AAA', 'AA+']:
        suggestions.append("✅ 高信用评级，违约风险较低")
    elif rating in ['AA', 'AA-']:
        suggestions.append("⚠️ 中等信用评级，需关注发行人财务状况")
    else:
        suggestions.append("❌ 较低信用评级，风险较高")
    
    # 规模建议
    avg_amount = successful_bonds['实际发行量'].mean()
    if issue_amount > avg_amount * 2:
        suggestions.append("📈 大规模发行，流动性可能较好")
    elif issue_amount < avg_amount * 0.5:
        suggestions.append("📉 小规模发行，流动性可能较差")
    
    return suggestions

# 示例使用
example_suggestions = investment_suggestion('AAA', '江苏', 'MTN', 10)
print("投资建议示例:")
for suggestion in example_suggestions:
    print(suggestion)
```

## 6️⃣ 练习题

### 初级练习
1. 计算不同债券类型的平均发行利率
2. 找出发行规模最大的前10只债券
3. 分析哪个月份发行的债券数量最多

### 中级练习
1. 比较国企、民企、央企的发行利率差异
2. 分析不同行业的发行规模分布
3. 研究增信方式对发行利率的影响

### 高级练习
1. 构建一个简单的信用评级预测模型
2. 分析募资用途与发行利率的关系
3. 创建一个债券投资风险评估指标

## 📖 学习要点总结

通过这个教程，你学会了：

1. **数据处理技能**
   - 使用pandas读取和处理Excel数据
   - 处理缺失值和异常值
   - 数据类型转换和格式化

2. **数据分析技能**
   - 描述性统计分析
   - 分组聚合分析
   - 相关性分析

3. **数据可视化技能**
   - 使用matplotlib和seaborn创建图表
   - 柱状图、饼图、直方图、箱线图、散点图
   - 图表美化和中文显示

4. **金融业务理解**
   - 信用债的基本概念
   - 评级、利率、发行规模等关键指标
   - 城投债的特点
   - 市场风险评估思路

## 🚀 进阶方向

- 学习更高级的统计分析方法
- 掌握机器学习在金融中的应用
- 深入研究债券定价模型
- 学习风险管理和投资组合理论