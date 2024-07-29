import os
from PyPDF2 import PdfReader, PdfWriter
import logging

def get_pdf_files_in_current_path():
    '''
    get pdf file in current path.
    :return: file path.
    '''
    current_path = os.getcwd()
    all_items = os.listdir(current_path)
    files = [f for f in all_items if f.endswith('.pdf') and os.path.isfile(os.path.join(current_path,f))]
    print(f"all pdf files in current path: {files}")
    files.sort()
    return files

def merge_pdfs(paths, output="merged.pdf"):
    '''
    多个pdf文件合并为1个pdf文件
    :param paths: pdf文件名列表。
    :param output: 输出文件名
    :return: 无
    '''
    paths = [p for p in paths if os.path.exists(p)]    # 确保所有文件存在
    pdf_writer = PdfWriter()
    for path in paths:
        pdf_reader = PdfReader(path)
        for index,page in enumerate(pdf_reader.pages):
            # 将每一页添加到PdfFileWriter对象中
            pdf_writer.add_page(pdf_reader.pages[index])

    # 写入到输出PDF文件
    with open(output, 'wb') as out:
        pdf_writer.write(out)


from PIL import Image
import io
from PyPDF2 import PdfFileReader, PdfFileWriter
import pdf2image


def merge_pdf_pages_to_one(pdf1_path, pdf2_path, output_path):
    # 将PDF页面转换为图像
    images1 = pdf2image.convert_from_path(pdf1_path)
    images2 = pdf2image.convert_from_path(pdf2_path)

    # 假设我们只合并第一页
    image1 = images1[0]
    image2 = images2[0]

    # 计算合并后图像的尺寸
    total_width = image1.width + image2.width
    max_height = max(image1.height, image2.height)

    # 创建一个新的空白图像，大小为两个图像的总宽度和最大高度
    combined_image = Image.new('RGB', (total_width, max_height))

    # 将两个图像粘贴到空白图像上
    combined_image.paste(image1, (0, 0))
    combined_image.paste(image2, (image1.width, 0))

    # 将合并后的图像保存为PDF
    combined_image.save(output_path, "PDF", resolution=100.0)


if __name__ == '__main__':

    # 1. 要合并的PDF文件路径列表,多个pdf文件合并为一个pdf文件
    # paths = ['1.pdf', '2.pdf', '3.pdf','4.pdf']
    # 多个pdf文件合并为1个
    merge_pdfs(get_pdf_files_in_current_path())


    # # 2. 两页PDF合并到1页
    # pdf1_path = '1.pdf'
    # pdf2_path = '3.pdf'
    # # 输出文件路径
    # output_path = 'merged_page.pdf'
    #
    # # 调用函数合并PDF页面内容
    # merge_pdf_pages_to_one(pdf1_path, pdf2_path, output_path)