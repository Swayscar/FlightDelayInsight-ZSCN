# verification_3_1_1.py
import pandas as pd

# 加载数据
df = pd.read_excel('output/khn_flight_processed.xlsx')

# 计算每小时的平均延误和航班量
hourly_stats = df.groupby('小时段').agg(
    avg_delay=('delayMin', 'mean'),
    flight_count=('航班号', 'count')
).reset_index()

# 找出延误和航班量的峰值
hourly_stats['avg_delay'] = hourly_stats['avg_delay'].round(1)  # 保留1位小数
hourly_stats['flight_count'] = hourly_stats['flight_count'].astype(int)  # 转换为整数

max_delay_hour = hourly_stats.loc[hourly_stats['avg_delay'].idxmax(), ['小时段', 'avg_delay']]
max_flight_hour = hourly_stats.loc[hourly_stats['flight_count'].idxmax(), ['小时段', 'flight_count']]

# 找出第二高峰值
sorted_delay = hourly_stats.sort_values(by='avg_delay', ascending=False)
sorted_flight = hourly_stats.sort_values(by='flight_count', ascending=False)

second_peak_delay_hour = sorted_delay.iloc[1][['小时段', 'avg_delay']]
second_peak_flight_hour = sorted_flight.iloc[1][['小时段', 'flight_count']]

print(f"平均延误最高峰: {max_delay_hour['小时段']}时，均值 {max_delay_hour['avg_delay']}分钟")
print(f"航班量最高峰: {max_flight_hour['小时段']}时，航班量 {max_flight_hour['flight_count']}")
print(f"延误次高峰: {second_peak_delay_hour['小时段']}时，均值 {second_peak_delay_hour['avg_delay']}分钟")
print(f"航班量次高峰: {second_peak_flight_hour['小时段']}时，航班量 {second_peak_flight_hour['flight_count']}")