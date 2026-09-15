"""
角色設定：你是一位 Python 自動化專家，精通 pandas、openpyxl 以及 Windows 自動化 (win32com.client)。

需求：
1. 產生填寫過的 Excel（.xlsx）收據，每家公司一份。
2. 每家公司 PDF 只匯出「資本簽收據」該工作表，不包含整本 Excel 其他分頁。

流程：
- 先以 openpyxl 依序填入並儲存每家 xlsx
- 再用 win32com 開啟 xlsx，只匯出「資本簽收據」這個工作表成 PDF
- Excel/PDF 檔名皆為收據_公司名稱.xslx / .pdf
- try-finally 確保 Excel 不殘留於背景

"""

import os
import pandas as pd
from openpyxl import load_workbook
os.chdir(r"\\192.168.0.203\Acc\leo\工商用小配件")
# --------- Config: 欄位/儲存格 映射 ---------
CONFIG = {
    "company_column": "公司名稱",      # 資料庫公司名稱欄位
    "id_column": "編號",              # 資料庫收據編號欄位
    "amount_column": "金額",          # 資料庫金額欄位

    "company_cell": "A10",            # 公司名稱 (模板儲存格)
    "id_cell": "F11",                 # 收據編號 (模板儲存格)
    "amount_cell": "E13",             # 金額 (模板儲存格)
    "amount_cell_2": "E29",           # 金額第二聯 (模板儲存格)

    "id_format": "第 {}號",           # 編號格式
    "source_excel": "@工商封面.xlsx",  # 資料庫檔案
    "source_sheet": "工作表1",
    "template_excel": "@@@@工商登記收據.xlsx",
    "template_sheet": "資本簽收據",
    "output_pattern": "5.{}收據.xlsx",
    "output_folder": r"\\192.168.0.203\Acc\leo\工商用小配件",  # 指定輸出資料夾
    "output_pdf_pattern": "5.{}.pdf"
}

def fill_and_save_excels():
    df = pd.read_excel(CONFIG["source_excel"], sheet_name=CONFIG["source_sheet"])
    out_xlsx_files = []
    os.makedirs(CONFIG["output_folder"], exist_ok=True)
    for idx, row in df.iterrows():
        company = str(row[CONFIG["company_column"]]).strip()
        number = row[CONFIG["id_column"]]
        amount = row[CONFIG["amount_column"]]
        output_filename = os.path.join(CONFIG["output_folder"], CONFIG["output_pattern"].format(company))
        receipt_number = CONFIG["id_format"].format(number)

        wb = load_workbook(CONFIG["template_excel"])
        ws = wb[CONFIG["template_sheet"]]
        ws[CONFIG["company_cell"]].value = company
        ws[CONFIG["id_cell"]].value = receipt_number
        ws[CONFIG["amount_cell"]].value = amount
        ws[CONFIG["amount_cell_2"]].value = amount

        output_filename = CONFIG["output_pattern"].format(company)
        wb.save(output_filename)
        wb.close()
        out_xlsx_files.append((output_filename, CONFIG["template_sheet"]))
    
    return out_xlsx_files

def convert_xlsx_sheet_to_pdf(xlsx_sheet_tuples):
    import win32com.client

    excel = None
    try:
        excel = win32com.client.Dispatch("Excel.Application")
        excel.Visible = False
        for xlsx, sheet_name in xlsx_sheet_tuples:
            abs_xlsx = os.path.abspath(xlsx)
            pdf_name = CONFIG["output_pdf_pattern"].format(os.path.splitext(os.path.basename(xlsx))[0][3:])  # 從檔名移除 '收據_'
            abs_pdf = os.path.abspath(pdf_name)
            try:
                wb = excel.Workbooks.Open(abs_xlsx, ReadOnly=1)
                try:
                    ws = wb.Worksheets(sheet_name)
                    ws.Select()
                    ws.ExportAsFixedFormat(0, abs_pdf)
                except Exception as e:
                    print(f"PDF 匯出表單 {sheet_name} 發生錯誤: {e}")
                wb.Close(False)
            except Exception as e:
                print(f"匯出 PDF 時無法開啟 {xlsx}: {e}")
    finally:
        if excel:
            excel.Quit()
            del excel

def main():
    xlsx_sheet_tuples = fill_and_save_excels()
    convert_xlsx_sheet_to_pdf(xlsx_sheet_tuples)
    print("Excel 檔案與 PDF（僅資本簽收據工作表）均已完成")

if __name__ == "__main__":
    main()

#測試修改備註