# -*- coding: utf-8 -*-
import pandas as pd
from pyecharts.charts import Line
from pyecharts import options as opts
from pyecharts.globals import ThemeType
import os

# 确保输出目录存在
os.makedirs('output/figures', exist_ok=True)


def load_flight_data_for_trend():
    """加载航班数据"""
    try:
        df = pd.read_excel('output/khn_flight_processed.xlsx')
        print(f"✓ 加载数据成功: {len(df)}条记录")
    except Exception as e:
        print(f"⚠ 读取处理后数据失败: {e}，尝试读取原始数据...")
        df = pd.read_excel('data/khn_flight.xlsx')

    if 'delayMin' not in df.columns or '小时段' not in df.columns:
        raise ValueError("数据缺少'delayMin'或'小时段'列！")

    return df


def plot_24h_trend_standalone():
    df = load_flight_data_for_trend()

    # 按小时统计（数据层面保证精度）
    hourly = df.groupby('小时段')['delayMin'].agg([
        lambda x: round(x.mean(), 1),  # 直接保留1位小数
        'median',
        lambda x: int(x.count())
    ]).reset_index()
    hourly.columns = ['小时段', 'mean', 'median', 'count']
    peak_hour = hourly.loc[hourly['mean'].idxmax()]

    # 创建图表
    line = Line(init_opts=opts.InitOpts(
        width='1000px', height='600px',
        renderer='canvas',
        theme=ThemeType.LIGHT
    ))

    # X轴
    line.add_xaxis(hourly['小时段'].astype(str).tolist())

    # 平均延误线（恢复动态计算）
    line.add_yaxis(
        series_name='平均延误(分钟)',
        y_axis=hourly['mean'].tolist(),
        is_smooth=True,
        symbol='circle',
        symbol_size=8,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(width=3, color='#e74c3c'),
        markpoint_opts=opts.MarkPointOpts(
            data=[opts.MarkPointItem(
                name=f"峰值{peak_hour['小时段']}时",
                coord=[str(peak_hour['小时段']), peak_hour['mean']],
                value=f"{peak_hour['mean']}分钟"
            )]
        ),
        # 关键：恢复type_="average"实现动态更新，用{c}显示（数据已处理为1位小数）
        markline_opts=opts.MarkLineOpts(
            data=[opts.MarkLineItem(type_="average", name="全天平均延误")],
            label_opts=opts.LabelOpts(
                font_size=12, color='#333333', font_family='SimHei',
                offset=[-80, 0], formatter='{c}\n（平均延误）'  # {c}会动态显示选中区间的均值
            )
        )
    )

    # 右Y轴：航班量（整数）
    line.extend_axis(
        yaxis=opts.AxisOpts(
            name='航班量(架次)',
            position='right',
            axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color='#3498db')),
            axislabel_opts=opts.LabelOpts(color='#3498db', font_family='SimHei')
        )
    )

    line.add_yaxis(
        series_name='航班量(架次)',
        y_axis=hourly['count'].tolist(),
        yaxis_index=1,
        is_smooth=True,
        symbol='diamond',
        symbol_size=6,
        label_opts=opts.LabelOpts(is_show=False),
        linestyle_opts=opts.LineStyleOpts(width=2, type_='dashed', color='#3498db')
    )

    # 全局配置
    line.set_global_opts(
        title_opts=opts.TitleOpts(
            title='',  # 图3-1 昌北机场24小时平均延误趋势
            subtitle=f'数据来源: 8630条航班 | 异常值191条 | 中位数11分钟',
            title_textstyle_opts=opts.TextStyleOpts(font_size=18, font_family='SimHei'),
            subtitle_textstyle_opts=opts.TextStyleOpts(font_size=11, font_family='SimHei'),
            pos_left='center'
        ),
        tooltip_opts=opts.TooltipOpts(
            trigger='axis',
            axis_pointer_type='cross',
            formatter='{b}时<br/>{a0}: {c0}分钟<br/>{a1}: {c1}架次'
        ),
        legend_opts=opts.LegendOpts(
            pos_top='8%', pos_left='center',
            textstyle_opts=opts.TextStyleOpts(font_size=12, font_family='SimHei')
        ),
        xaxis_opts=opts.AxisOpts(
            name='小时段(UTC+8)',
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, font_family='SimHei'),
            axislabel_opts=opts.LabelOpts(font_size=11, font_family='SimHei')
        ),
        yaxis_opts=opts.AxisOpts(
            name='延误均值(分钟)',
            min_=0, max_=250, interval=50,
            name_textstyle_opts=opts.TextStyleOpts(font_size=12, font_family='SimHei'),
            axislabel_opts=opts.LabelOpts(font_size=11, font_family='SimHei')
        ),
        datazoom_opts=[opts.DataZoomOpts(range_start=0, range_end=100)]  # 拖动生效
    )

    # 保存图表
    output_path = 'output/figures/图3-1_24小时延误趋势.html'
    line.render(output_path)

    print(f"\n✅ 图3-1生成完成！")
    print(f"  - 文件路径: {os.path.abspath(output_path)}")
    return line


if __name__ == '__main__':
    print("=" * 60)
    print("开始生成图3-1: 24小时平均延误趋势")
    print("=" * 60)

    chart = plot_24h_trend_standalone()
    print("\n📊 图表已生成，可直接用浏览器打开HTML文件查看！")
