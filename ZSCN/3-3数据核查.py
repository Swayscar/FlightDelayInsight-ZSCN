# verification_3_3_corrected.py
import pandas as pd

df = pd.read_excel('output/khn_flight_processed.xlsx')

# 重新计算：仅统计航班量≥100架次的航司（确保统计显著性）
airline_stats = df.groupby('所属航司代码').agg(
    航班量=('航班号', 'count'),
    正常航班=('延误等级', lambda x: x.isin(['准点', '轻微', '中度']).sum()),
    平均延误=('delayMin', 'mean')
)

airline_stats['正常率'] = (airline_stats['正常航班'] / airline_stats['航班量'] * 100).round(2)

# 筛选航班量≥100的航司
significant_airlines = airline_stats[airline_stats['航班量'] >= 100]

# 按正常率排序取Top10
top10 = significant_airlines.sort_values('正常率', ascending=False).head(10)

print("图3-3 航司正常率Top10（航班量≥100架次）:")
print(top10)

# 计算样本正常率（所有航司）
sample_normal_rate = airline_stats['正常航班'].sum() / airline_stats['航班量'].sum() * 100
print(f"\n样本总体正常率: {sample_normal_rate:.2f}%")

# 重新核查江西航空(CJX)
if 'CJX' in significant_airlines.index:
    cjx = significant_airlines.loc['CJX']
    print(f"\n江西航空(CJX)数据:")
    print(f"  正常率: {cjx['正常率']}%")
    print(f"  平均延误: {cjx['平均延误']:.1f}分钟")
    print(f"  运力份额: {cjx['航班量'] / len(df) * 100:.1f}%")
else:
    print("\n⚠️ 江西航空(CJX)航班量不足100架次，未进入统计")

# 输出山东航空（如果存在）
if 'CSC' in significant_airlines.index:
    csc = significant_airlines.loc['CSC']
    print(f"\n山东航空(CSC)数据:")
    print(f"  正常率: {csc['正常率']}%")
    print(f"  平均延误: {csc['平均延误']:.1f}分钟")
