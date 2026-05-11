import os
import sys
import time
import json

if getattr(sys, 'frozen', False):
    script_dir = os.path.dirname(os.path.abspath(sys.executable))
else:
    script_dir = os.path.dirname(os.path.abspath(__file__))


def try_selenium_login():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.options import Options as ChromeOptions
    except ImportError as e:
        print(f"缺少依赖库: {e}")
        print("请运行: pip install selenium")
        input("\n按回车键退出...")
        return None

    driver = None
    try:
        print("=" * 60)
        print("B站Cookie自动获取工具")
        print("=" * 60)

        print("\n正在启动Chrome浏览器...")
        options = ChromeOptions()
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-popup-blocking')

        driver = webdriver.Chrome(options=options)
        wait = WebDriverWait(driver, 30)

        print("正在访问B站登录页面...")
        driver.get('https://passport.bilibili.com/login')

        print("等待二维码加载...")
        time.sleep(3)

        qrcode_selector = '.qrcode-img img, .qrcode img, canvas, .login-qrcode img, .qcowimg, .scan-qrcode-img'

        try:
            wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, qrcode_selector))
            )
        except:
            print("未找到二维码元素，请检查Chrome浏览器是否正常")
            input("\n按回车键关闭浏览器...")
            driver.quit()
            return None

        print("\n请用手机B站客户端扫码登录...")
        print("-" * 40)

        start_time = time.time()
        timeout = 180

        while True:
            if time.time() - start_time > timeout:
                print("\n登录超时，请重新运行程序")
                input("\n按回车键关闭浏览器...")
                driver.quit()
                return None

            cookies = driver.get_cookies()

            sessdata = next((c['value'] for c in cookies if c['name'] == 'SESSDATA'), None)
            bili_jct = next((c['value'] for c in cookies if c['name'] == 'bili_jct'), None)
            dedeuserid = next((c['value'] for c in cookies if c['name'] == 'DedeUserID'), None)

            if sessdata and bili_jct and dedeuserid:
                cookie_dict = {
                    'SESSDATA': sessdata,
                    'bili_jct': bili_jct,
                    'DedeUserID': dedeuserid
                }

                print("\n" + "=" * 60)
                print("登录成功!")
                print("=" * 60)
                print(f"\n获取到的Cookie内容:")
                print(f"-" * 40)
                print(f"SESSDATA: {sessdata[:20]}...{sessdata[-10:]}")
                print(f"bili_jct: {bili_jct[:20]}...{bili_jct[-10:]}")
                print(f"DedeUserID: {dedeuserid}")
                print(f"-" * 40)

                save_cookies(cookie_dict)

                input("\n按回车键关闭浏览器并退出程序...")
                driver.quit()
                return cookie_dict

            time.sleep(1)

    except Exception as e:
        print(f"\n发生错误: {e}")
        import traceback
        traceback.print_exc()

        if driver:
            try:
                driver.quit()
            except:
                pass

        input("\n按回车键退出...")
        return None


def save_cookies(cookies):
    txt_file = os.path.join(script_dir, 'bilibili_cookies.txt')
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("B站Cookie信息\n")
        f.write("=" * 40 + "\n")
        f.write(f"获取时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("\nCookie内容:\n")
        f.write(f"SESSDATA={cookies['SESSDATA']}\n")
        f.write(f"bili_jct={cookies['bili_jct']}\n")
        f.write(f"DedeUserID={cookies['DedeUserID']}\n")
        f.write("\n完整Cookie字符串:\n")
        f.write(f"SESSDATA={cookies['SESSDATA']}; bili_jct={cookies['bili_jct']}; DedeUserID={cookies['DedeUserID']}\n")

    print(f"\nCookie已保存到记事本文件: {txt_file}")

    cookie_file = os.path.join(script_dir, 'data', 'cookies.json')
    os.makedirs(os.path.dirname(cookie_file), exist_ok=True)

    data = {
        'cookies': cookies,
        'saved_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

    with open(cookie_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Cookie已保存到: {cookie_file}")

    config_file = os.path.join(script_dir, 'config.json')
    if os.path.exists(config_file):
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)

        cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
        config['bilibili']['cookies'] = cookie_str

        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)

        print(f"Cookie已更新到: {config_file}")


def main():
    print("=" * 60)
    print("B站Cookie自动获取工具")
    print("=" * 60)
    print("\n本程序会自动打开Chrome浏览器")
    print("请使用手机B站客户端扫码登录\n")
    input("按回车键开始...")
    try_selenium_login()


if __name__ == '__main__':
    main()
