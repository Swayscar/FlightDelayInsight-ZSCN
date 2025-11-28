# -*- coding: utf-8 -*-
import pandas as pd
from pyecharts.charts import Bar
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode  # 确保颜色和交互生效
from pyecharts.globals import ThemeType
import os

os.makedirs('output/figures', exist_ok=True)


def load_flight_data():
    df = pd.read_excel('output/khn_flight_processed.xlsx')
    required_fields = ['delayMin', '延误等级', '所属航司代码', '航班号']
    missing = [f for f in required_fields if f not in df.columns]
    if missing:
        raise ValueError(f"缺少必需字段: {missing}")
    return df


def calculate_airline_stats(df):
    """计算航司正常率统计（航班量≥100架次）"""
    airline_stats = df.groupby('所属航司代码').agg(
        航班量=('航班号', 'count'),
        正常航班=('延误等级', lambda x: x.isin(['准点', '轻微', '中度']).sum()),
        平均延误=('delayMin', 'mean')
    )

    airline_stats['正常率'] = (airline_stats['正常航班'] / airline_stats['航班量'] * 100).round(2)
    significant_airlines = airline_stats[airline_stats['航班量'] >= 100]
    # 按正常率升序排列，保证柱状图从左到右递增
    top10 = significant_airlines.sort_values('正常率', ascending=True).tail(10)
    sample_normal_rate = airline_stats['正常航班'].sum() / airline_stats['航班量'].sum() * 100

    return top10, round(sample_normal_rate, 2)


def chart_3_3_airline_normal_rate():
    """
    图3-3：航司正常率Top10（修复标注位置和颜色高亮问题）
    """
    df = load_flight_data()
    top10, sample_normal_rate = calculate_airline_stats(df)

    # 保留所有控制台输出内容
    print("\n图3-3 航司正常率Top10核查结果:")
    print(top10)
    print(f"\n样本总体正常率: {sample_normal_rate}%")

    # 检查CJX并保留排名计算
    airlines = top10.index.tolist()
    cjx_in_top10 = 'CJX' in airlines
    cjx_rank = None
    cjx_data = None
    cjx_index = airlines.index('CJX') if cjx_in_top10 else -1  # 新增索引变量，用于颜色定位
    if cjx_in_top10:
        cjx_rank = len(top10) - list(top10.index).index('CJX')
        cjx_data = top10.loc['CJX']
        print(f"  - 江西航空(CJX)正常率: {cjx_data['正常率']}%（第{cjx_rank}位）")

    # 创建图表
    bar = Bar(init_opts=opts.InitOpts(
        width='900px',
        height='650px',
        renderer='canvas',
        theme=ThemeType.LIGHT,
        page_title="图3-3 航司正常率Top10"
    ))

    # X轴（航司代码）
    bar.add_xaxis(airlines)

    # 正常率数据
    normal_rates = top10['正常率'].tolist()

    # 核心修复：颜色和交互适配最新版，保留原有样式
    bar.add_yaxis(
        series_name='正常率(%)',
        y_axis=normal_rates,
        label_opts=opts.LabelOpts(
            formatter="{c}%",
            font_size=11,
            font_family='SimHei',
            color='#333333',
            position='top',
            offset=[0, -10]  # 保留偏移设置
        ),
        # 修复颜色：用JsCode强制定位CJX（最新版必用）
        itemstyle_opts=opts.ItemStyleOpts(
            color=JsCode(f"""
                function(params) {{
                    return params.dataIndex === {cjx_index} ? '#e74c3c' : '#3498db';
                }}
            """)
        ),
        # 修复tooltip：适配最新版params结构
        tooltip_opts=opts.TooltipOpts(
            trigger='axis',
            axis_pointer_type='cross',
            textstyle_opts=opts.TextStyleOpts(font_family='SimHei'),
            formatter=lambda p: f"{p[0].name}<br/>正常率: {p[0].value}%<br/>航班量: {int(top10.loc[p[0].name, '航班量'])}条<br/>平均延误: {top10.loc[p[0].name, '平均延误']:.1f}分钟"
        ),
        # 修复MarkLine：参数符合最新版规范
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(y=sample_normal_rate, name=f"样本正常率 {sample_normal_rate}%")],
            linestyle_opts=opts.LineStyleOpts(color='#95a5a6', type_='dashed', width=2),
            label_opts=opts.LabelOpts(color='#7f8c8d', font_family='SimHei', font_size=11, position='end')
        )
    )

    # 全局配置保留原有样式
    bar.set_global_opts(
        title_opts=opts.TitleOpts(
            title='   航司正常率Top10（航班量≥100架次）',  # 图3-3
            subtitle=f'判定标准: 延误≤60分钟 | 样本正常率: {sample_normal_rate}% | 江西航空(CJX)红色高亮',
            title_textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=16, font_weight='bold'),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_family='SimHei', font_size=11),
            pos_left='center'
        ),
        tooltip_opts=opts.TooltipOpts(trigger='axis', axis_pointer_type='cross',
                                      textstyle_opts=opts.TextStyleOpts(font_family='SimHei')),
        legend_opts=opts.LegendOpts(is_show=False),
        xaxis_opts=opts.AxisOpts(name='航司代码', name_textstyle_opts=opts.TextStyleOpts(font_family='SimHei'),
                                 axislabel_opts=opts.LabelOpts(font_family='SimHei', font_size=11)),
        yaxis_opts=opts.AxisOpts(name='正常率(%)', min_=50, max_=100, interval=5,
                                 name_textstyle_opts=opts.TextStyleOpts(font_family='SimHei'),
                                 axislabel_opts=opts.LabelOpts(font_family='SimHei', font_size=11))
    )

    # 渲染保存
    output_path = 'output/figures/图3-3_航司正常率Top10.html'
    bar.render(output_path)

    # 保留所有输出结果
    print(f"\n✅ 图3-3 生成成功!")
    print(f"  - 文件: {os.path.abspath(output_path)}")
    print(f"  - Top1: {top10.index[-1]} {top10.iloc[-1]['正常率']}%")
    if cjx_rank:
        print(f"  - 江西航空(CJX)排名: 第{cjx_rank}位")
        print(f"  - CJX正常率: {cjx_data['正常率']}%")
    print(f"  - 样本正常率参考线: {sample_normal_rate}%")

    return bar


if __name__ == '__main__':
    print("=" * 60)
    print("正在生成图3-3: 航司正常率Top10（修复版）...")
    print("=" * 60)

    try:
        chart = chart_3_3_airline_normal_rate()
        print("\n📊 图表已生成，请用浏览器打开HTML文件查看效果")
    except Exception as e:
        print(f"\n✗ 生成失败: {e}")
        import traceback

        traceback.print_exc()