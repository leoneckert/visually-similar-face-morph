from bs4 import BeautifulSoup
import urllib2, requests
import re
import random
import os, shutil
import cv2
import dlib
import tools as t

detector = dlib.get_frontal_face_detector()
#  base_url = 'https://yandex.ru/images/search?rpt=imageview&img_url='


#url = "http://files.leoneckert.com/original.resized.with_margin.face_no_frame_1.jpg"
#  url = "http://files.leoneckert.com/original.resized.with_margin.face_no_frame_0.jpg"

def download_file(url, local_filename):
    #  local_filename = url.split('/')[-1]
    #  local_filename = os.path.join(dir_for_tests, local_filename)
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local_filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)
                #f.flush() commented by recommendation from J.F.Sebastian
    return local_filename

def has_face(path):
    img = cv2.imread(path)
    img_with_margin = t.add_margin_to_image(img, factor = 0.5)
    rects = t.get_rects(img_with_margin)
    if len(rects) > 0: return True
    else: return False

#  def download_vs_image(input_path, dir_for_tests, outputpath):
def get_vs_links(input_path):
    
    base_url = 'https://yandex.ru/images/search?rpt=imageview&img_url='
    name = "/".join(input_path.split('/')[-2:])
    print "NAME", name
    url = "http://138.197.5.177/static/images/" + name
    print "URL", url

    url = base_url + url
    html = urllib2.urlopen(url).read()
    soup = BeautifulSoup(html, 'html.parser')

    imgs = soup.find_all('img')

    similar_links = list()

    for img in soup.findAll('img', attrs={'class': re.compile(r".*\bsimilar__image\b.*")}):
    # for img in imgs:
        try:
            # if 'similar__image' in img['class']:
            similar_img = "https:"+str(img['src'])
            similar_links.append(similar_img)
            print "added link"
        except KeyError:
            print "this is an error, why?"
            print img
            pass
    random.shuffle(similar_links)
    print similar_links
    return similar_links
    #  if not os.path.isdir(dir_for_tests):
    #      os.makedirs(dir_for_tests)
    #  while len(similar_links) > 0:
    #      link = similar_links[-1]
    #      similar_links = similar_links[:-1]
    #      local_filename = download_file(link, dir_for_tests)
    #      print local_filename
    #      if has_face(local_filename):
    #          shutil.copy(local_filename, outputpath)
    #          return True
    #          break
    #  return False

#  download_vs_image("dsds/dds/ds/original.resized.with_margin.face_no_frame_0.jpg", "images", "images/face_0_similar_original.jpg")
