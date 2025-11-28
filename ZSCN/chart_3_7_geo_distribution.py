# -*- coding: utf-8 -*-
import pandas as pd
from pyecharts.charts import Geo
from pyecharts import options as opts
from pyecharts.globals import ThemeType, ChartType
import json
import numpy as np
import os

# 确保输出目录存在
os.makedirs('output/figures', exist_ok=True)

# ==========================================
# IATA→ICAO转换字典
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
    'NTG': 'ZSNT', 'YNT': 'ZSYT', 'JNG': 'ZSJG', 'JJN': 'ZSQZ', 'XUZ': 'ZSXZ'
}

# ==========================================
# 机场代码→中文名称映射（核心添加！）
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
    'LJG': '丽江三义', 'ZPLJ': '丽江三义', 'LUM': '德宏芒市', 'ZPLX': '德宏芒市',
    'DLU': '大理凤仪', 'ZPDL': '大理凤仪', 'JHG': '西双版纳嘎洒', 'ZPJH': '西双版纳嘎洒',
    'KWL': '桂林两江', 'ZGKL': '桂林两江', 'BHY': '北海福成', 'ZGBH': '北海福成',
    'ENH': '恩施许家坪', 'ZHES': '恩施许家坪', 'RIZ': '日照山字河', 'ZSRZ': '日照山字河',
    'ZHA': '湛江吴川', 'ZGZJ': '湛江吴川', 'LYI': '临沂启阳', 'ZSLY': '临沂启阳',
    'JNG': '济宁大安', 'ZSJG': '济宁大安', 'WMT': '遵义茅台', 'ZSWT': '遵义茅台',
    'XUZ': '徐州观音', 'ZSXZ': '徐州观音', 'HSN': '舟山普陀山', 'ZSZS': '舟山普陀山',
    'DSN': '鄂尔多斯伊金霍洛', 'ZBDS': '鄂尔多斯伊金霍洛', 'DOY': '东营胜利', 'ZSDY': '东营胜利',
    'YCU': '运城张孝', 'ZBYC': '运城张孝', 'LFQ': '临汾尧都', 'ZBLF': '临汾尧都',
    'SWA': '揭阳潮汕', 'ZGOW': '揭阳潮汕', 'ZUH': '珠海金湾', 'ZGSD': '珠海金湾',
    'GOQ': '格尔木', 'ZLGM': '格尔木', 'YIN': '伊宁', 'ZWYN': '伊宁',
    'HTN': '和田', 'ZWAT': '和田', 'HET': '呼和浩特白塔', 'ZBHH': '呼和浩特白塔',
    'TYN': '太原武宿', 'ZBYN': '太原武宿', 'CGO': '郑州新郑', 'ZHCC': '郑州新郑',
    'HIA': '淮安涟水', 'ZSSH': '淮安涟水', 'LYG': '连云港花果山', 'ZSLG': '连云港花果山',
    'LYA': '洛阳北郊', 'ZHLY': '洛阳北郊', 'WNZ': '温州龙湾', 'ZSWZ': '温州龙湾',
    'NTG': '南通兴东', 'ZSNT': '南通兴东', 'YNT': '烟台蓬莱', 'ZSYT': '烟台蓬莱',
    'JJN': '泉州晋江', 'ZSQZ': '泉州晋江', 'XUZ': '徐州观音', 'ZSXZ': '徐州观音'
}


# ==========================================
# 数据加载
# ==========================================
def load_flight_data():
    df = pd.read_excel('output/khn_flight_processed.xlsx')
    field_mapping = {'起飞机场三字码': 'originAirport', '到达机场三字码': 'destAirport',
                     '小时段': 'hour', '延误分钟': 'delayMin', '航班号': 'flightNo'}
    for cn, en in field_mapping.items():
        if cn in df.columns and en not in df.columns:
            df[en] = df[cn]

    if 'isDelay' not in df.columns:
        df['isDelay'] = df['delayMin'] > 0

    print(f"✓ 数据加载: {len(df)}条记录")
    return df


def load_airport_coords():
    """加载并扩展坐标库"""
    with open('output/airport_coords.json', 'r', encoding='utf-8') as f:
        coords_original = json.load(f)

    coords_all = {}
    for code, coord in coords_original.items():
        coords_all[code] = coord
        for iata, icao in IATA_TO_ICAO.items():
            if icao == code:
                coords_all[iata] = coord

    print(f"✓ 坐标库: {len(coords_all)}个机场")
    return coords_all


# ==========================================
# 距离计算
# ==========================================
def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c


# ==========================================
# 图3-7: 地理分布（中文名称版）
# ==========================================
def plot_geo_distribution_enhanced(df, airport_coords):
    if not airport_coords:
        return None

    # 筛选数据
    df_outbound = df[df['originAirport'] == 'KHN'].copy()
    print(f"\n✓ 昌北出港: {len(df_outbound):,}条")

    # 转换目的地代码
    def convert_dest(dest):
        if dest in airport_coords:
            return dest
        return IATA_TO_ICAO.get(dest, None)

    df_outbound['destAirport'] = df_outbound['destAirport'].apply(convert_dest)
    df_outbound = df_outbound.dropna(subset=['destAirport'])
    df_outbound = df_outbound[df_outbound['destAirport'].isin(airport_coords.keys())]

    # 统计
    dest_stats = df_outbound.groupby('destAirport').agg(
        avg_delay=('delayMin', 'mean'),
        flight_count=('flightNo', 'count'),
        delay_flight_count=('isDelay', 'sum')
    ).round(2)

    # 获取南昌坐标（优先KHN）
    khn_code = 'KHN' if 'KHN' in airport_coords else 'ZSCN'
    khn_coord = airport_coords[khn_code]

    # 距离计算
    dest_stats['distance_km'] = dest_stats.index.map(
        lambda dest: haversine_distance(
            khn_coord['lat'], khn_coord['lon'],
            airport_coords[dest]['lat'], airport_coords[dest]['lon']
        )
    )

    # 早高峰分析
    morning_df = df_outbound[(df_outbound['hour'] >= 8) & (df_outbound['hour'] < 10)]
    if len(morning_df) > 0:
        morning_stats = morning_df.groupby('destAirport').agg(
            morning_total=('flightNo', 'count'),
            morning_delay=('isDelay', 'sum')
        ).fillna(0)

        dest_stats = dest_stats.join(morning_stats, how='left').fillna(0)

        mask = dest_stats['morning_total'] > 0
        dest_stats.loc[mask, 'morning_delay_ratio'] = (dest_stats.loc[mask, 'morning_delay'] /
                                                       dest_stats.loc[mask, 'morning_total'] * 100).round(1)
        dest_stats.loc[~mask, 'morning_delay_ratio'] = 0.0
    else:
        dest_stats['morning_total'] = 0
        dest_stats['morning_delay'] = 0
        dest_stats['morning_delay_ratio'] = 0.0

    print(f"  - 有效目的地: {len(dest_stats)}个")

    # ==========================================
    # 创建Geo图表
    # ==========================================
    geo = Geo(init_opts=opts.InitOpts(width='1400px', height='900px', theme=ThemeType.LIGHT, bg_color="#ffffff"))

    geo.add_schema(
        maptype="china",
        itemstyle_opts=opts.ItemStyleOpts(color="#f7f7f7", border_color="#aaa"),
        emphasis_itemstyle_opts=opts.ItemStyleOpts(color="#e0e0e0"),
        center=[115.9, 28.6],
        zoom=5.5
    )

    # 注册所有坐标
    geo.add_coordinate("昌北机场", khn_coord['lon'], khn_coord['lat'])
    for dest in dest_stats.index:
        geo.add_coordinate(dest, airport_coords[dest]['lon'], airport_coords[dest]['lat'])

    # ==========================================
    # 手动构建series（含中文名称）
    # ==========================================

    # 1. 飞线系列
    lines_data = []
    for dest, row in dest_stats.iterrows():
        # 获取中文名称
        dest_name_cn = AIRPORT_NAMES.get(dest, dest)
        lines_data.append({
            "coords": [
                [khn_coord['lon'], khn_coord['lat']],
                [airport_coords[dest]['lon'], airport_coords[dest]['lat']]
            ],
            "name": f"{dest}",
            "value": row['flight_count'],
            "tooltip": {
                "formatter": f"从昌北机场→{dest_name_cn} ({dest})<br/>航班量: {row['flight_count']:.0f}架次<br/>平均延误: {row['avg_delay']:.1f}分钟<br/>距离: {row['distance_km']:.0f}公里"
            }
        })

    lines_series = {
        "type": "lines",
        "name": "航线",
        "coordinateSystem": "geo",
        "zlevel": 1,
        "effect": {
            "show": True,
            "symbol": "arrow",
            "symbolSize": 6,
            "color": "#3498db",
            "trailLength": 0.1
        },
        "lineStyle": {
            "color": "rgba(149, 165, 166, 0.7)",
            "width": 3,
            "curveness": 0.2,
            "opacity": 0.6
        },
        "data": lines_data,
        "tooltip": {
            "formatter": "从昌北机场→{b}"
        }
    }

    # 2. 目的地散点系列（含中文名称）
    scatter_data = []
    for dest, row in dest_stats.iterrows():
        # 获取中文名称
        dest_name_cn = AIRPORT_NAMES.get(dest, dest)

        if row['avg_delay'] > 30:
            symbol_size, color = 40, "#e74c3c"
        elif row['avg_delay'] > 20:
            symbol_size, color = 30, "#f39c12"
        elif row['avg_delay'] > 10:
            symbol_size, color = 20, "#f1c40f"
        else:
            symbol_size, color = 15, "#2ecc71"

        morning_text = (f"{row['morning_delay_ratio']:.1f}%" if row['morning_total'] > 0
                        else "无早高峰航班")

        tooltip_text = (f"{dest_name_cn} ({dest})<br/>"
                        f"平均延误: {row['avg_delay']:.1f}分钟<br/>"
                        f"航班量: {row['flight_count']:.0f}架次<br/>"
                        f"距离: {row['distance_km']:.0f}公里<br/>"
                        f"早高峰延误占比: {morning_text}")

        scatter_data.append({
            "name": dest,
            "value": [
                airport_coords[dest]['lon'],
                airport_coords[dest]['lat'],
                row['avg_delay']
            ],
            "symbolSize": min(50, symbol_size),
            "itemStyle": {"color": color},
            "tooltip": {"formatter": tooltip_text}
        })

    scatter_series = {
        "type": "scatter",
        "name": "目的站平均延误",
        "coordinateSystem": "geo",
        "zlevel": 2,
        "data": scatter_data
    }

    # 3. 南昌机场系列
    khn_data = [{
        "name": "昌北机场",
        "value": [khn_coord['lon'], khn_coord['lat'], 0],
        "symbolSize": 30,
        "itemStyle": {"color": "#3498db", "borderColor": "#ffffff", "borderWidth": 3},
        "label": {
            "show": True,
            "position": "top",
            "formatter": "昌北机场",
            "fontSize": 14,
            "fontFamily": "SimHei",
            "color": "#000000"
        },
        "tooltip": {"formatter": "昌北机场（KHN）<br/>出发地"}
    }]

    khn_series = {
        "type": "scatter",
        "name": "出发地",
        "coordinateSystem": "geo",
        "zlevel": 3,
        "data": khn_data,
        "visualMap": False
    }

    # ==========================================
    # 合并所有series
    # ==========================================
    geo.options["series"] = [lines_series, scatter_series, khn_series]

    # ==========================================
    # 全局选项
    # ==========================================
    geo.set_global_opts(
        title_opts=opts.TitleOpts(
            title="昌北机场出港延误空间分布",  # 图3-7
            subtitle="散点大小=平均延误 | 颜色=延误等级 | 昌北机场为出发地（蓝色）",
            title_textstyle_opts=opts.TextStyleOpts(font_size=26, font_family='SimHei'),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=17, font_family='SimHei')
        ),
        visualmap_opts=opts.VisualMapOpts(
            min_=0,
            max_=40,
            range_text=['高延误', '低延误'],
            is_piecewise=True,
            series_index=[1],
            pieces=[
                {"min": 30, "label": ">30分钟\n红色预警", "color": "#e74c3c"},
                {"min": 20, "max": 30, "label": "20-30分钟", "color": "#f39c12"},
                {"min": 10, "max": 20, "label": "10-20分钟", "color": "#f1c40f"},
                {"max": 10, "label": "<10分钟", "color": "#2ecc71"}
            ],
            pos_left='left',
            pos_bottom='10%',
            textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=14)
        ),
        legend_opts=opts.LegendOpts(
            is_show=True,
            pos_top='5%',
            pos_right='5%',
            orient='vertical',
            textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=14)
        ),
        toolbox_opts=opts.ToolboxOpts(is_show=True, item_size=22)
    )

    # ==========================================
    # 渲染
    # ==========================================
    output_path = 'output/figures/图3-7_地理分布.html'
    geo.render(output_path)

    print(f"\n✓ 图3-7 已生成: {output_path}")
    print(f"  - 覆盖目的地: {len(scatter_data)}个机场")
    print(f"  - 飞线数量: {len(lines_data)}条")

    # ==========================================
    # 论文数据修正参考（含中文名称）
    # ==========================================
    print("\n" + "=" * 60)
    print("📊 论文正文数据修正参考")
    print("=" * 60)

    key_airports = {
        'ZGHA': 'CSX(长沙黄花)',
        'ZGSZ': 'SZX(深圳宝安)',
        'ZHHH': 'WUH(武汉天河)',
        'ZGGG': 'CAN(广州白云)',
        'ZSAM': 'XMN(厦门高崎)',
        'ZBTJ': 'TSN(天津滨海)',
        'ZSSS': 'SHA(上海虹桥)',
        'ZSPD': 'PVG(上海浦东)',
        'ZBAA': 'PEK(北京首都)',
        'ZBAD': 'PKX(北京大兴)'
    }

    print("\n1️⃣ 重点航线延误数据:")
    for code, name in key_airports.items():
        if code in dest_stats.index:
            row = dest_stats.loc[code]
            print(f"   {name}:")
            print(f"     - 平均延误: {row['avg_delay']:.1f}分钟")
            print(f"     - 航线距离: {row['distance_km']:.0f}公里")
            print(f"     - 航班总量: {row['flight_count']:.0f}架次")
            print(f"     - 早高峰(08-10)延误占比: {row['morning_delay_ratio']:.1f}%")
            print()

    # 高延误TOP3
    top3 = dest_stats.nlargest(3, 'avg_delay')
    print("2️⃣ 延误最高TOP3航线:")
    for i, (dest, row) in enumerate(top3.iterrows(), 1):
        iata_name = [k for k, v in IATA_TO_ICAO.items() if v == dest]
        name = f"{iata_name[0]}({dest})" if iata_name else dest
        name_cn = AIRPORT_NAMES.get(dest, dest)
        print(f"   {i}. {name_cn} {name}: {row['avg_delay']:.1f}分钟 ({row['flight_count']:.0f}架次)")

    # 相关性分析
    correlation = dest_stats['distance_km'].corr(dest_stats['avg_delay'])
    print(f"\n3️⃣ 距离-延误相关系数: {correlation:.3f}")
    if abs(correlation) < 0.3:
        print("   ⚠ 相关性较弱(<0.3)，建议弱化'距离衰减'表述")
    elif correlation > 0.5:
        print("   ✅ 正相关较强(>0.5)，支持'距离衰减'特征")
    else:
        print("   📈 中等相关性，建议描述为'弱距离衰减'")

    print("\n" + "=" * 60)
    print("✅ 请根据以上数据精确修正论文3.4.1节的数值表述")
    print("✅ 图表已显示中文机场名称，鼠标悬浮可查看完整信息")
    print("=" * 60)

    return geo


# ==========================================
# 主函数
# ==========================================
if __name__ == '__main__':
    print("=" * 60)
    print("开始生成图3-7...")
    print("=" * 60)

    df = load_flight_data()
    airport_coords = load_airport_coords()

    print(f"\n📊 数据摘要:")
    print(f"  - 总航班: {len(df):,}")
    print(f"  - 昌北出港: {len(df[df['originAirport'] == 'KHN']):,}")
    print(f"  - 坐标库: {len(airport_coords)}个\n")

    plot_geo_distribution_enhanced(df, airport_coords)

    print("\n" + "=" * 60)
    print("🎉 图3-7生成完成！")
    print("✏️  请根据上方统计数据精确修正论文正文")
    print("=" * 60)