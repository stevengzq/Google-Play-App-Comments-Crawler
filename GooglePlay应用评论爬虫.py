from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import re
import time
import pandas as pd

import warnings
warnings.filterwarnings("ignore")

# 利用webdriver打开网页
# url = 'https://play.google.com/store/apps/details?id=com.miHoYo.GenshinImpact&hl=en&gl=US&showAllReviews=true'
url = 'https://play.google.com/store/apps/details?id=com.nianticlabs.pokemongo&showAllReviews=true&hl=en&gl=US'
path = '/Users/gaosteven/Downloads/chromedriver'

driver = webdriver.Chrome(path)
driver.get(url)

user_review = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "td1D0d")))

results = []

tol_comments_num = 0
dis_comments_num = 0

# 爬取首页内容（前40条）
cur_comments = driver.find_elements(By.CLASS_NAME, 'UD7Dzf')
cur_stars = driver.find_elements(By.CLASS_NAME, 'nt2C1d')
cur_likes = driver.find_elements(By.CLASS_NAME, 'jUL89d')
cur_names_dates = driver.find_elements(By.CLASS_NAME, 'kx8XBd')

# 将爬取内容写进results列表中
for i in range(0, len(cur_comments)):
    star = re.findall('(?<=Rated )\d{1}', cur_stars[i].get_attribute('innerHTML'))[0]
    comment = cur_comments[i].get_attribute('textContent')
    if 'Full Review' in comment:
        comment = re.findall('(?<=Full Review).*', cur_comments[i].get_attribute('textContent'))[0]
    like = cur_likes[i].text
    name = cur_names_dates[i].text.split('\n')[0]
    date = cur_names_dates[i].text.split('\n')[1]
    results.append([name, date, star, comment, like])

    tol_comments_num += 1

# 设置页面加载次数
page_num = 100
for page in range(2, page_num+1):

    # 加载页面
    try:
        show_more = driver.find_element(By.CLASS_NAME, 'RveJvd')
        show_more.click()
        time.sleep(3)
    except:
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(3)

    # 判断是否因为加载页面导致中间评论丢失(当前页面评论数+历史丢失评论数<记录的总评论数)
    if len(driver.find_elements(By.CLASS_NAME, 'UD7Dzf')) + dis_comments_num < tol_comments_num + 40:

        # 本次丢失的评论数量
        cur_dis_num = tol_comments_num + 40 - (len(driver.find_elements(By.CLASS_NAME, 'UD7Dzf')) + dis_comments_num)

        # 更新历史丢失评论总数
        dis_comments_num += cur_dis_num

        # 爬取新加载的页面内容
        cur_comments = driver.find_elements(By.CLASS_NAME, 'UD7Dzf')[40:]
        cur_stars = driver.find_elements(By.CLASS_NAME, 'nt2C1d')[40:]
        cur_likes = driver.find_elements(By.CLASS_NAME, 'jUL89d')[40:]
        cur_names_dates = driver.find_elements(By.CLASS_NAME, 'kx8XBd')[40:]

        # 将新加载的内容写进results列表中
        for i in range(0, len(cur_comments)):
            star = re.findall('(?<=Rated )\d{1}', cur_stars[i].get_attribute('innerHTML'))[0]
            comment = cur_comments[i].get_attribute('textContent')
            if 'Full Review' in comment:
                comment = re.findall('(?<=Full Review).*', cur_comments[i].get_attribute('textContent'))[0]
            like = cur_likes[i].text
            name = cur_names_dates[i].text.split('\n')[0]
            date = cur_names_dates[i].text.split('\n')[1]
            content = [name, date, star, comment, like]
            if content not in results:
                results.append(content)
                tol_comments_num += 1

    else:

        # 爬取新加载页面的内容
        cur_comments = driver.find_elements(By.CLASS_NAME, 'UD7Dzf')[tol_comments_num - dis_comments_num:]
        cur_stars = driver.find_elements(By.CLASS_NAME, 'nt2C1d')[tol_comments_num - dis_comments_num:]
        cur_likes = driver.find_elements(By.CLASS_NAME, 'jUL89d')[tol_comments_num - dis_comments_num:]
        cur_names_dates = driver.find_elements(By.CLASS_NAME, 'kx8XBd')[tol_comments_num - dis_comments_num:]

        # 将新加载的内容写进results列表中
        for i in range(0, len(cur_comments)):
            star = re.findall('(?<=Rated )\d{1}', cur_stars[i].get_attribute('innerHTML'))[0]
            comment = cur_comments[i].get_attribute('textContent')
            if 'Full Review' in comment:
                comment = re.findall('(?<=Full Review).*', cur_comments[i].get_attribute('textContent'))[0]
            like = cur_likes[i].text
            name = cur_names_dates[i].text.split('\n')[0]
            date = cur_names_dates[i].text.split('\n')[1]
            content = [name, date, star, comment, like]
            if content not in results:
                results.append(content)
                tol_comments_num += 1


df = pd.DataFrame(results)
df.columns = ['Name','Date','Stars','Comments','Likes']
df.index = df.index+1
df['Likes'][df['Likes']=='']=0
df[['Stars','Likes']] = df[['Stars','Likes']].astype('int')
