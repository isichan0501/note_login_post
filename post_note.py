import re
from playwright.sync_api import Playwright, sync_playwright, expect, Page
from undetected_playwright import Tarnished
from datetime import datetime
from pathlib import Path
import re
import pysnooper
from playwright_stealth import stealth_sync
import json
import time

def save_cookies(context, path="cookies.json"):
    cookies = context.cookies()
    with open(path, "w") as file:
        json.dump(cookies, file)

def load_cookies(context, path="cookies.json"):
    with open(path, "r") as file:
        cookies = json.load(file)
        context.add_cookies(cookies)
        

def read_markdown_file(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print(f"ファイルが見つかりません: {file_path}")
        return None
    except Exception as e:
        print(f"ファイルの読み込み中にエラーが発生しました: {e}")
        return None
    
    


@pysnooper.snoop()
def login(page: Page, email: str, password: str) -> None:
    try:
        page.goto("https://note.com/", wait_until="networkidle")
        page.get_by_role("link", name="ログイン").click()
        page.locator("#email").fill(email)
        page.get_by_label("パスワード").fill(password)
        page.get_by_role("button", name="ログイン").click()
        return True
    except Exception as e:
        print(f"ログイン中にエラーが発生しました: {e}")
        return False



@pysnooper.snoop()
def post_blog(page:Page, image_path: str, title: str, markdown: str, set_paid: bool = False, price: int = 3000) -> None:
    try:
        page.goto("https://note.com/", wait_until="networkidle")
        page.get_by_label("投稿").click()
        page.get_by_role("link", name="テキスト").click()
        page.get_by_label("画像を追加").click()
        with page.expect_file_chooser() as fc_info:
            page.get_by_role("button", name="画像をアップロード").click()
            # page.get_by_label("Upload file").click()
            file_chooser = fc_info.value
            file_chooser.set_files(image_path)
        
        page.get_by_role("button", name="保存").click()
        time.sleep(5)
        page.get_by_placeholder("記事タイトル").fill(title)
        page.get_by_role("textbox").nth(1).fill(markdown)
        time.sleep(5)
        page.get_by_role("button", name="公開に進む").click()
        
        if set_paid:
            page.get_by_text("有料").click()
            page.locator("#price").fill("{}".format(price))
            page.get_by_role("button", name="有料エリア設定").click()
        # page.get_by_role("heading", name="価格").click()
        time.sleep(2)
        # breakpoint()
        # 本文内の特定の文字を検索して、近くの`ラインをこの場所に変更`を押す。
        # free_read_line_sep_words = =======================
        page.locator("button:near(:text(\"=======================\"))").first.click()
        #v age.get_by_text("ラインをこの場所に変更").all()

        page.get_by_role("button", name="投稿する").click()
        return True
    except Exception as e:
        print(f"投稿中にエラーが発生しました: {e}")
        return False




@pysnooper.snoop()
def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False, slow_mo=500)
    context = browser.new_context(locale="ja-JP")
    Tarnished.apply_stealth(context)
    load_cookies(context)
    page = context.new_page()
    # stealth_sync(page)
    page.set_default_timeout(15000)
    
    #-----------login---------
    if not login(page, "ryou8811@gmail.com", "majika19940909"):
        print("ログインに失敗しました")
        return
    
    # ログイン後にcookieを保存
    save_cookies(context)
    
    md_content = read_markdown_file("何でも売る.md")
    

    #-------投稿-----------------
    if not post_blog(page, "sensei-penguin.png", "タイトル", md_content, 
                     set_paid=True, price=3000):
        print("投稿に失敗しました")
        return

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
