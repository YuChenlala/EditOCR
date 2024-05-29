# from paddleocr import PaddleOCR, draw_ocr,PPStructure
# from PIL import Image
# import matplotlib.pyplot as plt
# import matplotlib.patches as patches
# import numpy as np
# from cnstd import LayoutAnalyzer
# from PIL import Image
# from pix2tex.cli import LatexOCR
# from bs4 import BeautifulSoup
# import os
# import cv2
# import multiprocessing
# model = LatexOCR()
# table_engine = PPStructure(table=False, ocr=False,show_log=True)
# table_engine2 = PPStructure(layout=False, show_log=True)
# ocr = PaddleOCR(use_angle_cls=True, lang="ch")
# analyzer = LayoutAnalyzer('mfd')
#
# def extract_td_contents(html_text):
#     # 用于找到<td>之间的元素
#     soup = BeautifulSoup(html_text, 'html.parser')
#     td_tags = soup.find_all('td')
#     td_contents = []
#     for td in td_tags:
#         td_contents.append(td.get_text())
#     return td_contents
# def extract_table_content(html):
#     # 用于提取表格内容
#     soup = BeautifulSoup(html, 'html.parser')
#     body = soup.find('table')
#     return str(body)
#
# def recognize_table(image_path):
#     img = cv2.imread(image_path)
#     result = table_engine2(img)
#     for line in result:
#         line.pop('img')
#      # html内容
#     htmlcode = result[0]['res']['html']
#     # 解码html文本
#     soup = BeautifulSoup(htmlcode, 'html.parser')
#     decoded_html = soup.prettify()
#     body_content = extract_table_content(decoded_html)
#     body_content = body_content.replace('<table>', '<table border=1>');
#     return body_content
#
# def recognize_formula(image_path):
#     img = Image.open(image_path)
#     result = model(img)
#     return result
#
# def recognize_text(image_path):
#     ans = []
#     result= ocr.ocr(image_path, cls=True)
#     image_demo = Image.open(image_path)
#     width, height = image_demo.size
#     for idx in range(len(result)):
#         res = result[idx]
#         for line in res:
#             for point in line[0]:
#                 point[0] /= width
#                 point[1] /= height
#             line[0][2][0] += 0.01
#             line[0][2][1] += 0.01
#             line[0][3][1] += 0.01
#     for index in result[0]:
#         item = {}
#         item['position'] = index[0]
#         item['type'] = 'text'
#         item['score'] = index[1][1]
#         item['text'] = index[1][0]
#         ans.append(item)
#     return ans
# def image_to_text(image_path):
#     result_table = []
#     result_formula = []
#     result_text = []
#     #版面分析部分
#     #表格检测
#     img_path = image_path
#     img = cv2.imread(img_path)
#     table_data = table_engine(img)
#     a = []
#     for line in table_data:
#         line.pop('img')  # 去除img
#         # print(line)
#         a.append(line)
#     table_all = []
#     for i in range(len(a)):
#         if a[i]["type"] == "table":
#             table_all.append(a[i])
#     img = Image.open(img_path).convert('RGB')
#     img_arr = np.array(img)
#     height, width, _ = img_arr.shape
#     tableNum = 0
#     for table in table_all:
#         x = table['bbox']
#         cropped_image = img.crop((table['bbox'][0], table['bbox'][1], table['bbox'][2], table['bbox'][3]))
#         cropped_image.save(f"{image_path}table{tableNum}.jpg")
#         tableNum += 1
#         img_arr[table['bbox'][1]:table['bbox'][3], table['bbox'][0]:table['bbox'][2]] = (255, 255, 255)
#         x = table['bbox'].copy()
#         x[1] = x[1] / height
#         x[3] = x[3] / height
#         x[0] = x[0] / width
#         x[2] = x[2] / width
#         tem0 = [x[0], x[1]]
#         tem1 = [x[2], x[1]]
#         tem2 = [x[0], x[3]]
#         tem3 = [x[2], x[3]]
#         temp = [tem0, tem1, tem2, tem3]
#         c = {}
#         c['position'] = temp
#         c['text'] = ""
#         c['type'] = "table"
#         c['score'] = 1
#         result_table.append(c)
#     img = Image.fromarray(img_arr)
#     img.save(f'{image_path}tableMask.png')
#     # 公式检测
#     img_formula = f'{image_path}tableMask.png'
#     image = Image.open(img_formula)
#     img_arr = np.array(image)
#     out = analyzer.analyze(img_formula, resized_shape=700)
#     formulaNum = 0
#     for formula in out:
#         min_x = int(min(formula['box'][:, 0]))
#         max_x = int(max(formula['box'][:, 0]))
#         min_y = int(min(formula['box'][:, 1]))
#         max_y = int(max(formula['box'][:, 1]))
#         cropped_image = image.crop((min_x, min_y, max_x, max_y))
#         cropped_image.save(f"{image_path}formula{formulaNum}.jpg")
#         formulaNum += 1
#         img_arr[min_y:max_y, min_x:max_x] = (255, 255, 255)
#         c = {}
#         c['position'] = formula['box'].tolist()
#         c['score'] = formula['score']
#         c['type'] = 'formula'
#         c['text'] = ""
#         result_formula.append(c)
#     image = Image.fromarray(img_arr)
#     image.save(f'{image_path}Mask.png')
#     print("--------------------------版面分析完成-----------------------------")
#     #识别部分
#     for i in range(formulaNum):
#         result_formula[i]['text'] = recognize_formula(f"{image_path}formula{i}.jpg")
#     for i in range(tableNum):
#         result_table[i]['text'] = recognize_table(f"{image_path}table{i}.jpg")
#     result_text = recognize_text(f'{image_path}Mask.png')
#     # pool = multiprocessing.Pool()
#     # formula_images = [f"{image_path}formula{i}.jpg" for i in range(formulaNum)]
#     # result_demo_formula = pool.map(recognize_formula, formula_images)
#     # table_images = [f"{image_path}table{i}.jpg" for i in range(tableNum)]
#     # result_demo_table = pool.map(recognize_table, table_images)
#     # result_demo_text = pool.map(recognize_table, [f'{image_path}Mask.png'])
#     # for i in range(formulaNum):
#     #     result_formula[i]['text'] = result_demo_formula[i]
#     # for i in range(tableNum):
#     #     result_table[i]['text'] = result_demo_table[i]
#     # result_text = result_demo_text
#     # pool.close()
#     # pool.join()
#     print("--------------------------识别完成-----------------------------")
#     result = result_table+result_formula+result_text
#     return result

from paddleocr import PaddleOCR, draw_ocr,PPStructure
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from cnstd import LayoutAnalyzer
from PIL import Image
from pix2tex.cli import LatexOCR
from bs4 import BeautifulSoup
import os
import cv2
ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
table_engine = PPStructure(show_log=True)
def extract_td_contents(html_text):
    # 用于找到<td>之间的元素
    soup = BeautifulSoup(html_text, 'html.parser')
    td_tags = soup.find_all('td')
    td_contents = []
    for td in td_tags:
        td_contents.append(td.get_text())
    return td_contents
def extract_table_content(html):
    # 用于提取表格内容
    soup = BeautifulSoup(html, 'html.parser')
    body = soup.find('table')
    return str(body)

def image_to_text(image_path):
    result = []
    # 表格识别
    img_path = image_path
    img = cv2.imread(img_path)
    table_data = table_engine(img)
    a = []
    for line in table_data:
        line.pop('img')  # 去除img
        # print(line)
        a.append(line)
    table_all = []
    for i in range(len(a)):
        if a[i]["type"] == "table":
            table_all.append(a[i])
    print("___________成功获取并解析图片内容并保存______________")
    img = Image.open(img_path).convert('RGB')
    for table in table_all:
        # html内容
        htmlcode = table['res']['html']
        # 解码html文本
        soup = BeautifulSoup(htmlcode, 'html.parser')
        decoded_html = soup.prettify()
        body_content = extract_table_content(decoded_html)
        body_content = body_content.replace('<table>', '<table border=1>');
        x = table['bbox']  # 左上为原点，目标的左上xy,右下xy
        img_arr = np.array(img)
        height, width, _ = img_arr.shape
        # 为以左上为原点的情况下上y:下y，左x:右x,
        img_arr[x[1]:x[3], x[0]:x[2]] = (255, 255, 255)
        img = Image.fromarray(img_arr)
        x[1] = x[1] / height
        x[3] = x[3] / height
        x[0] = x[0] / width
        x[2] = x[2] / width
        # 转化出表格四个点位
        tem0 = [x[0], x[1]]
        tem1 = [x[2], x[1]]
        tem2 = [x[0], x[3]]
        tem3 = [x[2], x[3]]
        temp = [tem0, tem1, tem2, tem3]
        table['bbox'] = temp
        c = {}
        # 修改key值
        c['position'] = temp
        c['text'] = table['res']
        c['text'] = body_content
        c['type'] = "table"
        c['score'] = 1
        result.append(c)
    img.save('./output/processed.png')
    print("_______________表格处理完毕______________")
    # 公式检测

    img_fp = './output/processed.png'
    analyzer = LayoutAnalyzer('mfd')
    out = analyzer.analyze(img_fp, resized_shape=700)
    model = LatexOCR()
    image = plt.imread(img_fp)  # 请替换'your_image.png'为你的图片路径
    image_demo = Image.open(img_fp)
    width, height = image_demo.size
    # 创建一个新的图像
    fig, ax = plt.subplots(figsize=(image.shape[1] / 100, image.shape[0] / 100))  # 设置fig的大小
    # 遍历数据并绘制坐标框，截取子图像并保存
    for i, data in enumerate(out):  # 请用你的数据代替'your_data'
        item = {}
        position = data['box']
        x = position[:, 0]
        y = position[:, 1]
        # 绘制坐标框
        rect = patches.Polygon(xy=position, closed=True, edgecolor='r', facecolor='none')
        ax.add_patch(rect)
        # 截取坐标框对应的子图像
        x_min, y_min = int(x.min()), int(y.min())
        x_max, y_max = int(x.max()), int(y.max())
        sub_image = image[y_min:y_max, x_min:x_max]
        file_name = "lishi.png"
        # 保存子图像
        plt.imsave("lishi.png", sub_image)
        img = Image.open('lishi.png')
        image[y_min:y_max, x_min:x_max] = 1.0
        for point in position:
            point[0] /= width
            point[1] /= height
        position[2][0] += 0.01
        position[2][1] += 0.01
        position[3][1] += 0.01
        item['position'] = position.tolist()
        item['score'] = data['score']
        item['type'] = 'formula'
        item['text'] = model(img)
        result.append(item)
    # 隐藏坐标轴
    ax.axis('off')
    # 显示原始图像
    plt.imshow(image)
    plt.savefig('output_image.png', bbox_inches='tight', pad_inches=0)
    print("_______________公式处理完毕______________")
    result_text = ocr.ocr('output_image.png', cls=True)
    image_demo = Image.open('output_image.png')
    width, height = image_demo.size
    for idx in range(len(result_text)):
        res = result_text[idx]
        for line in res:
            for point in line[0]:
                point[0] /= width
                point[1] /= height
            line[0][2][0] += 0.01
            line[0][2][1] += 0.01
            line[0][3][1] += 0.01
    for index in result_text[0]:
        item = {}
        item['position'] = index[0]
        item['type'] = 'text'
        item['score'] = index[1][1]
        item['text'] = index[1][0]
        result.append(item)
    print("_______________文本处理完毕______________")
    return result