# verification_3_2.py
import pandas as pd
from scipy import stats

df = pd.read_excel('output/khn_flight_processed.xlsx')

# 生成日期类型
df['日期类型'] = df['星期'].isin(['周六', '周日']).map({True: '周末', False: '工作日'})

# 核心统计
stats_summary = df.groupby('日期类型').agg(
    延误率=('isDelay', lambda x: x.mean() * 100),
    平均延误=('delayMin', 'mean'),
    航班量=('航班号', 'count')
).round(2)

# 航班量减少百分比
flight_reduction = (1 - stats_summary.loc['周末', '航班量'] / stats_summary.loc['工作日', '航班量']) * 100

# t检验
workday_delays = df[df['日期类型'] == '工作日']['delayMin']
weekend_delays = df[df['日期类型'] == '周末']['delayMin']
t_stat, p_value = stats.ttest_ind(workday_delays, weekend_delays)

print("图3-2 数据核查结果:")
print(stats_summary)
print(f"\n周末航班量减少: {flight_reduction:.1f}%")
print(f"t检验: t={t_stat:.3f}, p={p_value:.3f}")
print(f"差异显著性: {'p<0.01' if p_value<0.01 else 'p>=0.01'}")

# 3-2数据核查已经包括在3-2.py中
# 此代码有误无需运行
