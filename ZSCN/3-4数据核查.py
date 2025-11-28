import pandas as pd
import numpy as np
from scipy import stats
import sys

# ==================== 配置区 ====================
DATA_PATH = 'output/khn_flight_processed.xlsx'
# 主基地航司代码（江西航空）
MAIN_AIRLINE = 'CJX'
# 延误分钟合理范围（scale过滤）
DELAY_MIN_VALID = (0, 180)  # 0-3小时
# 最小样本量阈值
MIN_SAMPLE_SIZE = 10

# ==================== 数据加载 ====================
try:
    # 修复：使用原始列名"所属航司代码"
    df = pd.read_excel(DATA_PATH, usecols=['航班号', '所属航司代码', 'delayMin'])
    print(f"数据加载成功，总样本数：{len(df)} 条")
except Exception as e:
    print(f"✗ 数据加载失败: {e}")
    sys.exit(1)

# 过滤有效延误数据
df_valid = df[
    (df['delayMin'] >= DELAY_MIN_VALID[0]) &
    (df['delayMin'] <= DELAY_MIN_VALID[1])
    ].copy()
print(f"经过scale过滤后，有效样本数：{len(df_valid)} 条")

# ==================== 航司分布统计 ====================
# 修复：按"所属航司代码"分组
airline_stats = df_valid.groupby('所属航司代码').agg(
    航班数量=('航班号', 'count'),
    平均延误=('delayMin', 'mean'),
    中位延误=('delayMin', 'median'),
    标准差=('delayMin', 'std'),
    延误_25分位=('delayMin', lambda x: np.percentile(x, 25)),
    延误_75分位=('delayMin', lambda x: np.percentile(x, 75)),
    异常值数量=(
    'delayMin', lambda x: ((x < np.percentile(x, 25) - 1.5 * (np.percentile(x, 75) - np.percentile(x, 25))) |
                           (x > np.percentile(x, 75) + 1.5 * (np.percentile(x, 75) - np.percentile(x, 25)))).sum()),
    最大延误=('delayMin', 'max')
).round(2)

# 按航班数量排序
airline_stats = airline_stats.sort_values('航班数量', ascending=False)
print("\n========== 航司延误统计表（Top15）==========")
print(airline_stats.head(15).to_string())

# ==================== 主基地航司专项分析 ====================
# 修复：使用"所属航司代码"进行判断
if MAIN_AIRLINE in df_valid['所属航司代码'].values:
    main_data = df_valid[df_valid['所属航司代码'] == MAIN_AIRLINE]['delayMin']
    other_data = df_valid[df_valid['所属航司代码'] != MAIN_AIRLINE]['delayMin']

    print(f"\n========== 主基地航司 {MAIN_AIRLINE} 深度分析 ==========")
    print(f"江西航空样本数：{len(main_data)} 条")
    print(f"外航总样本数：{len(other_data)} 条")
    print(f"江西航空中位延误：{main_data.median():.2f} 分钟")
    print(f"外航中位延误：{other_data.median():.2f} 分钟")
    print(f"江西航空异常值数量：{airline_stats.loc[MAIN_AIRLINE, '异常值数量']} 个")
    print(f"江西航空延误分布偏度：{stats.skew(main_data):.3f}")

    # Mann-Whitney U检验（非参数检验）
    if len(main_data) >= MIN_SAMPLE_SIZE and len(other_data) >= MIN_SAMPLE_SIZE:
        statistic, p_value = stats.mannwhitneyu(main_data, other_data, alternative='two-sided')
        print(f"\nMann-Whitney U检验结果：")
        print(f"统计量 U = {statistic:.0f}")
        print(f"P值 = {p_value:.4f}")
        print(f"显著性水平 α = 0.05")
        if p_value < 0.05:
            print("结论：**拒绝原假设**，江西航空与外航延误分布存在显著差异")
        else:
            print("结论：**无法拒绝原假设**，江西航空与外航延误分布无显著差异")

        # 计算效应量（r = Z / sqrt(N)）
        z_score = stats.norm.ppf(p_value / 2) if p_value < 0.5 else stats.norm.ppf(1 - p_value / 2)
        n_total = len(main_data) + len(other_data)
        effect_size = abs(z_score) / np.sqrt(n_total)
        print(f"效应量 r = {effect_size:.3f} (0.1小/0.3中/0.5大)")
    else:
        print(f"\n样本量不足（需≥{MIN_SAMPLE_SIZE}），无法进行统计检验")
else:
    print(f"错误：主基地航司代码 {MAIN_AIRLINE} 不在数据中！")

# ==================== 数据导出（供图表使用） ====================
# 修复：使用"所属航司代码"创建标签
df_valid['航司类型'] = df_valid['所属航司代码'].apply(
    lambda x: '江西航空(CJX)' if x == MAIN_AIRLINE else f'外航({x})'
)

# 只保留样本量充足的航司（前N大航司）
# 修复：使用"所属航司代码"筛选
top_airlines = airline_stats.head(8).index.tolist()  # 取前8大航司
df_chart = df_valid[df_valid['所属航司代码'].isin(top_airlines)].copy()

# 修复：重命名列以匹配图表脚本的期望
df_chart.rename(columns={'所属航司代码': '航司代码'}, inplace=True)

# 保存用于绘图的数据
df_chart.to_excel('output/fig3_4_airline_data.xlsx', index=False)
print(f"\n✓ 图表数据已保存至：output/fig3_4_airline_data.xlsx")
print(f"包含航司：{df_chart['航司代码'].unique().tolist()}")