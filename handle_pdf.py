import os
import re
from pathlib import Path

from PyPDF2 import PdfReader, PdfWriter
import logging
from PIL import Image
import io
from PyPDF2 import PdfFileReader, PdfFileWriter
import pdf2image
import pdfplumber
from decimal import Decimal, getcontext

getcontext().prec = 6


def extract_number(filename):
    """
    extract number by using re.
    :param filename: file name
    :return: match group number,otherwise 0
    """
    import re
    match = re.search(r'\d+', filename)
    return int(match.group()) if match else 0


def get_pdf_files_in_current_path(current_path=os.getcwd()):
    """
     Get pdf files in current path.
    :param current_path
    :return: sorted files if success,otherwise return False.
    """
    all_items = os.listdir(current_path)
    files = [os.path.join(current_path, f) for f in all_items if
             f.lower().endswith('.pdf') and (not f.endswith('merged.pdf')) and os.path.isfile(os.path.join(current_path, f))]
    if files:
        sorted_files = sorted(files, key=extract_number)
        print(f"all sorted pdf files by number in current path,【{current_path}】:\n {sorted_files}")
        return sorted_files
    else:
        return False

def get_files_in_current_path(current_path=os.getcwd(),suffix = "merged.pdf"):
    """
     Get specified type files in current path.
    :param current_path
    :return: sorted files if success,otherwise return False.
    """
    all_items = os.listdir(current_path)
    files = [os.path.join(current_path, f) for f in all_items if
             f.lower().endswith(suffix)  and os.path.isfile(os.path.join(current_path, f))]
    if files:
        sorted_files = sorted(files, key=extract_number)
        print(f"all sorted pdf files by number in current path,【{current_path}】:\n {sorted_files}")
        return sorted_files
    else:
        return False





def merge_pdfs(paths, output="_merged.pdf"):
    """
    merge multiple pdfs to one.
    :param paths: pdfs path.
    :param output: by default,path+"_merged.pdf"
    :return:
    """
    paths_existed = [p for p in paths if os.path.exists(p)]  # 确保所有文件存在
    pdf_writer = PdfWriter()
    for path in paths_existed:
        pdf_reader = PdfReader(path)
        for index, page in enumerate(pdf_reader.pages):
            # add each page into PdfFileWriter
            print(f"Adding the pdf ：{path}  {index} page： {page}")
            pdf_writer.add_page(pdf_reader.pages[index])

    output_file = os.path.join(output, os.path.basename(output) + "_merged.pdf")
    print(f"Output PDF file：{output_file}")
    with open(output_file, 'wb') as out:
        pdf_writer.write(out)
    return True


def find_folders_with_pdfs(folder_path,suffix = ".pdf"):
    folders_with_pdfs = []
    # Directory tree generator
    for root, dirs, files in os.walk(folder_path):
        if any(file.lower().endswith(suffix) for file in files):
            folders_with_pdfs.append(root)
    return folders_with_pdfs




def merge_all_pdfs():
    """
    Combine functions for merge pdfs in every folder and its subfolders.
    :return: None
    """
    root_folder = os.getcwd()
    folders_containing_pdfs = find_folders_with_pdfs(root_folder)

    # print the folders including *.pdf,and generate the pdf file
    for folder in folders_containing_pdfs:
        print(folder)
        files = get_pdf_files_in_current_path(current_path=folder)
        print(f"want to merge files:{files}")
        if files:
            merge_pdfs(files, output=folder)




def merge_pdf_pages_to_one(pdf1_path, pdf2_path, output_path):
    """
     todo not finished
    :param pdf1_path:
    :param pdf2_path:
    :param output_path:
    :return:
    """
    images1 = pdf2image.convert_from_path(pdf1_path)
    images2 = pdf2image.convert_from_path(pdf2_path)
    # handle the first page.
    image1 = images1[0]
    image2 = images2[0]

    max_width = max(image1.width, image2.width)
    total_height = image1.height + image2.height

    combined_image = Image.new('RGB', (max_width, total_height))

    combined_image.paste(image1, (0, 0))
    combined_image.paste(image2, (0, image1.height+20))

    combined_image.save(output_path, "PDF", resolution=100.0)

def contains_uppercase_currency_numbers(s):
    uppercase_currency_numbers = {'壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖', '拾', '佰', '仟', '万', '亿', '圆','整'}
    for char in s:
        if char in uppercase_currency_numbers:
            return True
    return False

def extract_cny_numerical_values(text):
    # match numbers after ¥
    pattern = r'(?:¥|\s*￥\s*)\s*(\d+\.\d+|\d+)'
    matches = re.findall(pattern,text)
    return matches

def calculate_total_price_tax_from_pdf(file):
    # .一级一级的处理：
    """
    一. 把有发票总金额的行找出来。规则如下：
    1. 包含：价税合计
    2. 包含：大写数字的，比如：贰佰叁拾壹圆柒角
    3. 无上述两种，但包含总计的
    4. 后续待补充
    """
    with pdfplumber.open(file) as pdf:
        price_tax_text = []
        price_tax_value = []
        for index, page in enumerate(pdf.pages):
            page_text = page.extract_text()
            print(f"\npage:{index + 1}")
            print(page_text)
            text_arr = page_text.split('\n')
            for line in text_arr:
                # print(line)
                if ("价税合计" in line) and (( "¥"  in line) | ("￥" in line)):
                    price_tax_text.append(line)
                    print(line)
                    continue
                if contains_uppercase_currency_numbers(line) & (( "¥"  in line)| ("￥" in line)):
                    price_tax_text.append(line)
                    print(line)
                # if ("总计" in line) & (( "¥"  in line)):
                #     price_tax_text.append(line)
                #     print(line)

        print(f"price_tax_text: {price_tax_text}")
        price_tax_text_set = set(price_tax_text)
        print(f"price_tax_text_set: {price_tax_text_set}")

        for item in price_tax_text_set:
            price_tax_value.append(extract_cny_numerical_values(item))
        print(price_tax_value)
        sum = Decimal('0')
        for val in price_tax_value:
            for v in val:
                sum += Decimal(v)
        rounded_result = sum.quantize(Decimal('0.01'))
        print(f"sum = {sum}")
        print(f"rounded_result = {rounded_result}")

        return rounded_result

if __name__ == '__main__':

    # 1. merge pdfs
    # merge_all_pdfs()

    # # 2. 两页PDF合并到1页
    # pdf1_path = '1.pdf'
    # pdf2_path = '2.pdf'
    # # 输出文件路径
    # output_path = 'merged_page.pdf'
    #
    # # 调用函数合并PDF页面内容
    # merge_pdf_pages_to_one(pdf1_path, pdf2_path, output_path)

    folders = find_folders_with_pdfs(os.getcwd())
    for folder in folders:
        print(folder)
        files = get_files_in_current_path(current_path=folder)
        for file in files:
            print(file)
            total = calculate_total_price_tax_from_pdf(file)
            print(f"file:{file} total:{total}")
            file_name = os.path.basename(file)
            result_path = Path(folder).joinpath(f"{file_name}_total_¥{total}.txt")
            with open(f"{file_name}_total_¥{total}.txt",'w') as f:
                f.write(f"{file}\ntotal: ¥{total}")
            with open(result_path,'w') as f:
                f.write(f"{file}\ntotal: ¥{total}")




