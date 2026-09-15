import logging
import re
from pathlib import Path
import shutil
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s : %(message)s'
)


def get_company_name(filename):
    """
    範例
    得睿會計師事務所_87027385 or 94119945_思恩生命禮儀
    取得公司名稱:得睿會計師師事務所"""
    company_name = re.sub(r"\d{8}", "", filename)
    company_name = company_name.strip("_")

    logging.info(f"取得公司名稱來源test5: {company_name} (类型: {type(company_name)})")

    return company_name


def get_company_id(filename):
    result = re.findall(r"\d{8}", filename)
    logging.debug(f"取得公司統編來源test5: {result}")

    if not result:
        return None
    if result and len(result[0]) != 8:
        logging.warning(f"公司統編長度不正確：{result[0]}")
        return None

    return result[0]


def parse_company(folder_name):
    # 定義一個函式，名字叫 parse_company
    # folder_name 是外面傳進來的資料夾名稱

    # 用 "_" 把資料夾名稱切開
    # 1 代表最多只切一次
    # 例如："00026618_榮美永續"
    # 會變成：["00026618", "榮美永續"]
    parts = folder_name.split("_", 1)

    # 檢查切完之後是不是剛好有 2 個元素
    # 正常應該是：[統編, 公司名稱]
    if len(parts) != 2:

        # 如果不是 2 個元素，代表格式不符合我們的規則
        # 例如："東聚&紫雲綠" 沒有 "_"
        # 這時候回傳 None，表示「這不是標準客戶資料夾」
        return None

    # 取得第 0 個元素，也就是 "_" 左邊的資料
    # 例如："00026618"
    company_id = parts[0]

    # 取得第 1 個元素，也就是 "_" 右邊的資料
    # 例如："榮美永續"
    company_name = parts[1]

    # 檢查統編長度是不是 8 碼
    if len(company_id) != 8:

        # 如果不是 8 碼，就不是我們要的標準格式
        return None

    # isdigit() 用來檢查字串是不是全部都是數字
    # not 代表「不是」
    # 所以這句就是：如果 company_id 不是全部由數字組成
    if not company_id.isdigit():

        # 統編不是純數字，就回傳 None
        return None

    # 前面的檢查全部通過
    # 用 dictionary（字典）整理公司資料
    # "id" 存統編
    # "name" 存公司名稱
    return {
        "id": company_id,
        "name": company_name
    }


def find_folder_name(folder_path):
    """
    找出指定路徑「第一層」的所有資料夾。

    傳入：
    folder_path → 要搜尋的資料夾路徑

    做什麼：
    使用 iterdir() 查看第一層內容
    只保留資料夾，不要檔案

    回傳：
    folders → 資料夾 Path 組成的 list
    """
    logging.debug(f"資料夾路徑：{folder_path}")


    logging.debug(f"路徑是否存在：{folder_path.exists()}")
    logging.debug(f"是否為資料夾：{folder_path.is_dir()}")
    # folders = [f for f in folder_path.rglob("*") if f.is_dir()]
    folders = [f for f in folder_path.iterdir() if f.is_dir()]
    logging.debug(f"資料類型：{type(folders)}")
    logging.debug(f"資料夾數量：{len(folders)}")
    return folders

def is_company_folder(folder):
    """
    判斷這個資料夾是不是「公司資料夾」。

    傳入：
    folder → 要檢查的資料夾 Path

    做什麼：
    用 get_company_id() 從資料夾名稱找統編

    回傳：
    True  → 找到統編，是公司資料夾
    False → 找不到統編，視為群組資料夾
    """


    # 從資料夾名稱找統編
    company_id = get_company_id(folder.name)

    # 找得到統編，代表這是一個公司資料夾
    if company_id:
        return True

    # 找不到統編，暫時視為群組資料夾
    return False

def find_companies_in_group(folder):
    """
    找出「群組資料夾」下一層的所有公司資料夾。

    傳入：
    folder → 群組資料夾的 Path

    做什麼：
    查看群組資料夾的下一層
    用 is_company_folder() 判斷是不是公司

    回傳：
    companies → 找到的公司 Path 組成的 list
    """
    # 準備空清單，用來存找到的公司
    companies = []

    # 查看這個資料夾的下一層
    for child in folder.iterdir():

        # 如果不是資料夾就跳過
        if not child.is_dir():
            continue

        # 判斷是不是公司資料夾
        if is_company_folder(child):

            # 是公司的話就加入清單
            companies.append(child)

    # 把找到的公司全部傳回去
    return companies

def find_companies(folder_path):
    """
        folder_path
            ↓
        find_folder_name() → 找第一層資料夾
            ↓
        is_company_folder() → 判斷是不是公司
            ↓
        是 → 加入 companies
        不是 → 進群組裡繼續找
            ↓
        return companies
"""

    # 準備一個空清單
    # 最後所有找到的公司都會放進這裡
    companies = []

    # 找出根目錄底下第一層的所有資料夾
    folders = find_folder_name(folder_path)

    # 一個一個檢查第一層資料夾
    for folder in folders:

        # 判斷目前這個資料夾本身是不是公司資料夾
        if is_company_folder(folder):

            # 如果是單一公司
            # 就把這個公司的 Path 加入 companies
            companies.append(folder)

        # 如果第一層不是公司
        # 就有可能是群組資料夾
        else:

            # 進入群組資料夾
            # 找出裡面所有公司
            group_companies = find_companies_in_group(folder)

            # 將群組裡找到的所有公司
            # 一次加入 companies
            companies.extend(group_companies)

    # 回傳所有找到的公司
    return companies

if __name__ == "__main__":
    # companys = ["得睿會計師事務所_87027385", "其他公司_12345678", "沃肯&心苑", "長統編公司_123456789"]
    # for company in companys:
    #     company_name = get_company_name(company)
    #     company_id = get_company_id(company)
    pass
    # 準備一個正常的客戶資料夾名稱
# 準備要搜尋的根目錄
folder_path = Path(r"E:\測試")

# 找出所有公司
companies = find_companies(folder_path)


# 一家公司一家公司的處理
for company in companies:
    pass