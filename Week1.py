import urllib.request as req
import bs4
import re
import numpy as np
import csv
import time, random
#找到最大頁數
url_page1="https://24h.pchome.com.tw/store/DSAA31"
request=req.Request(url_page1,headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Referer":"https://24h.pchome.com.tw/"
}) 
with req.urlopen(request) as response:
    data=response.read().decode("utf-8")
    page=bs4.BeautifulSoup(data,"html.parser")
    all_page=page.find_all("li",class_="c-pagination__item")
    page_list=[]
    for p in all_page:
        page_tag=p.find("a",class_="c-pagination__link").text
        page_list.append(int(page_tag))
    max_page=max(page_list)
#找到每頁的prod_id並寫入products.txt檔案中
best_product=[]
for each_page in range(1,max_page+1):
    url=f"https://24h.pchome.com.tw/store/DSAA31?p={each_page}"
    with req.urlopen(url) as response:
        data=response.read().decode("utf-8")
        root=bs4.BeautifulSoup(data,"html.parser")
        prod=root.find_all("li",class_="c-listInfoGrid__item c-listInfoGrid__item--gridCardGray5")
        for prod_list in prod:
            prod_id=prod_list.find_all("a",class_="c-prodInfoV2__link gtmClickV2")
            for a_tag in prod_id:
                a_tag_id=a_tag.get('href')
                if a_tag_id:
                    tag=a_tag_id.split("/prod/")[-1]
                    best_product.append(tag)
with open("products.txt","w",encoding="utf-8") as file:
    file.write("\n".join(best_product))
print("products.txt finish.")
product_price_map={}
all_i5_price=[]
best_product_write=[]

for best_product_id in best_product:
    time.sleep(random.uniform(1, 3))
    url_product=f"https://24h.pchome.com.tw/prod/{best_product_id}"
    request=req.Request(url_product,headers={
    "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
    "Referer":"https://24h.pchome.com.tw/"
    }) 
    with req.urlopen(request) as response:
        data=response.read().decode("utf-8")
        root=bs4.BeautifulSoup(data,"html.parser")
        grade_tag=root.find('div',class_="c-ratingIcon__textNumber c-ratingIcon__textNumber--m700GrayDarkest")
        grade = float(grade_tag.text) if grade_tag else 0.0
        #取得評論數
        comment_tag = root.find('div', class_="c-ratingIcon__text c-ratingIcon__text--s400Gray")
        comment = comment_tag.text if comment_tag else ""
        comment_number = int(re.search(r'\d+', comment).group()) if re.search(r'\d+', comment) else 0
        i5process_tag = root.find_all('div', class_="c-tableGrid__htmlText")
        i5process_text = " ".join(tag.get_text(strip=True) for tag in i5process_tag)
        #取得所有價格
        price=root.find('div',class_="o-prodPrice__price").text
        if price:
            all_price=int(re.sub(r'\D+','',price))
        else:
            all_price=0
        #將id及相對price存入dic
        product_price_map[best_product_id]=all_price
        #將評論大於等於1則及分數大於等於4.9寫入檔案
        if int(comment_number)>=1 and grade>=4.9:
            best_product_write.append(best_product_id)
            
        if re.search(r'Intel.*Core.*i5', i5process_text, re.IGNORECASE):
            all_i5_price.append(all_price)
with open("best-product.txt","w",encoding='utf-8') as file:
    file.write("\n".join(best_product_write))
if all_i5_price:
    average_i5_processor_price = np.mean(all_i5_price)
    print(f"The average price of ASUS PCs with Intel i5 processor: {average_i5_processor_price}")
else:
    print("No Intel i5 products found.")


print("best-product.txt finish.")
#計算z_score
prices=list(product_price_map.values())
mean=np.mean(prices)
std_prices=np.std(prices)
with open("standarization.csv","w",newline="",encoding="utf-8") as file:
    csv_file=csv.writer(file)
    for prd,price in product_price_map.items():
        z_score=(price-mean)/std_prices
        csv_file.writerow([prd,price,z_score])
print("standarization.csv finish.")
