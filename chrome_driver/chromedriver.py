from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # 导入 Service 类
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

url_frp = "http://139.155.140.154:7500/static/#/"

chrome_options = Options()

service = Service(r"C:\Software\chrome114\Chrome-bin\chromedriver.exe")

#chrome_options.add_argument("--headless")  # 无界面模式（可选）
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...")
chrome_options.add_argument("--ignore-certificate-errors")  # 忽略证书错误
chrome_options.add_argument("--ignore-ssl-errors")          # 忽略SSL错误

#try:
    # 需提前下载ChromeDriver（与Chrome版本匹配）
if 1 :
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.get(url_frp)
    driver.implicitly_wait(10)  # 等待动态加载（秒）
    
    alert = WebDriverWait(driver,10).until(EC.alert_is_present())
    #username_field = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@placeholder='用户名' or contains(@name, 'user')]")))
    #username_field.send_keys("root")  # 替换为实际用户名
    
    
    #alert = driver.switch_to.alert()

    print(alert.text)
    # 示例：获取页面标题
    print("页面标题:", driver.title)
    
    # 示例：点击按钮（需替换实际元素ID）
    # button = driver.find_element(By.ID, "submit-btn")
    # button.click()
    
    # 示例：截屏保存（无界面模式下有效）
    #driver.save_screenshot("page_screenshot.png")
    
#except Exception as e:
 #   print(f"❌ Selenium操作失败: {e}")
#finally:
#    driver.quit()  # 必须关闭浏览器进程