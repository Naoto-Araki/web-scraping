from time import sleep
from bs4 import BeautifulSoup
import requests
import pandas as pd
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 福岡市城南区のSUUMOサイト
#url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40136&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&page={}'

# 福岡市西区のSUUMOサイト
# url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40135&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&page={}'

# 福岡市早良区のSUUMOサイト
# url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40137&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&page={}'

# 福岡市博多区のSUUMOサイト
# url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40132&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&page={}'

# 福岡市東区のSUUMOサイト
# url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40131&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1&page={}'

# 福岡市南区のSUUMOサイト
# url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40134&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&srch_navi=1&page={}'

# 福岡市中央区のSUUMOサイト
url = 'https://suumo.jp/jj/chintai/ichiran/FR301FC001/?ar=090&bs=040&ta=40&sc=40133&cb=0.0&ct=9999999&et=9999999&cn=9999999&mb=0&mt=9999999&shkr1=03&shkr2=03&shkr3=03&shkr4=03&fw2=&page={}'


# リトライ戦略を設定したセッションの作成
session = requests.Session()
retries = Retry(total=5, backoff_factor=0.3, status_forcelist=[429, 500, 502, 503, 504])
session.mount('https://', HTTPAdapter(max_retries=retries))

d_list = []

# 最初のページにアクセスしてページ数を取得
target_url = url.format(1)
try:
    r = session.get(target_url, timeout=10)
    soup = BeautifulSoup(r.text, 'html.parser')
    # ページ数の取得
    pages = soup.find('div', class_='pagination pagination_set-nav')
    page_tags = pages.find('ol', class_='pagination-parts')
    page_tag = page_tags.find_all('li')[-1]
    page_numbers = int(page_tag.text) + 1  # 整数に変換し、1ページ追加
except Exception as e:
    print(f"ページ数の取得エラー: {e}")
    page_numbers = 1

print(f"総ページ数: {page_numbers}")

for i in range(1, page_numbers):
    print(f'処理中のページ: {i}')
    target_url = url.format(i)
    try:
        r = session.get(target_url, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, 'html.parser')
    except requests.RequestException as e:
        print(f"ページ {i} の取得エラー: {e}")
        continue

    # 物件情報の抽出
    contents = soup.find_all('div', class_='cassetteitem')
    for content in contents:
        detail = content.find('div', class_='cassetteitem-detail')
        table = content.find('table', class_='cassetteitem_other')

        # 主要な詳細情報を抽出
        title = detail.find('div', class_='cassetteitem_content-title').text
        address = detail.find('li', class_='cassetteitem_detail-col1').text
        access = detail.find('li', class_='cassetteitem_detail-col2').text
        age = detail.find('li', class_='cassetteitem_detail-col3').text

        tr_tags = table.find_all('tr', class_='js-cassette_link')
        for tr_tag in tr_tags:
            floor, price, first_fee, capacity = tr_tag.find_all('td')[2:6]
            fee, management_fee = price.find_all('li')
            deposit, gratuity = first_fee.find_all('li')
            madori, menseki = capacity.find_all('li')

            link = tr_tag.find_all('td')[8]
            a = link.find('a')
            href = a.get('href')
            detail_link = 'https://suumo.jp' + href

            # 詳細リンクへのアクセス
            try:
                r_child = session.get(detail_link, timeout=10)
                r_child.raise_for_status()
                soup_child = BeautifulSoup(r_child.text, 'html.parser')

                contents_child = soup_child.find_all('div', class_='section l-space_small')
                if len(contents_child) > 1: # 0の方がいいかも (時間があれば再実行)
                    content_child = contents_child[1]
                    table_child = content_child.find('table', class_='data_table table_gaiyou')
                    structure, floors, year = table_child.find_all('td')[1:4]
                    numbers = table_child.find_all('td')[14]

                    # データリストに追加
                    d = {
                        'title': title,
                        'address': address,
                        'access': access,
                        'age': age,
                        'floor': floor.text,
                        'fee': fee.text,
                        'management_fee': management_fee.text,
                        'deposit': deposit.text,
                        'gratuity': gratuity.text,
                        'madori': madori.text,
                        'menseki': menseki.text,
                        'structure': structure.text,
                        'floors': floors.text,
                        'year': year.text,
                        'numbers': numbers.text
                    }
                    d_list.append(d)
                else:
                    print(f"リンクをスキップ: {detail_link}、コンテンツが不足しています")
            except requests.RequestException as e:
                print(f"詳細ページ {detail_link} の取得エラー: {e}")
            sleep(1)

df = pd.DataFrame(d_list)
# df.to_csv('chintai_zyounan.csv', index=None, encoding='utf-8-sig')
# df.to_csv('chintai_nishi.csv', index=None, encoding='utf-8-sig')
# df.to_csv('chintai_sawara.csv', index=None, encoding='utf-8-sig')
# df.to_csv('chintai_hakata.csv', index=None, encoding='utf-8-sig')
# df.to_csv('chintai_higashi.csv', index=None, encoding='utf-8-sig')
#df.to_csv('chintai_minami.csv', index=None, encoding='utf-8-sig')
df.to_csv('chintai_chuo.csv', index=None, encoding='utf-8-sig')