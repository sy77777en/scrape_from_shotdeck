# #!/usr/bin/env python3
# import os
# import time
# import requests
# import argparse
# from pathlib import Path
# from selenium import webdriver
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.support import expected_conditions as EC
# from selenium.common.exceptions import TimeoutException
#
#
# class ShotDeckDownloader:
#     def __init__(self, username, password, output_dir="./downloads"):
#         self.username = username
#         self.password = password
#         self.output_dir = Path(output_dir)
#         self.images_dir = self.output_dir / "images"
#         self.videos_dir = self.output_dir / "videos"
#
#         # 创建输出目录
#         self.images_dir.mkdir(parents=True, exist_ok=True)
#         self.videos_dir.mkdir(parents=True, exist_ok=True)
#
#         self.session = requests.Session()
#         self.driver = None
#
#         # 设置请求头
#         self.session.headers.update({
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
#             'Referer': 'https://shotdeck.com/',
#             'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
#             'Accept-Language': 'en-US,en;q=0.9',
#             'Accept-Encoding': 'gzip, deflate, br',
#             'Connection': 'keep-alive',
#         })
#
#     def setup_driver(self):
#         """设置Chrome WebDriver"""
#         try:
#             chrome_options = Options()
#             chrome_options.add_argument("--headless")
#             chrome_options.add_argument("--no-sandbox")
#             chrome_options.add_argument("--disable-dev-shm-usage")
#             chrome_options.add_argument("--window-size=1920,1080")
#
#             self.driver = webdriver.Chrome(options=chrome_options)
#             self.driver.implicitly_wait(10)
#             print("✓ Chrome WebDriver 初始化成功")
#             return True
#         except Exception as e:
#             print(f"✗ Chrome WebDriver 初始化失败: {e}")
#             return False
#
#     def login_and_get_cookies(self):
#         """登录ShotDeck并获取认证cookies"""
#         try:
#             if not self.setup_driver():
#                 return False
#
#             print("正在登录ShotDeck...")
#             self.driver.get("https://shotdeck.com/welcome/login")
#
#             # 等待登录表单加载
#             WebDriverWait(self.driver, 10).until(
#                 EC.presence_of_element_located((By.NAME, "user"))
#             )
#
#             # 填写登录信息
#             self.driver.find_element(By.NAME, "user").send_keys(self.username)
#             self.driver.find_element(By.NAME, "pass").send_keys(self.password)
#
#             # 勾选"保持登录"
#             try:
#                 stay_logged_in = self.driver.find_element(By.ID, "stayLoggedIn")
#                 if not stay_logged_in.is_selected():
#                     stay_logged_in.click()
#             except:
#                 print("注意: 未找到'保持登录'选项")
#
#             # 提交登录表单
#             self.driver.find_element(By.XPATH, "//button[@type='submit']").click()
#
#             # 等待登录完成
#             try:
#                 WebDriverWait(self.driver, 15).until(
#                     lambda driver: any(keyword in driver.current_url.lower()
#                                        for keyword in ["welcome/home", "browse/stills", "dashboard"])
#                 )
#                 print("✓ 登录成功!")
#
#                 # 获取cookies
#                 cookies = self.driver.get_cookies()
#                 for cookie in cookies:
#                     self.session.cookies.set(cookie['name'], cookie['value'])
#
#                 print(f"✓ 获取到 {len(cookies)} 个cookies")
#                 return True
#
#             except TimeoutException:
#                 current_url = self.driver.current_url
#                 print(f"✗ 登录可能失败，当前页面: {current_url}")
#
#                 # 检查是否有错误消息
#                 try:
#                     error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning")
#                     for element in error_elements:
#                         if element.text.strip():
#                             print(f"错误信息: {element.text}")
#                 except:
#                     pass
#
#                 return False
#
#         except Exception as e:
#             print(f"✗ 登录过程出错: {e}")
#             return False
#         finally:
#             if self.driver:
#                 self.driver.quit()
#
#     def test_image_urls(self, shot_id):
#         """测试不同的图片URL格式"""
#         test_urls = [
#             f"https://shotdeck.com/assets/images/stills/{shot_id}.jpg",
#             f"https://shotdeck.com/assets/images/stills/{shot_id}.png",
#             f"https://shotdeck.com/assets/images/stills/large_{shot_id}.jpg",
#             f"https://shotdeck.com/assets/images/stills/medium_{shot_id}.jpg",
#             f"https://shotdeck.com/assets/images/stills/small_{shot_id}.jpg",
#         ]
#
#         print(f"\n测试 SHOT_ID: {shot_id}")
#         working_urls = []
#
#         for url in test_urls:
#             try:
#                 response = self.session.head(url, timeout=10)
#                 status = response.status_code
#                 content_type = response.headers.get('content-type', 'unknown')
#                 content_length = response.headers.get('content-length', '0')
#
#                 print(f"  {url}")
#                 print(f"    状态: {status}, 类型: {content_type}, 大小: {content_length}")
#
#                 if status == 200 and ('image' in content_type.lower() or 'octet-stream' in content_type.lower()):
#                     working_urls.append((url, content_length))
#
#             except Exception as e:
#                 print(f"  {url} -> 错误: {e}")
#
#         return working_urls
#
#     def validate_file(self, filepath):
#         """验证文件是否为有效的媒体文件"""
#         try:
#             if not filepath.exists() or filepath.stat().st_size < 1024:
#                 return False, "文件不存在或太小"
#
#             # 读取文件头
#             with open(filepath, 'rb') as f:
#                 header = f.read(16)
#
#             # 检查常见的文件签名
#             if header.startswith(b'\xFF\xD8\xFF'):
#                 return True, "JPEG"
#             elif header.startswith(b'\x89\x50\x4E\x47'):
#                 return True, "PNG"
#             elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
#                 return True, "GIF"
#             elif b'ftyp' in header[:12]:
#                 return True, "MP4"
#             elif header.startswith(b'\x00\x00\x00'):
#                 # 可能是MP4的另一种格式
#                 return True, "MP4 (可能)"
#             elif b'<html' in header[:100].lower() or b'<!doctype' in header[:100].lower():
#                 return False, "HTML错误页面"
#             else:
#                 # 如果文件大于10KB，可能是有效的，即使我们不识别格式
#                 if filepath.stat().st_size > 10240:
#                     return True, f"未知格式但文件较大 ({filepath.stat().st_size} bytes)"
#                 return False, f"未知格式，文件头: {header[:8].hex()}"
#
#         except Exception as e:
#             return False, f"验证错误: {e}"
#
#     def download_file(self, url, filepath, file_type):
#         """下载单个文件"""
#         try:
#             # 检查文件是否已存在且有效
#             if filepath.exists():
#                 is_valid, reason = self.validate_file(filepath)
#                 if is_valid:
#                     print(f"  - {file_type}已存在且有效，跳过: {filepath.name}")
#                     return True
#                 else:
#                     print(f"  - 删除无效的现有文件: {filepath.name} ({reason})")
#                     filepath.unlink()
#
#             print(f"  下载{file_type}: {url}")
#
#             # 下载文件
#             response = self.session.get(url, stream=True, timeout=30)
#
#             if response.status_code != 200:
#                 print(f"  ✗ HTTP错误: {response.status_code}")
#                 return False
#
#             # 检查Content-Type
#             content_type = response.headers.get('content-type', '').lower()
#             if 'text/html' in content_type:
#                 print(f"  ✗ 返回HTML页面，可能是错误页面")
#                 return False
#
#             # 保存文件
#             with open(filepath, 'wb') as f:
#                 for chunk in response.iter_content(chunk_size=8192):
#                     f.write(chunk)
#
#             # 验证下载的文件
#             is_valid, reason = self.validate_file(filepath)
#             if is_valid:
#                 file_size = filepath.stat().st_size
#                 print(f"  ✓ {file_type}下载成功: {filepath.name} ({file_size:,} bytes) - {reason}")
#                 return True
#             else:
#                 print(f"  ✗ 下载的文件无效: {reason}")
#                 filepath.unlink()
#                 return False
#
#         except Exception as e:
#             print(f"  ✗ {file_type}下载失败: {e}")
#             if filepath.exists():
#                 filepath.unlink()
#             return False
#
#     def download_shot_id(self, shot_id, download_images=True, download_videos=True):
#         """下载指定shot_id的文件"""
#         print(f"\n处理 SHOT_ID: {shot_id}")
#         results = {'image': False, 'video': False}
#
#         if download_images:
#             # 尝试多种图片URL格式
#             image_urls = [
#                 (f"https://shotdeck.com/assets/images/stills/{shot_id}.jpg", ".jpg"),
#                 (f"https://shotdeck.com/assets/images/stills/{shot_id}.png", ".png"),
#                 (f"https://shotdeck.com/assets/images/stills/large_{shot_id}.jpg", "_large.jpg"),
#                 (f"https://shotdeck.com/assets/images/stills/medium_{shot_id}.jpg", "_medium.jpg"),
#                 (f"https://shotdeck.com/assets/images/stills/small_{shot_id}.jpg", "_small.jpg"),
#             ]
#
#             for url, suffix in image_urls:
#                 image_file = self.images_dir / f"{shot_id}{suffix}"
#                 if self.download_file(url, image_file, "图片"):
#                     results['image'] = True
#                     break
#
#         if download_videos:
#             # 尝试多种视频URL
#             video_urls = [
#                 f"https://crunch.shotdeck.com/assets/images/clips/{shot_id}_clip.mp4",
#                 f"https://shotdeck.com/assets/images/clips/{shot_id}_clip.mp4",
#                 f"https://crunch.shotdeck.com/assets/videos/clips/{shot_id}_clip.mp4",
#             ]
#
#             for url in video_urls:
#                 video_file = self.videos_dir / f"{shot_id}_clip.mp4"
#                 if self.download_file(url, video_file, "视频"):
#                     results['video'] = True
#                     break
#
#         return results
#
#     def download_from_file(self, shot_ids_file, download_images=True, download_videos=True, test_first=3):
#         """从文件批量下载"""
#         # 登录并获取认证
#         if not self.login_and_get_cookies():
#             print("✗ 登录失败，无法继续")
#             return False
#
#         # 读取SHOT_IDs
#         try:
#             with open(shot_ids_file, 'r', encoding='utf-8') as f:
#                 shot_ids = [line.strip() for line in f if line.strip()]
#         except FileNotFoundError:
#             print(f"✗ 找不到文件: {shot_ids_file}")
#             return False
#         except Exception as e:
#             print(f"✗ 读取文件失败: {e}")
#             return False
#
#         if not shot_ids:
#             print("✗ 文件中没有找到SHOT_ID")
#             return False
#
#         print(f"\n找到 {len(shot_ids)} 个SHOT_ID")
#         print(f"输出目录: {self.output_dir}")
#         print(f"下载图片: {download_images}")
#         print(f"下载视频: {download_videos}")
#
#         # 测试前几个ID
#         if test_first > 0 and len(shot_ids) >= test_first:
#             print(f"\n=== 测试前 {test_first} 个ID ===")
#             for i in range(test_first):
#                 self.test_image_urls(shot_ids[i])
#                 time.sleep(1)
#
#             response = input(f"\n按Enter继续下载全部{len(shot_ids)}个，或输入'q'退出: ").strip().lower()
#             if response == 'q':
#                 print("用户取消下载")
#                 return False
#
#         # 开始批量下载
#         print(f"\n=== 开始批量下载 ===")
#         stats = {
#             'images_success': 0,
#             'images_failed': 0,
#             'videos_success': 0,
#             'videos_failed': 0
#         }
#
#         for i, shot_id in enumerate(shot_ids, 1):
#             print(f"\n[{i}/{len(shot_ids)}] 处理: {shot_id}")
#
#             try:
#                 results = self.download_shot_id(shot_id, download_images, download_videos)
#
#                 if download_images:
#                     if results['image']:
#                         stats['images_success'] += 1
#                     else:
#                         stats['images_failed'] += 1
#
#                 if download_videos:
#                     if results['video']:
#                         stats['videos_success'] += 1
#                     else:
#                         stats['videos_failed'] += 1
#
#             except KeyboardInterrupt:
#                 print("\n用户中断下载")
#                 break
#             except Exception as e:
#                 print(f"  ✗ 处理出错: {e}")
#                 if download_images:
#                     stats['images_failed'] += 1
#                 if download_videos:
#                     stats['videos_failed'] += 1
#
#             # 添加延迟避免请求过快
#             time.sleep(0.5)
#
#         # 显示统计结果
#         print("\n" + "=" * 50)
#         print("下载完成!")
#
#         if download_images:
#             total_images = stats['images_success'] + stats['images_failed']
#             success_rate = (stats['images_success'] / total_images * 100) if total_images > 0 else 0
#             print(f"图片: 成功 {stats['images_success']}, 失败 {stats['images_failed']}, 成功率 {success_rate:.1f}%")
#             print(f"图片保存在: {self.images_dir}")
#
#         if download_videos:
#             total_videos = stats['videos_success'] + stats['videos_failed']
#             success_rate = (stats['videos_success'] / total_videos * 100) if total_videos > 0 else 0
#             print(f"视频: 成功 {stats['videos_success']}, 失败 {stats['videos_failed']}, 成功率 {success_rate:.1f}%")
#             print(f"视频保存在: {self.videos_dir}")
#
#         return True
#
#
# def main():
#     parser = argparse.ArgumentParser(
#         description="ShotDeck 认证下载器",
#         formatter_class=argparse.RawDescriptionHelpFormatter,
#         epilog="""
# 使用示例:
#   python3 shotdeck_downloader.py my_ids.txt -u user@email.com -p password
#   python3 shotdeck_downloader.py my_ids.txt -u user -p pass --images-only
#   python3 shotdeck_downloader.py my_ids.txt -u user -p pass --output-dir /path/to/save
#         """
#     )
#
#     parser.add_argument("shot_ids_file", help="包含SHOT_ID的文件路径")
#     parser.add_argument("-u", "--username", required=True, help="ShotDeck用户名/邮箱")
#     parser.add_argument("-p", "--password", required=True, help="ShotDeck密码")
#     parser.add_argument("--images-only", action="store_true", help="只下载图片")
#     parser.add_argument("--videos-only", action="store_true", help="只下载视频")
#     parser.add_argument("--output-dir", default="./downloads", help="输出目录 (默认: ./downloads)")
#     parser.add_argument("--test-first", type=int, default=3, help="先测试前N个ID (默认: 3, 设为0跳过测试)")
#
#     args = parser.parse_args()
#
#     # 验证参数
#     if args.images_only and args.videos_only:
#         print("错误: --images-only 和 --videos-only 不能同时使用")
#         return 1
#
#     # 检查文件是否存在
#     if not os.path.exists(args.shot_ids_file):
#         print(f"错误: 找不到文件 {args.shot_ids_file}")
#         return 1
#
#     # 确定下载选项
#     download_images = not args.videos_only
#     download_videos = not args.images_only
#
#     # 创建下载器
#     downloader = ShotDeckDownloader(args.username, args.password, args.output_dir)
#
#     # 开始下载
#     try:
#         success = downloader.download_from_file(
#             args.shot_ids_file,
#             download_images=download_images,
#             download_videos=download_videos,
#             test_first=args.test_first
#         )
#         return 0 if success else 1
#
#     except KeyboardInterrupt:
#         print("\n用户取消操作")
#         return 1
#     except Exception as e:
#         print(f"程序出错: {e}")
#         return 1
#
#
# if __name__ == "__main__":
#     exit(main())

# !/usr/bin/env python3
import os
import time
import json
import requests
import argparse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class ShotDeckDownloader:
    def __init__(self, username, password, output_dir="./downloads"):
        self.username = username
        self.password = password
        self.output_dir = Path(output_dir).resolve()  # Get absolute path
        self.images_dir = self.output_dir / "images"
        self.videos_dir = self.output_dir / "videos"

        print(f"Output directory will be: {self.output_dir}")
        print(f"Images directory: {self.images_dir}")
        print(f"Videos directory: {self.videos_dir}")

        # Create output directories
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)

        print(f"✓ Created output directories")

        self.session = requests.Session()
        self.driver = None

        # Set request headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://shotdeck.com/',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        })

    def setup_driver(self):
        """Setup Chrome WebDriver"""
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--window-size=1920,1080")

            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.implicitly_wait(10)
            print("✓ Chrome WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"✗ Chrome WebDriver initialization failed: {e}")
            return False

    def login_and_get_cookies(self):
        """Login to ShotDeck and get authentication cookies"""
        try:
            if not self.setup_driver():
                return False

            print("Logging in to ShotDeck...")
            self.driver.get("https://shotdeck.com/welcome/login")

            # Wait for login form to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "user"))
            )

            # Fill in login information
            self.driver.find_element(By.NAME, "user").send_keys(self.username)
            self.driver.find_element(By.NAME, "pass").send_keys(self.password)

            # Check "Stay logged in"
            try:
                stay_logged_in = self.driver.find_element(By.ID, "stayLoggedIn")
                if not stay_logged_in.is_selected():
                    stay_logged_in.click()
            except:
                print("Note: 'Stay logged in' option not found")

            # Submit login form
            self.driver.find_element(By.XPATH, "//button[@type='submit']").click()

            # Wait for login completion
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: any(keyword in driver.current_url.lower()
                                       for keyword in ["welcome/home", "browse/stills", "dashboard"])
                )
                print("✓ Login successful!")

                # Get cookies
                cookies = self.driver.get_cookies()
                for cookie in cookies:
                    self.session.cookies.set(cookie['name'], cookie['value'])

                print(f"✓ Retrieved {len(cookies)} cookies")
                return True

            except TimeoutException:
                current_url = self.driver.current_url
                print(f"✗ Login may have failed, current page: {current_url}")

                # Check for error messages
                try:
                    error_elements = self.driver.find_elements(By.CSS_SELECTOR, ".error, .alert, .warning")
                    for element in error_elements:
                        if element.text.strip():
                            print(f"Error message: {element.text}")
                except:
                    pass

                return False

        except Exception as e:
            print(f"✗ Login process error: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()

    def test_image_urls(self, shot_id):
        """Test different image URL formats"""
        test_urls = [
            f"https://shotdeck.com/assets/images/stills/{shot_id}.jpg",
            f"https://shotdeck.com/assets/images/stills/{shot_id}.png",
            f"https://shotdeck.com/assets/images/stills/large_{shot_id}.jpg",
            f"https://shotdeck.com/assets/images/stills/medium_{shot_id}.jpg",
            f"https://shotdeck.com/assets/images/stills/small_{shot_id}.jpg",
        ]

        print(f"\nTesting SHOT_ID: {shot_id}")
        working_urls = []

        for url in test_urls:
            try:
                response = self.session.head(url, timeout=10)
                status = response.status_code
                content_type = response.headers.get('content-type', 'unknown')
                content_length = response.headers.get('content-length', '0')

                print(f"  {url}")
                print(f"    Status: {status}, Type: {content_type}, Size: {content_length}")

                if status == 200 and ('image' in content_type.lower() or 'octet-stream' in content_type.lower()):
                    working_urls.append((url, content_length))

            except Exception as e:
                print(f"  {url} -> Error: {e}")

        return working_urls

    def validate_file(self, filepath):
        """Validate if file is a valid media file"""
        try:
            if not filepath.exists() or filepath.stat().st_size < 1024:
                return False, "File doesn't exist or too small"

            # Read file header
            with open(filepath, 'rb') as f:
                header = f.read(16)

            # Check common file signatures
            if header.startswith(b'\xFF\xD8\xFF'):
                return True, "JPEG"
            elif header.startswith(b'\x89\x50\x4E\x47'):
                return True, "PNG"
            elif header.startswith(b'GIF87a') or header.startswith(b'GIF89a'):
                return True, "GIF"
            elif b'ftyp' in header[:12]:
                return True, "MP4"
            elif header.startswith(b'\x00\x00\x00'):
                # Possibly another MP4 format
                return True, "MP4 (possible)"
            elif b'<html' in header[:100].lower() or b'<!doctype' in header[:100].lower():
                return False, "HTML error page"
            else:
                # If file is larger than 10KB, might be valid even if we don't recognize format
                if filepath.stat().st_size > 10240:
                    return True, f"Unknown format but large file ({filepath.stat().st_size} bytes)"
                return False, f"Unknown format, header: {header[:8].hex()}"

        except Exception as e:
            return False, f"Validation error: {e}"

    def download_file(self, url, filepath, file_type):
        """Download single file"""
        try:
            # Check if file already exists and is valid
            if filepath.exists():
                is_valid, reason = self.validate_file(filepath)
                if is_valid:
                    print(f"  - {file_type} already exists and valid, skipping: {filepath.name}")
                    return True
                else:
                    print(f"  - Deleting invalid existing file: {filepath.name} ({reason})")
                    filepath.unlink()

            print(f"  Downloading {file_type}: {url}")

            # Download file
            response = self.session.get(url, stream=True, timeout=30)

            if response.status_code != 200:
                print(f"  ✗ HTTP error: {response.status_code}")
                return False

            # Check Content-Type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' in content_type:
                print(f"  ✗ Returned HTML page, possibly error page")
                return False

            # Save file
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Validate downloaded file
            is_valid, reason = self.validate_file(filepath)
            if is_valid:
                file_size = filepath.stat().st_size
                print(f"  ✓ {file_type} downloaded successfully: {filepath.name} ({file_size:,} bytes) - {reason}")
                return True
            else:
                print(f"  ✗ Downloaded file invalid: {reason}")
                filepath.unlink()
                return False

        except Exception as e:
            print(f"  ✗ {file_type} download failed: {e}")
            if filepath.exists():
                filepath.unlink()
            return False

    def download_shot_id(self, shot_id, download_images=True, download_videos=True, keyword=None):
        """Download files for specified shot_id"""
        keyword_info = f" (keyword: {keyword})" if keyword else ""
        print(f"\nProcessing SHOT_ID: {shot_id}{keyword_info}")
        results = {'image': False, 'video': False}

        if download_images:
            # Try multiple image URL formats
            image_urls = [
                (f"https://shotdeck.com/assets/images/stills/{shot_id}.jpg", ".jpg"),
                (f"https://shotdeck.com/assets/images/stills/{shot_id}.png", ".png"),
                (f"https://shotdeck.com/assets/images/stills/large_{shot_id}.jpg", "_large.jpg"),
                (f"https://shotdeck.com/assets/images/stills/medium_{shot_id}.jpg", "_medium.jpg"),
                (f"https://shotdeck.com/assets/images/stills/small_{shot_id}.jpg", "_small.jpg"),
            ]

            for url, suffix in image_urls:
                # Include keyword in filename if provided
                if keyword:
                    sanitized_keyword = self._sanitize_filename(keyword)
                    image_file = self.images_dir / f"{shot_id}_{sanitized_keyword}{suffix}"
                else:
                    image_file = self.images_dir / f"{shot_id}{suffix}"

                if self.download_file(url, image_file, "Image"):
                    results['image'] = True
                    break

        if download_videos:
            # Try multiple video URLs
            video_urls = [
                f"https://crunch.shotdeck.com/assets/images/clips/{shot_id}_clip.mp4",
                f"https://shotdeck.com/assets/images/clips/{shot_id}_clip.mp4",
                f"https://crunch.shotdeck.com/assets/videos/clips/{shot_id}_clip.mp4",
            ]

            for url in video_urls:
                # Include keyword in filename if provided
                if keyword:
                    sanitized_keyword = self._sanitize_filename(keyword)
                    video_file = self.videos_dir / f"{shot_id}_{sanitized_keyword}_clip.mp4"
                else:
                    video_file = self.videos_dir / f"{shot_id}_clip.mp4"

                if self.download_file(url, video_file, "Video"):
                    results['video'] = True
                    break

        return results

    def _sanitize_filename(self, filename):
        """Sanitize string for use in filename"""
        invalid_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*', ' ']
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()

    def load_shot_ids_from_json(self, json_file):
        """Load shot IDs from JSON file created by the extractor"""
        json_path = Path(json_file).resolve()
        print(f"Loading JSON file: {json_path}")

        if not json_path.exists():
            print(f"✗ JSON file does not exist: {json_path}")
            return {}, []

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            print(f"✓ Successfully loaded JSON file")
            shot_ids_by_keyword = {}
            all_shot_ids = []

            # Process each keyword (skip _summary)
            for keyword, info in data.items():
                if keyword.startswith('_'):  # Skip metadata like _summary
                    continue

                if isinstance(info, dict) and 'shot_ids' in info:
                    shot_ids = info['shot_ids']
                    shot_ids_by_keyword[keyword] = shot_ids
                    all_shot_ids.extend(shot_ids)
                    print(f"Found {len(shot_ids)} shot IDs for keyword: '{keyword}'")

            # Remove duplicates while preserving order
            unique_shot_ids = []
            seen = set()
            for shot_id in all_shot_ids:
                if shot_id not in seen:
                    unique_shot_ids.append(shot_id)
                    seen.add(shot_id)

            print(f"\nTotal unique shot IDs: {len(unique_shot_ids)}")
            print(f"Total shot IDs (with duplicates): {len(all_shot_ids)}")

            return shot_ids_by_keyword, unique_shot_ids

        except FileNotFoundError:
            print(f"✗ File not found: {json_path}")
            return {}, []
        except json.JSONDecodeError as e:
            print(f"✗ Invalid JSON format: {e}")
            return {}, []
        except Exception as e:
            print(f"✗ Error loading JSON file: {e}")
            return {}, []

    def load_shot_ids_from_text(self, text_file):
        """Load shot IDs from text file (backwards compatibility)"""
        try:
            with open(text_file, 'r', encoding='utf-8') as f:
                shot_ids = [line.strip() for line in f if line.strip()]
            return {}, shot_ids
        except FileNotFoundError:
            print(f"✗ File not found: {text_file}")
            return {}, []
        except Exception as e:
            print(f"✗ Error reading text file: {e}")
            return {}, []

    def download_from_file(self, input_file, download_images=True, download_videos=True, test_first=3,
                           organize_by_keyword=False):
        """Download from file (supports both JSON and text formats)"""
        # Login and get authentication
        if not self.login_and_get_cookies():
            print("✗ Login failed, cannot continue")
            return False

        # Determine file type and load shot IDs
        if input_file.lower().endswith('.json'):
            print("Detected JSON file format")
            shot_ids_by_keyword, all_shot_ids = self.load_shot_ids_from_json(input_file)
        else:
            print("Detected text file format")
            shot_ids_by_keyword, all_shot_ids = self.load_shot_ids_from_text(input_file)

        if not all_shot_ids:
            print("✗ No shot IDs found in file")
            return False

        print(f"\nFound {len(all_shot_ids)} total shot IDs")
        print(f"Output directory: {self.output_dir}")
        print(f"Download images: {download_images}")
        print(f"Download videos: {download_videos}")
        print(f"Organize by keyword: {organize_by_keyword}")

        # Test first few IDs
        if test_first > 0 and len(all_shot_ids) >= test_first:
            print(f"\n=== Testing first {test_first} IDs ===")
            for i in range(min(test_first, len(all_shot_ids))):
                self.test_image_urls(all_shot_ids[i])
                time.sleep(1)

            response = input(
                f"\nPress Enter to continue downloading all {len(all_shot_ids)}, or 'q' to quit: ").strip().lower()
            if response == 'q':
                print("User canceled download")
                return False

        # Start batch download
        print(f"\n=== Starting batch download ===")
        stats = {
            'images_success': 0,
            'images_failed': 0,
            'videos_success': 0,
            'videos_failed': 0,
            'by_keyword': {}
        }

        if organize_by_keyword and shot_ids_by_keyword:
            # Download organized by keyword
            total_processed = 0
            for keyword, shot_ids in shot_ids_by_keyword.items():
                print(f"\n{'=' * 60}")
                print(f"Processing keyword: '{keyword}' ({len(shot_ids)} shot IDs)")
                print(f"{'=' * 60}")

                stats['by_keyword'][keyword] = {
                    'images_success': 0, 'images_failed': 0,
                    'videos_success': 0, 'videos_failed': 0
                }

                for i, shot_id in enumerate(shot_ids, 1):
                    total_processed += 1
                    print(
                        f"\n[{total_processed}/{len(all_shot_ids)}] ({keyword} {i}/{len(shot_ids)}) Processing: {shot_id}")

                    try:
                        results = self.download_shot_id(shot_id, download_images, download_videos, keyword)

                        if download_images:
                            if results['image']:
                                stats['images_success'] += 1
                                stats['by_keyword'][keyword]['images_success'] += 1
                            else:
                                stats['images_failed'] += 1
                                stats['by_keyword'][keyword]['images_failed'] += 1

                        if download_videos:
                            if results['video']:
                                stats['videos_success'] += 1
                                stats['by_keyword'][keyword]['videos_success'] += 1
                            else:
                                stats['videos_failed'] += 1
                                stats['by_keyword'][keyword]['videos_failed'] += 1

                    except KeyboardInterrupt:
                        print("\nUser interrupted download")
                        return self._print_stats(stats, download_images, download_videos)
                    except Exception as e:
                        print(f"  ✗ Processing error: {e}")
                        if download_images:
                            stats['images_failed'] += 1
                            stats['by_keyword'][keyword]['images_failed'] += 1
                        if download_videos:
                            stats['videos_failed'] += 1
                            stats['by_keyword'][keyword]['videos_failed'] += 1

                    # Add delay to avoid requests too fast
                    time.sleep(0.5)
        else:
            # Download all shot IDs without keyword organization
            for i, shot_id in enumerate(all_shot_ids, 1):
                print(f"\n[{i}/{len(all_shot_ids)}] Processing: {shot_id}")

                try:
                    results = self.download_shot_id(shot_id, download_images, download_videos)

                    if download_images:
                        if results['image']:
                            stats['images_success'] += 1
                        else:
                            stats['images_failed'] += 1

                    if download_videos:
                        if results['video']:
                            stats['videos_success'] += 1
                        else:
                            stats['videos_failed'] += 1

                except KeyboardInterrupt:
                    print("\nUser interrupted download")
                    break
                except Exception as e:
                    print(f"  ✗ Processing error: {e}")
                    if download_images:
                        stats['images_failed'] += 1
                    if download_videos:
                        stats['videos_failed'] += 1

                # Add delay to avoid requests too fast
                time.sleep(0.5)

        return self._print_stats(stats, download_images, download_videos, organize_by_keyword)

    def _print_stats(self, stats, download_images, download_videos, organize_by_keyword=False):
        """Print download statistics"""
        print("\n" + "=" * 50)
        print("Download completed!")

        if download_images:
            total_images = stats['images_success'] + stats['images_failed']
            success_rate = (stats['images_success'] / total_images * 100) if total_images > 0 else 0
            print(
                f"Images: Success {stats['images_success']}, Failed {stats['images_failed']}, Success rate {success_rate:.1f}%")
            print(f"Images saved in: {self.images_dir}")

        if download_videos:
            total_videos = stats['videos_success'] + stats['videos_failed']
            success_rate = (stats['videos_success'] / total_videos * 100) if total_videos > 0 else 0
            print(
                f"Videos: Success {stats['videos_success']}, Failed {stats['videos_failed']}, Success rate {success_rate:.1f}%")
            print(f"Videos saved in: {self.videos_dir}")

        # Print per-keyword stats if organized by keyword
        if organize_by_keyword and stats['by_keyword']:
            print(f"\n{'=' * 30} Per-keyword stats {'=' * 30}")
            for keyword, kw_stats in stats['by_keyword'].items():
                print(f"\n'{keyword}':")
                if download_images:
                    img_total = kw_stats['images_success'] + kw_stats['images_failed']
                    img_rate = (kw_stats['images_success'] / img_total * 100) if img_total > 0 else 0
                    print(f"  Images: {kw_stats['images_success']}/{img_total} ({img_rate:.1f}%)")
                if download_videos:
                    vid_total = kw_stats['videos_success'] + kw_stats['videos_failed']
                    vid_rate = (kw_stats['videos_success'] / vid_total * 100) if vid_total > 0 else 0
                    print(f"  Videos: {kw_stats['videos_success']}/{vid_total} ({vid_rate:.1f}%)")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="ShotDeck Authenticated Downloader with JSON support",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Usage examples:
  # Download from JSON file (from extractor)
  python3 shotdeck_downloader.py shotid.json -u user@email.com -p password

  # Download from text file (backwards compatibility)
  python3 shotdeck_downloader.py my_ids.txt -u user@email.com -p password

  # Download with keyword organization in filenames
  python3 shotdeck_downloader.py shotid.json -u user -p pass --organize-by-keyword

  # Images only
  python3 shotdeck_downloader.py shotid.json -u user -p pass --images-only

  # Custom output directory
  python3 shotdeck_downloader.py shotid.json -u user -p pass --output-dir /path/to/save
        """
    )

    parser.add_argument("input_file", help="JSON file with shot IDs (from extractor) or text file with shot IDs")
    parser.add_argument("-u", "--username", required=True, help="ShotDeck username/email")
    parser.add_argument("-p", "--password", required=True, help="ShotDeck password")
    parser.add_argument("--images-only", action="store_true", help="Download images only")
    parser.add_argument("--videos-only", action="store_true", help="Download videos only")
    parser.add_argument("--organize-by-keyword", action="store_true",
                        help="Include keyword in filenames (only works with JSON input)")
    parser.add_argument("--output-dir", default="./downloads", help="Output directory (default: ./downloads)")
    parser.add_argument("--test-first", type=int, default=3,
                        help="Test first N IDs (default: 3, set to 0 to skip testing)")

    args = parser.parse_args()

    # Validate arguments
    if args.images_only and args.videos_only:
        print("Error: --images-only and --videos-only cannot be used together")
        return 1

    # Check if file exists
    if not os.path.exists(args.input_file):
        print(f"Error: File not found {os.path.abspath(args.input_file)}")
        print(f"Current working directory: {os.getcwd()}")
        print("Files in current directory:")
        try:
            for f in os.listdir('.'):
                print(f"  {f}")
        except:
            pass
        return 1

    # Determine download options
    download_images = not args.videos_only
    download_videos = not args.images_only

    # Create downloader
    downloader = ShotDeckDownloader(args.username, args.password, args.output_dir)

    # Start download
    try:
        success = downloader.download_from_file(
            args.input_file,
            download_images=download_images,
            download_videos=download_videos,
            test_first=args.test_first,
            organize_by_keyword=args.organize_by_keyword
        )
        return 0 if success else 1

    except KeyboardInterrupt:
        print("\nUser canceled operation")
        return 1
    except Exception as e:
        print(f"Program error: {e}")
        return 1


if __name__ == "__main__":
    exit(main())