import logging
import io
import argparse
import os
import time
import sys
from datetime import datetime
from pathlib import Path

from PIL import Image
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import (
    UnexpectedAlertPresentException,
    TimeoutException,
    NoAlertPresentException,
    ElementClickInterceptedException,
)
from webdriver_manager.chrome import ChromeDriverManager

# --- Global Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger()

SCREENSHOT_DIR = "screensave"
BASE_URL = "http://yield.chinabond.com.cn/cbweb-mn/yield_main?locale=en_US"


def save_element_screen(element, filename: Path):
    """Saves a screenshot of a specific element to a file."""
    filename.parent.mkdir(parents=True, exist_ok=True)
    try:
        img_bytes = element.screenshot_as_png
        image_stream = io.BytesIO(img_bytes)
        img = Image.open(image_stream)
        img.save(filename)
        logger.debug(f"Screenshot saved to {filename}")
    except Exception as e:
        logger.error(f"Failed to save screenshot {filename}: {e}")

# --- MODIFIED FUNCTION ---
def set_datepicker_date(driver: webdriver.Chrome, date_str: str):
    """选择日期控件的指定日期"""
    logger.info(f"Selecting date {date_str} in date picker...")
    year, month, day = map(int, date_str.split("-"))
    wait = WebDriverWait(driver, 10)

    # 1. 点击主页面日期输入框，弹出日期选择器
    date_input = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[5]/div/div[2]/div/div[1]/div/div[1]/div[1]/input")))
    date_input.click()
    time.sleep(0.5)

    # 2. 切换到日期选择器弹窗（不需要iframe）
    # 3. 找到年份和月份输入框
    year_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='dpTitle']//input[@class='yminput']")))
    month_input = wait.until(EC.visibility_of_element_located((By.XPATH, "//div[@id='dpTitle']//input[@class='mminput']")))

    # 4. 输入年份和月份
    year_input.click()
    year_input.clear()
    year_input.send_keys(str(year))
    month_input.click()
    month_input.clear()
    month_input.send_keys(str(month))

    # 5. 点标题区域触发刷新
    driver.find_element(By.ID, "dpTitle").click()
    time.sleep(0.5)

    # 6. 选日期
    day_str = str(int(day))
    day_xpath = f"//table[@class='WdayTable']//td[not(contains(@class, 'WotherDay')) and text()='{day_str}']"
    day_element = wait.until(EC.element_to_be_clickable((By.XPATH, day_xpath)))
    day_element.click()

# --- The rest of the file is unchanged ---
def get_single_data_point(driver: webdriver.Chrome, screen_element, output_dir: Path) -> tuple | None:
    """Reads a single maturity/yield data point from the table and takes a screenshot."""
    try:
        table_rows = driver.find_elements(By.XPATH, "//div[@id='dataTable']//tr[@id='tr0']/td")
        maturity, yield_pc = None, None
        for td in table_rows:
            if td.get_attribute('id') == "dcq0":
                maturity = td.get_attribute('innerHTML')
            elif td.get_attribute('id') == "syl0":
                yield_pc = td.get_attribute('innerHTML')
        
        if maturity and yield_pc:
            data_point = (float(maturity), float(yield_pc))
            screenshot_path = output_dir / SCREENSHOT_DIR / f"{data_point[0]:.2f}.png"
            save_element_screen(screen_element, screenshot_path)
            return data_point
    except (ValueError, TypeError) as e:
        logger.warning(f"Could not parse data point: {e}")
    return None


# def collect_data_from_graph(driver: webdriver.Chrome, output_dir: Path) -> list:
#     """Iterates through the interactive graph and collects all unique data points."""
#     logger.info("Starting data collection from the interactive graph...")
#     results = []
    
#     try:
#         screen = WebDriverWait(driver, 15).until(
#             EC.presence_of_element_located((By.ID, "main"))
#         )
#         graph = driver.find_element(By.XPATH, "//*[@id='container']//*[name()='svg']")
#     except TimeoutException:
#         logger.error("Graph or main container not found. This might be due to a search error (e.g., no data for the date).")
#         handle_alert(driver)
#         return []

#     ActionChains(driver).move_to_element(graph).perform()
#     time.sleep(0.5)

#     previous_results_count = -1
#     while len(results) > previous_results_count:
#         previous_results_count = len(results)
        
#         new_data = get_single_data_point(driver, screen, output_dir)
#         if new_data and new_data not in results:
#             results.append(new_data)
#             logger.info(f"Collected data point {len(results)}: {new_data}")
        
#         ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
#         time.sleep(0.1)

#     logger.info(f"Data collection complete. Total unique points found: {len(results)}")
#     return sorted(results)

def collect_data_from_graph(driver: webdriver.Chrome, output_dir: Path) -> list:
    """Iterates through the interactive graph and collects all unique data points."""
    logger.info("Starting data collection from the interactive graph...")
    results = []
    
    try:
        screen = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, "main"))
        )
        graph = driver.find_element(By.XPATH, "//*[@id='container']//*[name()='svg']")
    except TimeoutException:
        logger.error("Graph or main container not found. This might be due to a search error (e.g., no data for the date).")
        handle_alert(driver)
        return []

    # 移动到图表开始位置
    ActionChains(driver).move_to_element(graph).perform()
    time.sleep(1)

    # 收集数据点
    max_attempts = 100  # 防止无限循环
    no_new_data_count = 0
    max_no_new_data = 5  # 如果连续5次没有新数据，则停止
    
    for attempt in range(max_attempts):
        new_data = get_single_data_point(driver, screen, output_dir)
        
        if new_data:
            if new_data not in results:
                results.append(new_data)
                logger.info(f"Collected data point {len(results)}: {new_data}")
                no_new_data_count = 0
            else:
                no_new_data_count += 1
                logger.debug(f"Duplicate data point found: {new_data}")
        else:
            no_new_data_count += 1
            logger.debug("No data point found at current position")
        
        # 如果连续多次没有新数据，可能已经到达末尾
        if no_new_data_count >= max_no_new_data:
            logger.info(f"No new data for {max_no_new_data} attempts, assuming end of data")
            break
        
        # 移动到下一个数据点
        ActionChains(driver).send_keys(Keys.ARROW_RIGHT).perform()
        time.sleep(0.2)  # 稍微增加等待时间

    logger.info(f"Data collection complete. Total unique points found: {len(results)}")
    return sorted(results)


def write_results_to_csv(results: list, output_dir: Path, page_url: str, date_str: str):
    """Writes the collected data to a CSV file."""
    filename = output_dir / f"cn_yield_data_{date_str}.csv"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Writing {len(results)} data points to csv: {filename}")
    with open(filename, 'w', newline='') as f:
        f.write(f"Source,{page_url}\n")
        f.write(f"Date,{date_str}\n\n")
        f.write("Maturity,Yield\n")
        for data in results:
            f.write(f"{data[0]},{data[1]}\n")
    logger.info("Successfully saved CSV file.")


def handle_alert(driver: webdriver.Chrome) -> bool:
    """Checks for and handles a JavaScript alert. Returns True if an alert was handled."""
    try:
        alert = driver.switch_to.alert
        alert_text = alert.text
        logger.warning(f"Website alert detected: '{alert_text}'")
        alert.accept()
        logger.info("Alert accepted.")
        return True
    except NoAlertPresentException:
        return False

def main(date: str, output_dir_str: str):
    """Main function to orchestrate the web scraping process."""
    output_dir = Path(output_dir_str)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Initializing Chrome browser with automatic driver management...")
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless')  # 可以重新启用 headless 模式
    options.add_argument('--window-size=1920,1080')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--log-level=3')
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        logger.info(f"Loading page: {BASE_URL}")
        driver.get(BASE_URL)
        time.sleep(2)

        # Step 1: Select Curve Type
        logger.info("Selecting 'Spot rate curve' type...")
        dropdown_list = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "chartQuota"))
        )
        dropdown_list.click()
        time.sleep(0.5)
        
        curve_options = driver.find_elements(By.XPATH, "//div[@class='chartOptionsFlowTrend']//input[@name='xycheck']")
        
        # 清除所有选择
        for option in curve_options:
            if option.is_selected():
                option.click()
                time.sleep(0.1)
        
        # 只选择前两个选项（Yield to Maturity Curve 和 Spot Rate Curve）
        if len(curve_options) >= 2:
            curve_options[0].click()  # Yield to Maturity Curve
            time.sleep(0.1)
            curve_options[1].click()  # Spot Rate Curve
            logger.info("Selected both Yield to Maturity Curve and Spot Rate Curve")
        
        dropdown_list.click()
        time.sleep(0.5)

        # Step 2: Select Date - 这是关键部分！
        logger.info(f"Selecting date: {date}")
        date_img = driver.find_element(By.ID, "img_date")
        date_img.click()
        time.sleep(0.5)
        
        # 确保调用日期选择函数
        set_datepicker_date(driver, date)
        time.sleep(1)
        
        # 验证日期是否正确设置
        try:
            date_input = driver.find_element(By.ID, "date")
            selected_date = date_input.get_attribute("value")
            logger.info(f"Date field shows: {selected_date}")
        except:
            logger.warning("Could not verify selected date")

        # Step 3: Search
        logger.info("Clicking search button...")
        search_button = driver.find_element(By.XPATH, "//button[contains(text(), 'Search')]")
        search_button.click()
        
        time.sleep(3)
        
        # 检查是否有警告
        if handle_alert(driver):
            logger.error(f"Search failed for date {date}. No data found.")
            return

        # Step 4: Collect Data
        logger.info("Starting data collection...")
        results = collect_data_from_graph(driver, output_dir)

        if not results:
            logger.warning("Failed to collect any data points.")
            return

        # Step 5: Save Results
        write_results_to_csv(results, output_dir, BASE_URL, date)
        logger.info(f"Process completed successfully. Collected {len(results)} data points.")

    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        debug_path = output_dir / "error_screenshot.png"
        driver.save_screenshot(str(debug_path))
        logger.info(f"Saved a debug screenshot to {debug_path}")
            
    finally:
        logger.info("Closing browser.")
        driver.quit()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Scrape ChinaBond yield curve data for a specific date.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "-d", "--date",
        type=str,
        default="2024-07-26", # A known recent valid date
        help="The date to scrape data for, in YYYY-MM-DD format. Must be a trading day."
    )
    parser.add_argument(
        "-o", "--output-dir",
        type=str,
        default="output",
        help="The directory to save CSV files and screenshots."
    )
    args = parser.parse_args()

    try:
        datetime.strptime(args.date, "%Y-%m-%d")
    except ValueError:
        logger.error(f"Invalid date format: '{args.date}'. Please use YYYY-MM-DD.")
        sys.exit(1)

    main(date=args.date, output_dir_str=args.output_dir)