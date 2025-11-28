# -*- coding: utf-8 -*-
"""
图3-7地理分析数据核查与论文正文生成器
用途：生成论文3.4.1节所需的所有精确数据，无需绘制图表
输出：结构化数据报告 + 可直接引用的论文段落
"""

import pandas as pd
import json
import numpy as np

# ==========================================
# IATA→ICAO转换字典（扩展版）
# ==========================================
IATA_TO_ICAO = {
    'KHN': 'ZSCN', 'PEK': 'ZBAA', 'PKX': 'ZBAD', 'SHA': 'ZSSS', 'PVG': 'ZSPD',
    'CAN': 'ZGGG', 'SZX': 'ZGSZ', 'CTU': 'ZUUU', 'TFU': 'ZUTF', 'HGH': 'ZSHC',
    'WUH': 'ZHHH', 'XIY': 'ZLXY', 'CKG': 'ZUCK', 'TSN': 'ZBTJ', 'HAK': 'ZJHK',
    'SYX': 'ZJSY', 'XMN': 'ZSAM', 'TAO': 'ZSQD', 'DLC': 'ZYTL', 'NKG': 'ZSNJ',
    'KMG': 'ZPPP', 'NNG': 'ZGNN', 'CSX': 'ZGHA', 'HFE': 'ZSOF', 'SHE': 'ZYTX',
    'CGQ': 'ZYCC', 'HRB': 'ZYHB', 'INC': 'ZBYC', 'URC': 'ZWWW', 'KWE': 'ZUGY',
    'LJG': 'ZPLJ', 'LUM': 'ZPLX', 'DLU': 'ZPDL', 'JHG': 'ZPJH', 'KWL': 'ZGKL',
    'BHY': 'ZGBH', 'ENH': 'ZHES', 'RIZ': 'ZSRZ', 'ZHA': 'ZGZJ', 'LYI': 'ZSLY',
    'JNG': 'ZSJG', 'WMT': 'ZSWT', 'XUZ': 'ZSXZ', 'HSN': 'ZSZS', 'DSN': 'ZBDS',
    'DOY': 'ZSDY', 'YCU': 'ZBYC', 'LFQ': 'ZBLF', 'SWA': 'ZGOW', 'ZUH': 'ZGSD',
    'GOQ': 'ZLGM', 'YIN': 'ZWYN', 'HTN': 'ZWAT', 'HET': 'ZBHH', 'TYN': 'ZBYN',
    'CGO': 'ZHCC', 'HIA': 'ZSSH', 'LYG': 'ZSLG', 'LYA': 'ZHLY', 'WNZ': 'ZSWZ',
    'NTG': 'ZSNT', 'YNT': 'ZSYT', 'JJN': 'ZSQZ'
}

# ==========================================
# 机场代码→中文名称映射
# ==========================================
AIRPORT_NAMES = {
    'KHN': '南昌昌北', 'ZSCN': '南昌昌北', 'PEK': '北京首都', 'ZBAA': '北京首都',
    'PKX': '北京大兴', 'ZBAD': '北京大兴', 'SHA': '上海虹桥', 'ZSSS': '上海虹桥',
    'PVG': '上海浦东', 'ZSPD': '上海浦东', 'CAN': '广州白云', 'ZGGG': '广州白云',
    'SZX': '深圳宝安', 'ZGSZ': '深圳宝安', 'CTU': '成都双流', 'ZUUU': '成都双流',
    'TFU': '成都天府', 'ZUTF': '成都天府', 'HGH': '杭州萧山', 'ZSHC': '杭州萧山',
    'WUH': '武汉天河', 'ZHHH': '武汉天河', 'XIY': '西安咸阳', 'ZLXY': '西安咸阳',
    'CKG': '重庆江北', 'ZUCK': '重庆江北', 'TSN': '天津滨海', 'ZBTJ': '天津滨海',
    'HAK': '海口美兰', 'ZJHK': '海口美兰', 'SYX': '三亚凤凰', 'ZJSY': '三亚凤凰',
    'XMN': '厦门高崎', 'ZSAM': '厦门高崎', 'TAO': '青岛胶东', 'ZSQD': '青岛胶东',
    'DLC': '大连周水子', 'ZYTL': '大连周水子', 'NKG': '南京禄口', 'ZSNJ': '南京禄口',
    'KMG': '昆明长水', 'ZPPP': '昆明长水', 'NNG': '南宁吴圩', 'ZGNN': '南宁吴圩',
    'CSX': '长沙黄花', 'ZGHA': '长沙黄花', 'HFE': '合肥新桥', 'ZSOF': '合肥新桥',
    'SHE': '沈阳桃仙', 'ZYTX': '沈阳桃仙', 'CGQ': '长春龙嘉', 'ZYCC': '长春龙嘉',
    'HRB': '哈尔滨太平', 'ZYHB': '哈尔滨太平', 'INC': '银川河东', 'ZBYC': '银川河东',
    'URC': '乌鲁木齐地窝堡', 'ZWWW': '乌鲁木齐地窝堡', 'KWE': '贵阳龙洞堡', 'ZUGY': '贵阳龙洞堡',
    'ZUH': '珠海金湾', 'ZGSD': '珠海金湾'
}

# ==========================================
# 核心配置
# ==========================================
DATA_PATH = 'output/khn_flight_processed.xlsx'
COORDS_PATH = 'output/airport_coords.json'


# ==========================================
# 数据加载函数
# ==========================================
def load_flight_data():
    """加载并清洗航班数据"""
    df = pd.read_excel(DATA_PATH)

    # 字段映射
    field_mapping = {
        '起飞机场三字码': 'originAirport',
        '到达机场三字码': 'destAirport',
        '小时段': 'hour',
        '延误分钟': 'delayMin',
        '航班号': 'flightNo'
    }
    for cn, en in field_mapping.items():
        if cn in df.columns and en not in df.columns:
            df[en] = df[cn]

    # 生成延误标识
    if 'isDelay' not in df.columns:
        df['isDelay'] = df['delayMin'] > 0

    print(f"✓ 数据加载成功: {len(df):,}条航班记录")
    return df


def load_airport_coords():
    """加载并扩展机场坐标库（ICAO+IATA双索引）"""
    with open(COORDS_PATH, 'r', encoding='utf-8') as f:
        coords_original = json.load(f)

    # 双向索引
    coords_all = {}
    for icao_code, coord in coords_original.items():
        coords_all[icao_code] = coord
        # 反向查找IATA
        for iata_code, icao in IATA_TO_ICAO.items():
            if icao == icao_code:
                coords_all[iata_code] = coord

    print(f"✓ 坐标库加载: {len(coords_all)}个机场")
    print(f"  - ICAO代码: {len([c for c in coords_all if len(c) == 4])}个")
    print(f"  - IATA代码: {len([c for c in coords_all if len(c) == 3])}个")
    print(f"  - 南昌机场: {coords_all.get('KHN', coords_all.get('ZSCN'))}")
    return coords_all


def haversine_distance(lat1, lon1, lat2, lon2):
    """计算两点间球面距离（公里）"""
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


# ==========================================
# 核心分析函数
# ==========================================
def analyze_geo_delay(df, airport_coords):
    """
    地理延误分析核心函数
    返回：统计数据DataFrame + 分析摘要字典
    """
    # 1. 筛选昌北出港航班
    df_outbound = df[df['originAirport'] == 'KHN'].copy()
    total_outbound = len(df_outbound)

    if total_outbound == 0:
        raise ValueError("未找到昌北机场出港航班！")

    # 2. 机场代码转换与匹配
    print("\n" + "=" * 60)
    print("🔍 机场坐标匹配核查")
    print("=" * 60)

    unique_dests = df_outbound['destAirport'].unique()
    matched_dests = {}

    for dest in unique_dests:
        if dest in airport_coords:
            matched_dests[dest] = dest
        else:
            icao = IATA_TO_ICAO.get(dest)
            if icao and icao in airport_coords:
                matched_dests[dest] = icao
                print(f"  ✓ 转换成功: {dest}({AIRPORT_NAMES.get(dest, dest)}) → {icao}")

    # 应用转换
    df_outbound['destAirport'] = df_outbound['destAirport'].map(matched_dests)
    df_outbound = df_outbound.dropna(subset=['destAirport'])

    coverage = len(df_outbound['destAirport'].unique()) / len(unique_dests) * 100
    print(f"\n📊 匹配统计:")
    print(f"  - 去重后目的地: {len(unique_dests)}个")
    print(f"  - 匹配成功机场: {len(df_outbound['destAirport'].unique())}个")
    print(f"  - 坐标覆盖率: {coverage:.1f}%")

    if coverage < 30:
        print("  ⚠ 警告: 坐标覆盖率偏低，可能影响空间分析代表性")

    # 3. 核心统计分析
    print("\n" + "=" * 60)
    print("📈 延误空间分布统计")
    print("=" * 60)

    dest_stats = df_outbound.groupby('destAirport').agg(
        avg_delay=('delayMin', 'mean'),
        median_delay=('delayMin', 'median'),
        flight_count=('flightNo', 'count'),
        delay_flight_count=('isDelay', 'sum'),
        total_delay=('delayMin', 'sum'),
        delay_rate=('isDelay', 'mean')
    ).round(2)

    # 计算延误率百分比
    dest_stats['delay_rate_pct'] = (dest_stats['delay_rate'] * 100).round(1)

    # 4. 距离计算
    khn_code = 'KHN' if 'KHN' in airport_coords else 'ZSCN'
    khn_coord = airport_coords[khn_code]

    dest_stats['distance_km'] = dest_stats.index.map(
        lambda dest: haversine_distance(
            khn_coord['lat'], khn_coord['lon'],
            airport_coords[dest]['lat'], airport_coords[dest]['lon']
        )
    ).round(0)

    # 5. 早高峰时段分析 (08:00-10:00)
    print("\n" + "=" * 60)
    print("⏰ 早高峰时段(08:00-10:00)分析")
    print("=" * 60)

    morning_df = df_outbound[(df_outbound['hour'] >= 8) & (df_outbound['hour'] < 10)]

    if len(morning_df) > 0:
        morning_stats = morning_df.groupby('destAirport').agg(
            morning_total=('flightNo', 'count'),
            morning_delay=('isDelay', 'sum')
        )

        dest_stats = dest_stats.join(morning_stats, how='left').fillna(0)

        # 计算早高峰延误占比
        mask = dest_stats['morning_total'] > 0
        dest_stats.loc[mask, 'morning_delay_ratio'] = (
                dest_stats.loc[mask, 'morning_delay'] / dest_stats.loc[mask, 'morning_total'] * 100
        ).round(1)
        dest_stats.loc[~mask, 'morning_delay_ratio'] = np.nan

        print(f"  - 早高峰总航班: {len(morning_df):,}架次")
        print(f"  - 涉及目的地: {morning_df['destAirport'].nunique()}个")
    else:
        dest_stats['morning_total'] = 0
        dest_stats['morning_delay'] = 0
        dest_stats['morning_delay_ratio'] = np.nan
        print("  - 早高峰无航班数据")

    # 6. 距离-延误相关性分析
    print("\n" + "=" * 60)
    print("🔗 距离-延误相关性分析")
    print("=" * 60)

    valid_data = dest_stats.dropna(subset=['distance_km', 'avg_delay'])
    correlation = valid_data['distance_km'].corr(valid_data['avg_delay'])

    print(f"  - 相关系数: {correlation:.3f}")
    if abs(correlation) < 0.3:
        print("  - 结论: 相关性弱，'距离衰减'特征不显著")
        correlation_desc = "弱负相关" if correlation < 0 else "弱正相关"
    elif abs(correlation) < 0.5:
        print("  - 结论: 中等相关性，可描述为'弱距离衰减'")
        correlation_desc = "中等负相关" if correlation < 0 else "中等正相关"
    else:
        print("  - 结论: 强相关性，支持'距离衰减'假说")
        correlation_desc = "强负相关" if correlation < 0 else "强正相关"

    # 7. 分类统计
    delay_levels = {
        '严重延误(>60min)': (dest_stats['avg_delay'] > 60).sum(),
        '高度延误(30-60min)': ((dest_stats['avg_delay'] > 30) & (dest_stats['avg_delay'] <= 60)).sum(),
        '中度延误(20-30min)': ((dest_stats['avg_delay'] > 20) & (dest_stats['avg_delay'] <= 30)).sum(),
        '轻微延误(10-20min)': ((dest_stats['avg_delay'] > 10) & (dest_stats['avg_delay'] <= 20)).sum(),
        '准点(<10min)': (dest_stats['avg_delay'] <= 10).sum()
    }

    print("\n" + "=" * 60)
    print("📊 延误等级分布")
    print("=" * 60)
    for level, count in delay_levels.items():
        pct = count / len(dest_stats) * 100
        print(f"  - {level}: {count}个机场 ({pct:.1f}%)")

    return dest_stats, correlation, correlation_desc, delay_levels


# ==========================================
# 论文正文生成函数
# ==========================================
def generate_paper_content(dest_stats, correlation_desc):
    """
    生成可直接用于论文的文本段落
    包含3.4.1节所有关键数据点
    """
    print("\n" + "=" * 60)
    print("📝 论文正文内容生成")
    print("=" * 60)

    # 1. 总体描述
    total_routes = len(dest_stats)
    avg_delay_all = dest_stats['avg_delay'].mean()
    print("\n【段落1：总体描述】")
    print(f"提取originAirport='KHN'的出港航班，共{total_routes}条航线。平均延误时间为{avg_delay_all:.1f}分钟，")
    print(f"延误率中位数为{dest_stats['delay_rate_pct'].median():.1f}%。")

    # 2. 重点航线数据（按论文要求）
    print("\n【段落2：重点航线数据】")
    key_airports = {
        'ZGHA': 'CSX(长沙黄花)',
        'ZGSZ': 'SZX(深圳宝安)',
        'ZHHH': 'WUH(武汉天河)'
    }

    for icao, name in key_airports.items():
        if icao in dest_stats.index:
            row = dest_stats.loc[icao]
            iata = name.split('(')[0]
            print(f"{name}航线平均延误{row['avg_delay']:.0f}分钟")
            if not np.isnan(row['morning_delay_ratio']) and row['morning_delay_ratio'] > 0:
                print(f"（早高峰延误占比{row['morning_delay_ratio']:.1f}%）")
            else:
                print("（无早高峰数据）")
        else:
            print(f"  ⚠ {name}数据缺失，请调整论文表述")

    # 3. 距离衰减验证
    print(f"\n【段落3：距离衰减特征】")
    correlation = dest_stats['distance_km'].corr(dest_stats['avg_delay'])
    print(f"距离与延误时间呈现{correlation_desc}（r={correlation:.3f}）。")

    # 4. 高延误TOP3（更新论文数据）
    print("\n【段落4：高延误航线TOP3】")
    top3 = dest_stats.nlargest(3, 'avg_delay')
    for i, (icao, row) in enumerate(top3.iterrows(), 1):
        iata_name = [k for k, v in IATA_TO_ICAO.items() if v == icao]
        name_str = f"{iata_name[0]}({icao})" if iata_name else icao
        name_cn = AIRPORT_NAMES.get(icao, icao)
        print(f"{i}. {name_cn}({name_str})")
        print(f"   平均延误: {row['avg_delay']:.1f}分钟，")
        print(f"   距离: {row['distance_km']:.0f}公里，")
        print(f"   航班量: {row['flight_count']:.0f}架次")
        if row['morning_total'] >= 5:
            print(f"   早高峰延误: {row['morning_delay_ratio']:.1f}%")

    # 5. 可视化说明（保留图表引用）
    print("\n【段落5：图表说明】")
    print("图3-7采用ECharts Geo地图可视化，飞线宽度正比于航班量，")
    print("散点大小映射平均延误时间，颜色分级表示延误等级（绿→黄→橙→红）。")
    print("地图支持缩放至长江中游城市群，点击散点可联动查看24小时延误序列。")

    # 6. 数据局限性说明（重要！）
    print("\n【段落6：数据局限性】")
    coverage = len(dest_stats) / len(unique_dests) * 100 if 'unique_dests' in locals() else 100
    if coverage < 100:
        print(f"注：本研究获取了{len(dest_stats)}个机场的精确坐标，")
        print(f"占昌北机场目的地总数的{coverage:.1f}%。")


# ==========================================
# 主函数
# ==========================================
def main():
    print("=" * 70)
    print("🚀 图3-7地理分析数据核查与论文正文生成器")
    print("=" * 70)

    # 加载数据
    df = load_flight_data()
    airport_coords = load_airport_coords()

    # 执行分析
    dest_stats, correlation, correlation_desc, delay_levels = analyze_geo_delay(df, airport_coords)

    # 生成论文内容
    generate_paper_content(dest_stats, correlation_desc)

    # 额外：生成详细数据表格（可直接复制到论文附录）
    print("\n" + "=" * 70)
    print("📋 附录：详细航线统计表")
    print("=" * 70)
    export_df = dest_stats.copy()
    export_df['机场名称'] = export_df.index.map(lambda x: AIRPORT_NAMES.get(x, x))
    export_df = export_df.sort_values('avg_delay', ascending=False)
    export_df['延误等级'] = pd.cut(export_df['avg_delay'],
                                   bins=[-np.inf, 10, 20, 30, np.inf],
                                   labels=['准点', '轻微', '中度', '高度'])

    # 显示前15行
    print("\n前15条高延误航线：")
    display_cols = ['机场名称', 'avg_delay', 'distance_km', 'flight_count', 'delay_rate_pct', 'morning_delay_ratio']
    display_df = export_df[display_cols].head(15)
    display_df.columns = ['机场名称', '平均延误(min)', '距离(km)', '航班量', '延误率(%)', '早高峰延误占比(%)']
    print(display_df.to_string(index=True))

    # 保存完整表格
    output_csv = 'output/figures/航线延误统计表.csv'
    export_df.to_csv(output_csv, encoding='utf-8-sig')
    print(f"\n✓ 完整表格已保存至: {output_csv}")

    # 生成论文修改建议总结
    print("\n" + "=" * 70)
    print("✏️ 论文修改建议总结")
    print("=" * 70)
    print("1. 替换3.4.1节所有具体数值为上方【段落2-4】的精确数据")
    print("2. 在图表说明中补充坐标覆盖率信息（当前：见段落6）")
    print("3. 根据相关系数调整'距离衰减'表述强度（当前：{})".format(correlation_desc))
    print("4. 在论文附录中添加'详细航线统计表'")
    print("5. 检查CSX/SZX/WUH早高峰数据，若缺失需删除相关论述")

    print("\n" + "=" * 70)
    print("🎉 数据核查完成！请直接复制上方内容至论文")
    print("=" * 70)


if __name__ == '__main__':
    main()
#
# ============================================================
# ✓ 数据加载: 8630条记录
# ✓ 坐标库: 45个机场
#
# 📊 数据摘要:
#   - 总航班: 8,630
#   - 昌北出港: 4,334
#   - 坐标库: 45个
#
#
# ✓ 昌北出港: 4,334条
#   - 有效目的地: 21个
#
# ✓ 图3-7 已生成: output/figures/图3-7_地理分布.html
#   - 覆盖目的地: 21个机场
#
# ============================================================
# 📊 论文正文数据修正参考
# ============================================================
#
# 1️⃣ 重点航线延误数据:
# 2️⃣ 延误最高TOP5航线:
#    1. ZUH: 61.8分钟 (169架次)
#    2. CAN: 61.5分钟 (74架次)
#    3. SHE: 56.1分钟 (143架次)
#    4. HAK: 54.7分钟 (212架次)
#    5. HRB: 47.5分钟 (93架次)
#
# 3️⃣ 距离-延误相关系数: 0.333
#    📈 中等相关性，建议描述为'弱距离衰减'
#
# 4️⃣ 区域特征:
#    - 高延误机场(>30分钟): 10个
#    - 平均距离: 1154公里
#    - 建议表述: '高延误航线呈现远距离分散特征'
#
# ============================================================
# ✅ 请根据以上数据精确修正论文3.4.1节的数值表述
# ✅ 图表已完全兼容ECharts，可直接双击HTML查看
# ============================================================
#
# ============================================================
# 🎉 图3-7生成完成！
# ✏️  请根据上方统计数据精确修正论文正文
# ============================================================
#
# Process finished with exit code 0
