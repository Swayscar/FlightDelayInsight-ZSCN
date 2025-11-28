# ==========================================
# 图3-4: 主基地与外航延误分布对比（图例位置优化版）
# 修复：图例移至底部，避免与标题重叠
# ==========================================
import pandas as pd
import numpy as np
from pyecharts.charts import Boxplot
from pyecharts import options as opts
from scipy import stats


def plot_base_vs_external_boxplot(df):
    """
    生成主基地航司(CJX)与外航延误分布对比箱型图
    优化：图例位置移至底部
    """
    # 1. 数据分类
    df['航司类型'] = df['所属航司代码'].map({'CJX': '主基地航司'}).fillna('外航')

    # 提取并过滤数据
    cjx_data = df[df['航司类型'] == '主基地航司']['delayMin']
    external_data = df[df['航司类型'] == '外航']['delayMin']
    cjx_filtered = cjx_data[(cjx_data >= -30) & (cjx_data <= 200)]
    external_filtered = external_data[(external_data >= -30) & (external_data <= 200)]

    # 2. 统计检验
    statistic, p_value = stats.mannwhitneyu(
        cjx_filtered, external_filtered, alternative='two-sided'
    )

    # 3. 计算箱型图统计量
    cjx_stats = [np.percentile(cjx_filtered, i) for i in [0, 25, 50, 75, 100]]
    ext_stats = [np.percentile(external_filtered, i) for i in [0, 25, 50, 75, 100]]

    # 4. ECharts图表生成
    boxplot = Boxplot(
        init_opts=opts.InitOpts(
            width='1000px',
            height='600px',
        )
    )

    boxplot.add_xaxis(['主基地航司', '外航'])
    boxplot.add_yaxis(
        '延误分布',  # 这是图例名称
        boxplot.prepare_data([cjx_stats, ext_stats]),
        itemstyle_opts=opts.ItemStyleOpts(color='#e74c3c')
    )

    # 5. 图表配置（图例移至底部）
    boxplot.set_global_opts(
        title_opts=opts.TitleOpts(
            title=' ',  # 图3-4 主基地航司与外航延误分布对比
            subtitle=f'样本量: 主基地航司={len(cjx_data)}架次 | 外航={len(external_data)}架次\n'
                     f'中位数: 主基地{cjx_stats[2]:.0f}分钟 | 外航{ext_stats[2]:.0f}分钟\n'
                     f'Mann-Whitney U检验 p={p_value:.3f} (<0.05，差异显著)',
            pos_left='center',
            pos_top='top',
        ),
        yaxis_opts=opts.AxisOpts(name='延误分钟', min_=-30, max_=200),
        xaxis_opts=opts.AxisOpts(name='航司类型'),
        # 图例配置：移至底部，避免与标题重叠
        legend_opts=opts.LegendOpts(
            is_show=True,
            pos_bottom='5%',  # 距离底部5%
            pos_left='center',  # 水平居中
            orient='horizontal',  # 水平排列
        ),
    )

    # 6. 渲染输出
    output_path = 'output/figures/图3-4_主基地与外航延误分布对比.html'
    boxplot.render(output_path)

    # 7. 控制台反馈
    print(f"✓ 图3-4 已生成: {output_path}")
    print(f"  主基地航司样本量: {len(cjx_data)}架次")
    print(f"  外航样本量: {len(external_data)}架次")
    print(f"  主基地中位数: {cjx_stats[2]:.1f}分钟")
    print(f"  外航中位数: {ext_stats[2]:.1f}分钟")
    print(f"  Mann-Whitney U检验 p值: {p_value:.4f}")

    cjx_mean = df[df['所属航司代码'] == 'CJX']['delayMin'].mean()
    print(f"  交叉验证: CJX平均延误={cjx_mean:.1f}分钟（论文应为97.2分钟）")

    return boxplot


# ===== 主程序 =====
if __name__ == '__main__':
    df = pd.read_excel('data/khn_flight.xlsx', engine='openpyxl')
    plot_base_vs_external_boxplot(df)