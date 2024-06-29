import tkinter as tk
from tkinter import ttk
import threading
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# 브라우저 드라이버 인스턴스를 저장할 리스트
drivers = []

# 락 생성
driver_lock = threading.Lock()

def init_driver():
    options = uc.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')

    driver = uc.Chrome(options=options)
    return driver

def do_login(driver):
    driver.get('https://velog.io')

    # 로그인 버튼 클릭
    login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="로그인"]'))
    )
    login_button.click()

    # 구글 로그인 버튼 클릭
    google_login_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="Google"]'))
    )
    google_login_button.click()

    # 새 탭으로 구글 로그인 페이지 이동
    driver.switch_to.window(driver.window_handles[1])

    # 이메일 입력
    email_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'identifierId'))
    )
    email_input.send_keys('******************')  # 여기에 실제 구글 이메일 입력

    next_button = driver.find_element(By.ID, 'identifierNext')
    next_button.click()

    # 비밀번호 입력
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'password'))
    )
    password_input.send_keys('***************')  # 여기에 실제 구글 비밀번호 입력

    next_button = driver.find_element(By.ID, 'passwordNext')
    next_button.click()

    # 로그인 완료 확인
    driver.switch_to.window(driver.window_handles[0])
    WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, '//button[text()="새 글 작성"]'))
    )

def open_youtube_with_selenium(url):
    with driver_lock:
        driver = init_driver()
        do_login(driver)
        drivers.append(driver)  # 드라이버 인스턴스를 리스트에 추가
        driver.get(url)

        try:
            # 페이지가 완전히 로드될 때까지 기다림
            WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "video")))

            # JavaScript를 사용하여 자동 재생 시도
            driver.execute_script("""
                var video = document.querySelector('video');
                if (video) {
                    video.play();
                } else {
                    var button = document.querySelector('button.ytp-large-play-button');
                    if (button) {
                        button.click();
                    }
                }
            """)
        except Exception as e:
            print(f"Error: {e}")

def open_youtube():
    url = entry_url.get()
    # 여러 서버에서 실행할 수 있도록 스레드로 실행
    threads = []
    for _ in range(3):  # 예제로 3개의 서버로 설정 (필요한 서버 수만큼 반복)
        t = threading.Thread(target=open_youtube_with_selenium, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

def close_browsers():
    for driver in drivers:
        driver.quit()
    drivers.clear()

# GUI 생성
root = tk.Tk()
root.title("YouTube Live Stream Viewer")

# 스타일 적용
style = ttk.Style()
style.configure('TButton', font=('calibri', 10, 'bold'), foreground='black', background='lightgray')
style.configure('TLabel', font=('calibri', 12, 'bold'), foreground='blue')

# URL 입력 필드 및 라벨 생성
label_url = ttk.Label(root, text="YouTube URL:")
label_url.grid(row=0, column=0, padx=10, pady=10)
entry_url = ttk.Entry(root, width=40)
entry_url.grid(row=0, column=1, padx=10, pady=10)

# 방송 보기 버튼
btn_watch = ttk.Button(root, text="Watch", command=open_youtube)
btn_watch.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

# 종료 버튼
btn_close = ttk.Button(root, text="Close Browsers", command=close_browsers)
btn_close.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

# GUI 시작
root.mainloop()