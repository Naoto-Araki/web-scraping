from time import sleep
from bs4 import BeautifulSoup
import requests
import pandas as pd

# requestsでurlにアクセスしてHTML解析
# 博多区の中古マンションSUUMOサイト
url = 'https://suumo.jp/jj/bukken/ichiran/JJ010FJ001/?ar=090&bs=011&ta=40&jspIdFlg=patternShikugun&sc=40131&sc=40132&sc=40133&sc=40134&sc=40135&sc=40136&sc=40137&kb=1&kt=9999999&mb=0&mt=9999999&ekTjCd=&ekTjNm=&tj=0&cnb=0&cn=9999999&srch_navi=1&page={}'

d_list = []

target_url = url.format(1)
r = requests.get(target_url)
soup = BeautifulSoup(r.text)

# ページ数を取得
pages = soup.find('div', class_='pagination pagination_set-nav')
page_tags = pages.find('ol', class_='pagination-parts')
# ページ数一覧の 'li' タグの数で変更する
page_tag = page_tags.find_all('li')[10]
page_numbers = page_tag.text  # ページ番号を文字列で取得
page_numbers = int(page_numbers)  # 整数に変換
page_numbers = page_numbers + 1  # ページ番号を1増加

print(f"総ページ数: {page_numbers}")

for i in range(1, page_numbers):
    print(f'処理中のページ: {i}')
    target_url = url.format(i)
    #print(taget_url)

    r = requests.get(target_url)
    soup = BeautifulSoup(r.text, 'html.parser')

    # サーバーに負荷をかけないため
    sleep(1)

    # soupから情報を取得
    contents = soup.find_all('div', class_='property_unit-content')

    for content in contents:
        # 詳細リンクを取得
        link = content.find('h2', class_='property_unit-title')
        a = link.find('a')
        href = a.get('href')
        detail_link = 'https://suumo.jp' + href + 'bukkengaiyo/?fmlg=t001'

        # print(detail_link)
        
        # 詳細リンクへのアクセス
        try:
            r_child = requests.get(detail_link)
            r_child.raise_for_status()
            soup_child = BeautifulSoup(r_child.text, 'html.parser')
            # soup_childから情報を取得
            contents_child = soup_child.find_all('div', class_='secTitleOuterR') or soup_child.find_all('div', class_='secTitleOuterK')
            
            if len(contents_child) > 1:
                content_child = contents_child[0]
                title = content_child.find('h3', class_='secTitleInnerR') or content_child.find('h3', class_='secTitleInnerK')
                tables_child = soup_child.find_all('table', class_='mt10 bdGrayT bdGrayL bgWhite pCell10 bdclps wf')
                table_child = tables_child[0]
                years = table_child.find_all('td')[13]
                table_child = tables_child[1]
                address, access, numbers, structure_floors = table_child.find_all('td')[0:4]

                # 取得した情報を辞書に格納
                d ={
                    'title':title.text,
                    'address':address.text,
                    'access':access.text,
                    'years':years.text,
                    'numbers':numbers.text,
                    'structure/floors':structure_floors.text
                }
                d_list.append(d)
            else:
                print(f"リンクをスキップ: {detail_link}、コンテンツが不足しています")
        except requests.RequestException as e:
            print(f"詳細ページ {detail_link} の取得エラー: {e}")
        
        # サーバーに負荷をかけないために
        sleep(1)

df = pd.DataFrame(d_list)

df.to_csv('used_apartment_hakata.csv', index=None, encoding='utf-8-sig')