import pandas as pd
import json


def get_airport_coordinates():
    """
    从OpenFlights获取机场经纬度坐标
    数据格式: AirportID,Name,City,Country,IATA,ICAO,Latitude,Longitude,...
    """
    url = "https://raw.githubusercontent.com/jpatokal/openflights/master/data/airports.dat"

    # 正确读取CSV格式(逗号分隔)
    airports = pd.read_csv(url, sep=',', header=None,
                           names=['AirportID', 'Name', 'City', 'Country', 'IATA', 'ICAO',
                                  'Latitude', 'Longitude', 'Altitude', 'Timezone', 'DST',
                                  'Tz', 'Type', 'Source'],
                           na_values=['\\N'])  # 处理空值标记

    # 筛选出有效的ICAO代码和坐标
    airports = airports.dropna(subset=['ICAO', 'Latitude', 'Longitude'])

    # 确保ICAO唯一
    airports = airports.drop_duplicates(subset=['ICAO'])

    # 转换为字典格式
    coords = {}
    for _, row in airports.iterrows():
        if pd.notna(row['ICAO']) and pd.notna(row['Latitude']) and pd.notna(row['Longitude']):
            coords[row['ICAO']] = {
                'lat': float(row['Latitude']),
                'lon': float(row['Longitude'])
            }

    return coords


def save_airport_coords_to_json(coords):
    """保存坐标到JSON文件"""
    # 确保output目录存在
    import os
    os.makedirs('output', exist_ok=True)

    with open('output/airport_coords.json', 'w', encoding='utf-8') as f:
        json.dump(coords, f, indent=4, ensure_ascii=False)


if __name__ == '__main__':
    try:
        print("正在从OpenFlights获取机场坐标数据...")
        airport_coords = get_airport_coordinates()
        save_airport_coords_to_json(airport_coords)
        print(f"✓ 成功获取 {len(airport_coords)} 个机场的坐标")
        print("✓ 文件已保存到: output/airport_coords.json")

        # 显示前5个作为示例
        print("\n前5个机场示例:")
        for icao, coord in list(airport_coords.items())[:5]:
            print(f"  {icao}: {coord}")

    except Exception as e:
        print(f"✗ 获取失败: {e}")
        print("建议: 检查网络连接或手动创建JSON文件")
