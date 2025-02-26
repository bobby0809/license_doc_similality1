import os
import urllib.request
from bs4 import BeautifulSoup
import json
from chardet.universaldetector import UniversalDetector  # https://chardet.readthedocs.io/en/latest/usage.html#example-using-the-detect-function
import html5lib # for BeautifulSoup parser

encode_detector = UniversalDetector()
if not os.path.isfile('./config/FSF-licenses-full.json'): 
  try:
    with urllib.request.urlopen('https://wking.github.io/fsf-api/licenses-full.json') as res:
        body = res.read()
    encode_detector.reset()
    encode_detector.feed( body)
    if encode_detector.done:
        encode_detector.close()
        raw_doc =  body.decode(encode_detector.result['encoding'], errors='ignore' ) # .encode('utf-8', 'ignore')
    else:
        encode_detector.close()
        raw_doc =  body.decode('utf-8', errors='ignore')
    f = open("./config/FSF-licenses-full.json", "w", encoding='utf-8')
    f.write(raw_doc)
    f.close()
    license_metaData = json.loads(raw_doc)
  except urllib.error.HTTPError as err:
    print( 'licenses.json get failed', err)
    exit(1)
  except urllib.error.URLError as err:
    print( 'licenses.json get failed', err)
    exit(1)
else:
    f = open("./config/FSF-licenses-full.json", "r")
    # jsonデータを読み込んだファイルオブジェクトからPythonデータを作成
    license_metaData = json.load(f)
    # ファイルを閉じる
    f.close()
for licName,licMetaData in license_metaData['licenses'].items():
    lic_count = 0
    if (len(licMetaData.get('uris', [])) > 0):
        for url in licMetaData['uris']:
            if not url.startswith("https://www.gnu.org/licenses/license-list.html"):
                req = urllib.request.Request(url)
                try:
                    with urllib.request.urlopen(req) as res:
                        body = res.read()
                        contentType = (res.info().get('Content-Type', ''))
                    encode_detector.reset()
                    encode_detector.feed( body)
                    if encode_detector.done:
                        encode_detector.close()
                        raw_doc =  body.decode(encode_detector.result['encoding'], errors='ignore' ) # .encode('utf-8', 'ignore')
                    else:
                        encode_detector.close()
                        raw_doc =  body.decode('utf-8', errors='ignore')
                    try:
                        soup = BeautifulSoup(raw_doc, 'html5lib')
                        licSuffix = ""
                        if  url.startswith("https://directory.fsf.org/wiki") or url.startswith("http://directory.fsf.org/wiki"):
                            raw_doc = soup.find('pre').text
                            licSuffix = '.txt'
                        else:
                            # kill all script and style elements
                            for script in soup(["script", "style", "noscript","h1", "h2", "h3", "hr", "input", "button", "aside", "form", "label", "a"]):
                                script.extract()    # rip it out
                            raw_doc = soup.get_text()
                    finally:
                        pass 
                    print(licName + licSuffix ,contentType, url) 
                    f = open('./FSF_texts/' + licName + licSuffix ,  "w", encoding='utf-8')
                    f.write(raw_doc)
                    f.close()
                    lic_count = lic_count  + 1
                except urllib.error.HTTPError as err:
                    print( licName, url, err.code)
                except urllib.error.URLError as err:
                    print( licName, url, err.reason)
    if  lic_count <= 0:
        print(licName, '** no text found **')

  