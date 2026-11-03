import json

import requests


def get_data():
    """从 USGS 下载地震数据，返回解析后的 Python 字典。"""
    url = "https://earthquake.usgs.gov/fdsnws/event/1/query"

    # 如果课程模板已提供查询参数，使用模板里的原值。
    params = {
        "format": "geojson",
        "starttime": "1900-01-01",
        "endtime": "1999-12-31T23:59:59.999",
        "minlatitude": 49.5,
        "maxlatitude": 61.0,
        "minlongitude": -9.0,
        "maxlongitude": 2.0,
        "eventtype": "earthquake",
    }

    # params 会被加到 URL 的查询字符串里。
    # timeout 指定连接或读取响应时的等待上限，单位是秒。
    response = requests.get(url, params=params, timeout=30)

    # 如果服务器返回 HTTP 错误，就抛出异常。
    response.raise_for_status()

    # response.text 是网页返回的 JSON 字符串。
    # json.loads() 把字符串解析成 Python 字典。
    return json.loads(response.text)


def get_magnitude(earthquake):
    """从一条地震记录中取出震级。"""
    return earthquake["properties"]["mag"]


def get_location(earthquake):
    """从一条地震记录中取出经度和纬度。"""
    # GeoJSON 的坐标顺序是 [经度, 纬度, 深度]。
    longitude, latitude, depth = earthquake["geometry"]["coordinates"]
    return longitude, latitude


def get_maximum(earthquakes):
    """返回最大震级及对应的坐标，格式为 (震级, (经度, 纬度))。"""
    strongest = None
    max_magnitude = None

    for earthquake in earthquakes:
        magnitude = get_magnitude(earthquake)

        # 震级缺失时，跳过这条记录。
        if magnitude is None:
            continue

        # 第一条有效记录先保存下来。
        # 之后每遇到更大的震级，就更新最大值和对应的整条记录。
        if max_magnitude is None or magnitude > max_magnitude:
            max_magnitude = magnitude
            strongest = earthquake

    if strongest is None:
        raise ValueError("查询结果中没有带有效震级的地震记录。")

    # 从同一条记录取坐标，保证位置和最大震级对应。
    return max_magnitude, get_location(strongest)


if __name__ == "__main__":
    # 直接运行 python earthquakes.py 时，才下载数据并打印结果。
    # 其他脚本 import 这里的函数时，这个块不会运行。
    data = get_data()
    earthquakes = data["features"]

    # README Step 1：查看整份响应的结构和记录数。
    print("Top-level keys:", list(data))
    print("Reported count:", data["metadata"]["count"])
    print("Number of records:", len(earthquakes))

    # 看第一条记录的字段，了解数据长什么样。
    if earthquakes:
        first = earthquakes[0]
        print("Example magnitude:", get_magnitude(first))
        print("Example place:", first["properties"]["place"])
        print("Example coordinates:", first["geometry"]["coordinates"])
        print("Example time (Unix milliseconds):", first["properties"]["time"])

    # README Step 2：找出最大震级并解包坐标。
    magnitude, (longitude, latitude) = get_maximum(earthquakes)
    print(f"The maximum magnitude is {magnitude}.")
    print(f"Coordinates (longitude, latitude): ({longitude}, {latitude})")