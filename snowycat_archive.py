#!.snowenv/bin/python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 15 17:50:44 2026

@author: Akshay S
akshaysvk0@gmail.com
akshaysmin@gmail.com
"""

"""
Requirements:
selenium 3.141.0
proxy.py 2.4.4.dev12+g4248a1f97
Mozilla Firefox 146.0.1
geckodriver 0.34.0
"""
import sys
import os
import subprocess
from datetime import datetime
from time import sleep
import random
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from getpass import getpass

get_filename = lambda file : os.path.basename(file)


def create_proxy_extension(proxy_host, proxy_port, proxy_user, proxy_pass):
    """Creates a Firefox extension to handle proxy authentication."""

    # 1. The manifest file
    manifest_json = """
    {
        "version": "1.0.0",
        "manifest_version": 2,
        "name": "Firefox Proxy Auth",
        "permissions": [
            "proxy",
            "tabs",
            "unlimitedStorage",
            "storage",
            "<all_urls>",
            "webRequest",
            "webRequestBlocking"
        ],
        "background": {
            "scripts": ["background.js"]
        }
    }
    """

    # 2. The background script that provides the credentials
    background_js = f"""
    var config = {{
        mode: "fixed_servers",
        rules: {{
            singleProxy: {{
                scheme: "http",
                host: "{proxy_host}",
                port: parseInt({proxy_port})
            }},
            bypassList: ["localhost"]
        }}
    }};

    browser.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

    browser.webRequest.onAuthRequired.addListener(
        function callbackFn(details) {{
            return {{
                authCredentials: {{
                    username: "{proxy_user}",
                    password: "{proxy_pass}"
                }}
            }};
        }},
        {{urls: ["<all_urls>"]}},
        ["blocking"]
    );
    """

    # Create the extension zip file (.xpi)
    plugin_file = 'proxy_auth_plugin.xpi'
    with zipfile.ZipFile(plugin_file, 'w') as zp:
        zp.writestr("manifest.json", manifest_json)
        zp.writestr("background.js", background_js)

    return os.path.abspath(plugin_file)

def open_browser():
    # firefox options
    service = Service(geckodriver_path)
    options = Options()
    if not display:
        options.add_argument('-headless')
    # --- 1. Disable all background pings ---
    options.set_preference("network.captive-portal-service.enabled", False)
    options.set_preference("browser.safebrowsing.malware.enabled", False)
    options.set_preference("browser.safebrowsing.phishing.enabled", False)
    options.set_preference("browser.selfsupport.url", "")
    options.set_preference("browser.tabs.remote.autostart", False)
    options.set_preference("extensions.update.enabled", False)
    options.set_preference("app.update.auto", False)
    options.set_preference("app.update.enabled", False)
    # --- 2. Disable Proxy Autodiscovery  ---
    # 0 = No proxy, 1 = Manual, 2 = PAC, 4 = Auto-detect, 5 = System
    options.set_preference("network.proxy.type", 1) 
    options.set_preference("network.proxy.http", "127.0.0.1")
    options.set_preference("network.proxy.http_port", 8899)
    options.set_preference("network.proxy.ssl", "127.0.0.1")
    options.set_preference("network.proxy.ssl_port", 8899)
    options.set_preference("network.proxy.no_proxies_on", "localhost, 127.0.0.1")
    options.set_preference("network.http.proxy-auth-per-host", False)
    options.set_preference("signon.autologin.proxy", True)
    # --- 3. Start at about:blank ---
    options.set_preference("browser.startup.page", 0)
    options.set_preference("browser.startup.homepage", "about:blank")
    # open driver
    driver = webdriver.Firefox(options=options, executable_path=geckodriver_path, firefox_binary=firefox_binary)
    #driver = webdriver.Firefox(service=service, options=options)
    driver.install_addon(extension_path, temporary=True)
    driver.implicitly_wait(50)
    #refresh(driver)
    print('opened driver')
    driver.get(upload_website)
    sleep(2)
    refresh(driver)
    driver.find_element(By.NAME, 'username').send_keys(usname)
    sleep(2*random.random())
    driver.find_element(By.NAME, 'username').send_keys(Keys.TAB)
    sleep(2*random.random())
    driver.find_element(By.NAME, 'password').send_keys(passwd)
    sleep(2*random.random())
    driver.find_element(By.NAME, 'password').send_keys(Keys.ENTER)
    driver.maximize_window()
    return driver

def refresh(driver):
    refresh_counter = 10
    for i in range(refresh_counter):
        try:
            driver.refresh()
            sleep(20)
            rows = driver.find_elements(By.CLASS_NAME, "checkbox-cell")
            return True
        except:
            print('refreshing ', i, 'th time failed')
            sleep(20 + 10*random.random())
    return False

def drag_and_drop_file(drop_target, path):
    try:
        JS_DROP_FILE = """
        var target = arguments[0],
            offsetX = arguments[1],
            offsetY = arguments[2],
            document = target.ownerDocument || document,
            window = document.defaultView || window;
    
        var input = document.createElement('INPUT');
        input.type = 'file';
        input.onchange = function () {
          var rect = target.getBoundingClientRect(),
              x = rect.left + (offsetX || (rect.width >> 1)),
              y = rect.top + (offsetY || (rect.height >> 1)),
              dataTransfer = { files: this.files };
    
          ['dragenter', 'dragover', 'drop'].forEach(function (name) {
            var evt = document.createEvent('MouseEvent');
            evt.initMouseEvent(name, !0, !0, window, 0, 0, 0, x, y, !1, !1, !1, !1, 0, null);
            evt.dataTransfer = dataTransfer;
            target.dispatchEvent(evt);
          });
    
          setTimeout(function () { document.body.removeChild(input); }, 25);
        };
        document.body.appendChild(input);
        return input;
        """
        driver = drop_target.parent
        file_input = driver.execute_script(JS_DROP_FILE, drop_target, 0, 0)
        file_input.send_keys(path)
    except Exception as E:
        print(E)
        print('Error in drag and drop', datetime.today())
        #drag_and_drop_file(drop_target, path)

def keep_active(driver):
    elements = driver.find_element(By.CLASS_NAME, "progress-items").find_elements(By.XPATH, './/*')
    #missed_uploads = [elem.text.split('/')[-1] for elem in elements if elem.text.strip()!='']
    #print(missed_uploads)
    progress = 0
    progress2 = 0
    while progress!='Done':
        elements = driver.find_element(By.CLASS_NAME, "progress-items").find_elements(By.TAG_NAME, "progress")#find_elements(By.XPATH, './/*')
        element = random.choice(elements)
        print(element.location_once_scrolled_into_view)
        print(element.text)
        #element.click()
        try:
            progress2 = driver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div[1]/div/div[1]/span").text
            #print(progress2)
            did_exception = False
        except:
            did_exception = True
            print('Could not retrieve current proress, instead got', progress2)
        if not did_exception: progress = progress2
        print(progress)
        #rows_text = ''
        #for i in range(len(driver.find_elements(By.TAG_NAME, "tr"))):
        #    elems = driver.find_elements(By.TAG_NAME, "tr")
        #    if len(elems)<i:
        #        elem = elems[i]
        #    rows_text += elem.text
        #for filename in missed_uploads:
        #    if filename in rows_text:
        #        while filename in missed_uploads:
        #            missed_uploads.remove(filename)
        sleep(2)
    return #missed_uploads

#actions = ActionChains(driver)
#actions.send_keys(usname)
#sleep(3+3*random.random())
#actions.send_keys(Keys.TAB)
#sleep(3+3*random.random())
#actions.send_keys(passwd)
#sleep(3+3*random.random())
#actions.send_keys(Keys.ENTER)


#mode = input('Press Enter to start program \n>>')

def extract_and_upload_files(files2upload): # archive, files2upload
    driver = open_browser()
    n = len(files2upload)
    untar_process = subprocess.Popen(['tar', '-xzf', archive, files2upload[0]])
    uploaded_files = []
    for i,upload_file in enumerate(files2upload):
        # Extract file from compressed archive
        untar_status = untar_process.wait()
        print(f'{untar_status=}')
        if i<n-1: # extract files2upload[i+1]
            untar_process = subprocess.Popen(['tar', '-xzf', archive, files2upload[i+1]])
        # refresh until uploads are transfered
        #refresh()
        uploading = True
        upload_file = os.path.realpath(upload_file)
        while uploading:
            i+=1
            rows = driver.find_elements(By.TAG_NAME, "tr")
            print(len(rows))
            while len(rows)>5:
                refresh_success = refresh(driver)
                print('refresh success : ', refresh_success)
                sleep(1+2*random.random())
                rows = driver.find_elements(By.TAG_NAME, "tr")
            
            # upload next file
            filename = os.path.basename(upload_file)
                
            #sleep(10)
        
            rows_text = ''.join([elem.text for elem in driver.find_elements(By.TAG_NAME, "tr")])
            
            count_refresh_to_get_filename_in_rows = 0
            while filename not in rows_text:
                print(datetime.today())
                refresh_success = refresh(driver)
                count_refresh_to_get_filename_in_rows += 1
                print('refresh success : ', refresh_success)
                print('Uploading ', i, '/', n, ' : ',  upload_file)
                if (not refresh_success) or (count_refresh_to_get_filename_in_rows>10):
                    remaining_files = sorted(list(set(files2upload) - set(uploaded_files)))
                    print('files remaining:\n')
                    print(*remaining_files, sep='\t')
                    print('Refresh success : ', refresh_success)
                    print('Retries to see uploaded file in server : ', count_refresh_to_get_filename_in_rows)
                    print('---------------------->{ Re-opening browser }<----------------------')
                    driver.quit()
                    sleep(5)
                    return extract_and_upload_files(remaining_files)
                #dropzone = driver.find_element(By.ID, 'dropzone')
                try:
                    dropzone = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.ID, "dropzone")))
                except:
                    continue
                drag_and_drop_file(dropzone, upload_file)
                keep_active(driver)
                rows_text = ''.join([elem.text for elem in driver.find_elements(By.TAG_NAME, "tr")])
            try:
                _ = driver.find_element(By.CLASS_NAME, "progress-items").find_element(By.TAG_NAME, "progress").find_elements(By.CLASS_NAME, "is-primary")
                uploading = False
                uploaded_files.append(upload_file)
            except:
                print('Danger progress bar', datetime.today())
                sleep(10+10*random.random())   #####!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                refresh_success = refresh(driver)
                #driver.quit()
                #upload_files(filesremaining)
                print('refresh success : ', refresh_success)
    
            #uploading = False
    
    """
    while True:
        print('Waiting for new uploads')
        q = input('Press Enter after uploading to keep active')
        if q == 'exit' or q=='exit()':
            break
        try:
            r = keep_active(driver)
            print(r)
        except:
            print('Some Error Occured')
    """
    print('Completed all uploads')
    driver.close()
    return sorted(list(set(files2upload) - set(uploaded_files)))



if __name__=='__main__':

    # Handle command line arguments
    display = False
    if '-d' in sys.argv:
        display = True
        sys.argv.remove('-d')
    elif '--display' in sys.argv:
        display = True
        sys.argv.remove('--display')
    files2exclude = []
    if '-ex' in sys.argv:
        parser = sys.argv.index('-ex')
        files2exclude = [os.path.realpath(file) for file in sys.argv[parser:]]
        sys.argv = sys.argv[:parser]
    files2upload = []
    if len(sys.argv)>=3:
        archive = os.path.realpath(sys.argv[1])
        files2upload = [os.path.realpath(file) for file in sys.argv[2:]]
    else:
        print('Usage : ')
        #print('dev_snowycat_archive.py <archive.tar> ')
        print('dev_snowycat_archive.py <archive.tar> <files to extract and upload one by one> ')
        print('dev_snowycat_archive.py <archive.tar> <files to extract and upload one by one> -ex <files to exclude from uploading>')
    assert os.path.exists(archive)
    workdir = os.path.dirname(archive)
    os.chdir(workdir)
    files2upload = [ file for file in files2upload 
                       if not any(get_filename(file).startswith( get_filename(ex) ) 
                                  for ex in files2exclude
                                 )
                   ]
    scriptdir = os.path.dirname(os.path.realpath(__file__))
    print(f'scriptdir = {scriptdir}')

    # Path to your executables
    geckodriver_path = os.path.join(scriptdir, 'geckodriver-v0.34.0-linux64/geckodriver')
    firefox_binary = os.path.join(scriptdir, 'firefox-146.0.1/firefox/firefox')

    # Get auth details from auth.info
    try:
        with open('auth.info') as f:
            exec(f.read())
    except FileNotFoundError:
        print('File "auth.info" not found! Create file "auth.info" in the following format:\n\n')
        print('''
proxy_host = '<proxy.host.address>'
proxy_port = '<port_number>'
username = '<username>'
password = '<password>'
upload_website = '<http://website.to.upload.files.site/'
            ''')

    # Get info not present in auth.info
    for var in ['proxy_host', 'proxy_port', 'upload_website']:
        if var not in dir():
            exec(f"{var} = input('{var} : ')")
    for var in ['username', 'password']:
        if var not in dir():
            exec(f"{var} = getpass('{var} : ')")

    # Create the extension
    extension_path = create_proxy_extension(proxy_host, proxy_port, username, password)

    # Start proxy for browser
    proxy_process = subprocess.Popen(['proxy', '--plugins', 'proxy.plugin.ProxyPoolPlugin', '--proxy-pool', f'http://{username}:{password}@{proxy_host}:{proxy_port}'])

    # open browser and upload files in archive
    print(files2upload)
    extract_and_upload_files(files2upload)

    # Stop proxy for browser
    proxy_process.terminate()

