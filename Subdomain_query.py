import requests
from bs4 import BeautifulSoup
import json
import urllib3
import time
import sys
import argparse

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def write_to_file(filename, data):
    with open(filename, 'a', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}\n")

def fetch_data(url, page, headers):
    response = requests.get(f"{url}&page={page}", verify=False, headers=headers)
    if response.status_code == 200:
        json_data = response.json()
        return json_data.get('data', {}).get('result', [])
    else:
        print(f"[!] 我焯，你被拉黑了，等脚本跑完就换个代理吧. 状态码: {response.status_code}")
        return []

def fetch_a_tags(url, headers):
    response = requests.get(url, verify=False, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        a_tags = soup.find_all('a', string=lambda text: text and 'faw.cn' in text)
        return [tag.text for tag in a_tags]
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")
        return []

def check_domains(domains_file):
    with open(domains_file, 'r', encoding='utf-8') as file:
        domains = file.readlines()

    for domain in domains:
        domain = domain.strip()  # 去除首尾空白符，例如换行符
        http_url = f"http://{domain}"
        https_url = f"https://{domain}"

        try:
            # 检查HTTP协议
            check_protocol(http_url)
            # 检查HTTPS协议
            check_protocol(https_url)

        except requests.RequestException as e:
            print(f"{e}\n")

def check_protocol(url):
    response = requests.get(url, timeout=5)
    try:
        title = extract_title(response.content, 'utf-8')
        print(f"Domain: {url} | Status: {response.status_code} | Title: {title}\n")
        pass
    except Exception as e:
        print(f"{e}\n")

def extract_title(html,encoding='utf-8'):
    soup = BeautifulSoup(html, 'html.parser', from_encoding=encoding)
    title_tag = soup.title
    return title_tag.string.strip() if title_tag else "N/A"

def main():

    fingerprint()

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('url', type=str, help='python3 Subdomain_query.py xxx.com')
    parser.add_argument('--check', action='store_true', help='可选项，同时对收集结果进行状态检测，输出标题')
    args = parser.parse_args()

    url = args.url
    check_option = args.check

    print("[*] 正在执行任务，请稍后...等待时间视网络情况而定,一般10秒内就有结果，资产多的话时间会更长")

    proxy = {
        'http': 'http://localhost:8080',
        'https': 'http://localhost:8080'
    }

    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edge/16.16299'
    }

    headers_weixin = {
    'User-Agent': 'Mozilla/5.0 (Linux; Android 7.0; SM-G9300 Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 Mobile Safari/537.36 MicroMessenger/6.6.7.1321(0x26060739) NetType/WIFI Language/zh_CN'
    }

    headers_weixinIOS = {
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 11_0 like Mac OS X) AppleWebKit/604.1.38 (KHTML, like Gecko) Version/11.0 Mobile/15A372 Safari/604.1 MicroMessenger/6.6.7 NetType/WIFI Language/zh_CN'
    }

    headers_firefox = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0'
    }

    headers_safari = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'
    }

    result_filename = f"{url}_output.txt"

    response = requests.get("https://crt.sh/?q=" + url, verify=False, headers=headers)

    if response.status_code == 200:
        soup1 = BeautifulSoup(response.text, 'html.parser')

        matching_cells = soup1.find_all('td', string=lambda text: text and url in text)

        # 遍历结果时排除指定class的<td>标签，因为有一个标签也带有目标字符，但是是垃圾信息，不要也罢，顺便对结果去重
        unique_matching_cells = set()
        for cell in matching_cells:
            if 'outer' not in cell.get('class', []):
                unique_matching_cells.add(cell.text)
        print("[+] 第一轮收集")
        for unique_cell in unique_matching_cells:
            print(unique_cell)
            write_to_file(result_filename, [unique_cell])
        print("\n")
    else:
        print(f"Failed to retrieve data from {url}. Status code: {response.status_code}")

    page = 2
    all_results = []
    while True:
    	#这个接口从第二页开始才有数据，第一页不显示
    	results = fetch_data(f"https://chaziyu.com/ipchaxun.do?domain={url}", page, headers_weixin)
    	if results:
    		all_results.extend(results)
    		page += 1
    		time.sleep(3)  #防止被拉黑，放慢点速度
    	else:
    		break
    print("[+] 第二轮收集")
    for result in all_results:
    	print(result)
    	write_to_file(result_filename, [result])
    print("\n")

    #把上面的第一页结果直接输出到html了，所以导致上面的接口第一页没有数据，这里是第一页缺失的数据
    a_tags = fetch_a_tags(f"https://chaziyu.com/{url}/", headers_weixin)
    print("[+] 第三轮收集")
    for tag in a_tags:
    	print(tag)
    	write_to_file(result_filename, [tag])
    print("\n")
    print(f"收集完成，如有结果会在当前目录下生成{result_filename}文件\n")

    if check_option:
        print("[*] 正在进行状态检测...")
        print("__________________________________________________________________\n")
        check_domains(f"{url}_output.txt")
    print("\n")
    print("[+] 任务结束")

def fingerprint():
	author = '''

   _____       __        __                      _                                     
  / ___/__  __/ /_  ____/ /___  ____ ___  ____ _(_)___     ____ ___  _____  _______  __
  \__ \/ / / / __ \/ __  / __ \/ __ `__ \/ __ `/ / __ \   / __ `/ / / / _ \/ ___/ / / /
 ___/ / /_/ / /_/ / /_/ / /_/ / / / / / / /_/ / / / / /  / /_/ / /_/ /  __/ /  / /_/ / 
/____/\__,_/_.___/\__,_/\____/_/ /_/ /_/\__,_/_/_/ /_/   \__, /\__,_/\___/_/   \__, /  
                                                           /_/                /____/    

根据备案和证书收集子域名资产                                            Fupo's series
______________________________________________________________________________________
	'''
	print(author)

if __name__ == "__main__":
    main()
