# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from pyecharts.charts import Boxplot
from pyecharts import options as opts
from pyecharts.globals import ThemeType
from pyecharts.commons.utils import JsCode
import os
import traceback  # 补充导入，避免报错

# 确保输出目录存在
os.makedirs('output/figures', exist_ok=True)


def load_flight_data():
    """加载并预处理航班数据"""
    df = pd.read_excel('output/khn_flight_processed.xlsx')
    required_fields = ['delayMin', '机型', '航班号']
    if not all(f in df.columns for f in required_fields):
        raise ValueError("数据缺少必需字段")
    return df


def classify_aircraft_type(model):
    """机型分类函数（覆盖所有变体）"""
    if pd.isna(model):
        return '其他'
    model = str(model).upper().strip()
    if any(x in model for x in ['A320', 'A321', 'A319', 'A318']):
        return 'A320系列'
    elif 'B737' in model or 'BOEING 737' in model:
        return 'B737系列'
    elif any(x in model for x in ['E190', 'E195', 'E-190']):
        return 'E190支线'
    elif 'CRJ' in model:
        return 'CRJ支线'
    elif 'ARJ21' in model or ('ARJ' in model and '21' in model):
        return 'ARJ21支线'
    else:
        return '其他'


def chart_3_5_aircraft_boxplot():
    """
    图3-5：主流与支线机型延误箱型对比
    论文3.3.1节文字描述为设计值，实际数据因夏季雷暴右偏
    正文中需增加说明段解释统计差异
    """
    df = load_flight_data()
    df['机型分类'] = df['机型'].apply(classify_aircraft_type)

    # 关键：统计清洗（|delayMin|≤180）后数据，避免极端值压缩箱体
    main_groups = ['A320系列', 'B737系列', 'E190支线', 'CRJ支线', 'ARJ21支线']
    boxplot_data = []
    valid_groups = []
    stats_results = {}

    print("\n图3-5 统计分析摘要:")
    print("=" * 60)

    for group in main_groups:
        # 原始数据
        raw_data = df[df['机型分类'] == group]['delayMin'].dropna().values
        if len(raw_data) == 0:
            continue

        # 清洗后数据（|delayMin|≤180）
        clean_data = raw_data[np.abs(raw_data) <= 180]

        # 计算五数
        stats = [
            float(np.min(clean_data)),
            float(np.percentile(clean_data, 25)),
            float(np.percentile(clean_data, 50)),
            float(np.percentile(clean_data, 75)),
            float(np.max(clean_data))
        ]

        mean_val = float(np.mean(clean_data))
        iqr_val = stats[3] - stats[1]

        stats_results[group] = {
            'count': len(raw_data),
            'clean_count': len(clean_data),
            'mean': mean_val,
            'median': stats[2],
            'iqr': iqr_val,
            'stats': stats
        }

        boxplot_data.append(stats)
        valid_groups.append(group)

        # 输出与论文3.3.1节对比
        print(f"【{group}】")
        print(f"  样本量: {len(raw_data)}架次 (清洗后{len(clean_data)})")
        print(f"  均值: {mean_val:.1f}分钟")
        print(f"  中位数: {stats[2]:.1f}分钟")
        print(f"  IQR: {iqr_val:.1f}分钟")
        print(f"  五数: {stats[0]:.1f}/{stats[1]:.1f}/{stats[2]:.1f}/{stats[3]:.1f}/{stats[4]:.1f}")

        # 标记与论文差异
        if 'A320系列' in group and abs(mean_val - 11.4) > 5:
            print(f"  ⚠ 与论文11.4分钟存在差异，需在正文说明")

    # 创建箱型图
    boxplot = Boxplot(init_opts=opts.InitOpts(
        width='900px',
        height='600px',
        renderer='canvas',
        theme=ThemeType.LIGHT,
        page_title="图3-5 机型箱型对比"
    ))

    boxplot.add_xaxis(valid_groups)
    boxplot.add_yaxis(
        series_name='延误分布',
        y_axis=boxplot_data,
        itemstyle_opts=opts.ItemStyleOpts(
            color=lambda params: '#e67e22' if '支线' in params.name else '#3498db'
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger='item',
            formatter=JsCode("""
                function(params) {
                    var d = params.value;
                    return params.name + '<br/>'
                         + '最小值: ' + d[0].toFixed(1) + '分钟<br/>'
                         + 'Q1: ' + d[1].toFixed(1) + '分钟<br/>'
                         + '中位数: ' + d[2].toFixed(1) + '分钟<br/>'
                         + 'Q3: ' + d[3].toFixed(1) + '分钟<br/>'
                         + '最大值: ' + d[4].toFixed(1) + '分钟';
                }
            """),
            textstyle_opts=opts.TextStyleOpts(font_family='SimHei')
        )
    )

    # 全局配置（仅添加标题居中设置，其他不变）
    boxplot.set_global_opts(
        title_opts=opts.TitleOpts(
            title=' ',  # 图3-5 主流与支线机型延误箱型对比
            subtitle='数据清洗后(|delayMin|≤180分钟) | 异常值影响详见正文',
            title_textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=16, font_weight='bold'),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=12),
            pos_left='center'  # 正副标题居中
        ),
        legend_opts=opts.LegendOpts(pos_top='0%', textstyle_opts=opts.TextStyleOpts(font_family='SimHei')),
        xaxis_opts=opts.AxisOpts(
            name='机型分类',
            name_textstyle_opts=opts.TextStyleOpts(font_family='SimHei'),
            axislabel_opts=opts.LabelOpts(font_family='SimHei', rotate=15)
        ),
        yaxis_opts=opts.AxisOpts(
            name='延误分钟',
            name_textstyle_opts=opts.TextStyleOpts(font_family='SimHei'),
            axislabel_opts=opts.TextStyleOpts(font_family='SimHei')
        ),
        datazoom_opts=[
            opts.DataZoomOpts(type_="inside"),
            opts.DataZoomOpts(type_="slider", pos_bottom='5%')
        ]
    )

    # 渲染
    output_path = 'output/figures/图3-5_机型箱型对比.html'
    boxplot.render(output_path)

    print(f"\n✅ 图3-5 生成成功!")
    print(f"  - 路径: {os.path.abspath(output_path)}")
    print(f"  - 关键: 正文需增加数据说明段解释实际值与论文设计值的差异")
    return boxplot


if __name__ == '__main__':
    print("=" * 60)
    print("正在生成图3-5: 主流与支线机型延误箱型对比...")
    print("=" * 60)

    try:
        chart = chart_3_5_aircraft_boxplot()
        print("\n📊 图表已生成，请手动核验箱体形态与论文描述的逻辑一致性")
    except Exception as e:
        print(f"\n❌ 失败: {e}")
        traceback.print_exc()
