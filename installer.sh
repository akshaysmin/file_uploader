# install packages in virtual environment
python3 -m venv .snowenv
source .snowenv/bin/activate
pip install selenium==3.141.0
pip install proxy.py==2.4.4

# make scripts use python from the virtual environment
cwd=$(pwd)
pattern='1s|^#!.*$|#!'${cwd}'/.snowenv/bin/activate|'
for file in dev_snowycat.py dev_snowycat_folder.py dev_snowycat_archive.py
    do
        sed -i "${pattern}" $file
        chmod +x $file
    done

# download and extract geckodriver
wget https://github.com/akshaysmin/file_uploader/blob/69b7f1aeeaef20d5cb2960a75c445095cfbfd61a/geckodriver-v0.34.0-linux64.tar.gz
# uncomment the next line if geckodriver download fails in previous line. you can also go to the link and manually download this version
# wget https://github.com/mozilla/geckodriver/releases/download/v0.34.0/geckodriver-v0.34.0-linux64.tar.gz
mkdir geckodriver-v0.34.0-linux64
tar -xvf geckodriver-v0.34.0-linux64.tar.gz --directory geckodriver-v0.34.0-linux64

# download and extract browser
wget https://ftp.mozilla.org/pub/firefox/releases/146.0.1/linux-x86_64/en-US/firefox-146.0.1.tar.xz
mkdir firefox-146.0.1
tar -xvf firefox-146.0.1.tar.xz --directory firefox-146.0.1

# deactivate virtual environment after installation
deactivate
