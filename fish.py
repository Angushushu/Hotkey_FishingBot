# -*- coding: UTF-8 -*-
import pyautogui
import pydirectinput as pd
import time
from cnocr import CnOcr
import cv2
import numpy as np

pyautogui.PAUSE = 1
last_death = None
last_pull = None
ocr = CnOcr()

def findfish(res):
    for line in res:
        if(line == ['浮', '漂', ':', '溅', '起', '水', '花']):
            return True
    return False

def reborn():
    global last_death
    fig_dead = pyautogui.screenshot(region=(659,493,601,52))
    img_dead = np.asarray(fig_dead)
    textImg_dead = detect(img_dead)
    res = ocr.ocr(textImg_dead)
    print("Dead or not:", res)
    for line in res:
        print('reborn:', line)
        if(line == ['重','生']):
            # 防止传送冷却
            new_death = time.time()
            if last_death and new_death-last_death < 120:
                time.sleep(120)
            last_death = new_death
            pyautogui.moveTo(960, 540)
            pd.click()
            time.sleep(6)
            pd.typewrite('/home')
            pd.press('enter')
            time.sleep(6)
            pyautogui.click(button='right') # 抛竿

def reconnect():
    fig_disconnect = pyautogui.screenshot(region=(660,569,601,57))
    img_disconnect = np.asarray(fig_disconnect)
    textImg_disconnect = detect(img_disconnect)
    res = ocr.ocr(textImg_disconnect)
    for line in res:
        print('reconnect:', line)
        if(line == ['回','到','服','务','器','列','表']):
            pyautogui.moveTo(960, 599)
            pd.click()
            time.sleep(2)
            pyautogui.moveTo(962, 293)
            pd.click()
            pd.click()
            time.sleep(5)
            login()

def login():
    text = '以登录'
    arr = list(text)
    # fig_login = pyautogui.screenshot(region=(0,880,880,35))
    fig_login = pyautogui.screenshot(region=(0,850,600,150))
    img_login = np.asarray(fig_login)
    textImg_login = detect(img_login)
    res = ocr.ocr(textImg_login)
    for line in res:
        print('login:', line)
        match = True
        for i in arr:
            if not i in line:
                match = False
                break
        if match:
            print('重新登陆')
            pd.typewrite('/login ')
            pd.press('capslock')
            pd.press('a')
            pd.press('capslock')
            pd.typewrite('ngus52529850')
            pd.press('enter')
            time.sleep(2)
            pd.typewrite('/home')
            pd.press('enter')
            time.sleep(6)
            pyautogui.click(button='right') # 抛竿

def fish():
    global last_pull
    last_pull = time.time()
    
    cnt = 0
    
    while(1):
        # 如被打断，重新抛竿
        if last_pull and (time.time()-last_pull > 60):
            pd.typewrite('/home')
            pd.press('enter')
            time.sleep(6)
            pyautogui.click(button='right')
            last_pull = time.time()
            print('重新抛竿')

        # 1、截图，手动定位字幕大致区域
        # fig = pyautogui.screenshot(region=(1775, 700, 130, 300))
        fig = pyautogui.screenshot(region=(1720, 700, 170, 300))
        
        # 2、检测文本所在区域
        img = np.asarray(fig)
        textImg = detect(img)

        # 3、利用cnocr识别文本
        res = ocr.ocr(textImg)
        
        print("Predicted Chars:", res)
        
        # 4、通过文本判断是否收杆
        if(findfish(res)):
            pyautogui.click(button='right') #收杆
            # 检查服务器状态，login，上钩
            # if(cnt >= 100):
            #     login()
            #     reborn()
            #     reconnect()
            #     cnt = 0
            pyautogui.click(button='right') #抛竿
            last_pull = time.time()
            time.sleep(1)
        else:
            # time.sleep(1)
            if(cnt >= 100):
                reborn()
                reconnect()
                login()
                cnt = 0
            time.sleep(0.5)
        cnt += 1
        if cnt%10 == 0:
            print('cnt: ', cnt) 

def detect(img):
    # 1.  转化成灰度图
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
    # 2. 形态学变换的预处理，得到可以查找矩形的图片
    dilation = preprocess(gray)
    # 3. 查找和筛选文字区域
    x, y, w, h = findTextRegion(dilation)
    return img[y:y + h, x:x + w]

def preprocess(gray):
    # 1. Sobel算子，x方向求梯度
    sobel = cv2.Sobel(gray, cv2.CV_8U, 1, 0, ksize=3)
    # 2. 二值化
    _, binary = cv2.threshold(sobel, 0, 255, cv2.THRESH_OTSU + cv2.THRESH_BINARY)
    # 3. 膨胀和腐蚀操作的核函数
    element1 = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 9))
    element2 = cv2.getStructuringElement(cv2.MORPH_RECT, (24, 6))
    # 4. 膨胀一次，让轮廓突出
    dilation = cv2.dilate(binary, element2, iterations=1)
    # 5. 腐蚀一次，去掉细节，如表格线等。注意这里去掉的是竖直的线
    erosion = cv2.erode(dilation, element1, iterations=1)
    # 6. 再次膨胀，让轮廓明显一些
    dilation2 = cv2.dilate(erosion, element2, iterations=2)
    return dilation2

def findTextRegion(img):
    # 查找轮廓
    contours, _ = cv2.findContours(img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    maxArea = 0
    maxContour = 0
    if(len(contours)==0):
        return 0,0,0,0
    for i in range(len(contours)):
        cnt = contours[i]
        # 计算该轮廓的面积
        area = cv2.contourArea(cnt)
        if area > maxArea:
            maxArea = area
            maxContour = cnt
    x, y, w, h = cv2.boundingRect(maxContour)
    return x, y, w, h

if __name__ =='__main__':
    fish()