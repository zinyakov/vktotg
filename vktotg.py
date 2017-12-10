#!/usr/bin/python3
# pip install bs4 vk_api telethon

import collections, os, sys, time, ssl
import shutil, requests
import webbrowser
import vk_api
import re
import discogsClientHelper
import time
from vk_api.audio import VkAudio

def captcha_handler(captcha):
  url = captcha.get_url()
  key = input("Enter captcha code {0}: ".format(url)).strip()
  webbrowser.open(url, new=2, autoraise=True)
  return captcha.try_again(key)

def auth_handler():
  key = input("Enter authentication code: ")
  remember_device = True
  return key, remember_device

def get(self, owner_id, offset=0):
  response = self._vk.http.get(
    'https://m.vk.com/audios{}'.format(owner_id),
    params={'offset': offset},
    allow_redirects=False
  )
  if not response.text:
    raise AccessDenied('You don\'t have permissions to browse {}\'s audio'.format(owner_id))
  return scrap_data(response.text)

def scrap_data(html):
  soup = BeautifulSoup(html, 'html.parser')
  tracks = []
  for audio in soup.find_all('div', {'class': 'audio_item ai_has_btn'}):
    ai_artist = audio.select('.ai_artist')
    artist = ai_artist[0].text
    link = audio.select('.ai_body')[0].input['value']
    if 'audio_api_unavailable' in link: link = decode_audio_url(link)
    tracks.append({
      'artist': artist,
      'title': audio.select('.ai_title')[0].text,
      'dur': audio.select('.ai_dur')[0]['data-dur'],
      'url': link
    })
  return tracks

def save(url, filename):
  response = requests.get(url, stream=True)
  with open(filename, 'wb') as out_file:
    shutil.copyfileobj(response.raw, out_file)
  del response

def auth_vk():
  print('First, log in to vk.com')
  folderName = 'Music '
  vk_session = vk_api.VkApi(
    'ringsheep@gmail.com',
    'IANCURTISIANCURTIS',
    captcha_handler=captcha_handler,
    auth_handler=auth_handler
  )

  try:
    vk_session.auth()
  except vk_api.AuthError as error_msg:
    print(error_msg)
    return

  user_id = vk_session.get_api().users.get()[0]['id']
  try:
    user_id = str(sys.argv[1])
    print('Downloading audios from ' + user_id)
  except: pass
  if not os.path.exists(folderName + str(user_id)): os.mkdir(folderName + str(user_id))
  return VkAudio(vk_session), user_id

def main():
  discogsHelper = discogsClientHelper.Helper()
  discogsHelper.authorize()
  folderName = 'parsed'

  vkaudio, user_id = auth_vk()
  progress = 0

  offset = 0
  audios = []
  last_chunk = []
  chunk = None
  while chunk != last_chunk:
    last_chunk = chunk
    chunk = vkaudio.get(user_id, None, offset)
    audios.extend(chunk)
    offset += 50
  total = len(audios)
  print()

  for i, track in enumerate(audios[::-1]):
    if progress and i < progress-1: continue
    filename = track['artist'] + ' - ' + track['title']
    escaped_filename = filename.replace("/","_")
    artist_name = re.split(" +- +", escaped_filename)[0]
    folder_path = folderName
    artist_path = folder_path + '/' + artist_name

    if not os.path.exists(artist_path): os.mkdir(artist_path)

    album_path = artist_path
    discogs_result = discogsHelper.search(escaped_filename, artist_name, 1)
    if len(discogs_result) > 0 :
        discogs_release_id_separator = '|#'
        album = discogs_result[0]
        print('album tracks ' + str(album.tracklist))
        for track in album.tracklist:
            print('keys ' + str(track.__dict__.{1!r}))
            # if track.__getitem__ == re.split(" +- +", escaped_filename)[1]:
            #     album_name = album.title.replace("/","_") + ' ' + discogs_release_id_separator + str(album.id)
            #     album_path = artist_path + '/' + album_name
            #     print('This track belongs to album ' + album_path)
    else:
        print('This track is off-album')

    if not os.path.exists(album_path): os.mkdir(album_path)

    file_path = './' + album_path + '/' + escaped_filename +'.mp3'
    if os.path.exists(file_path):
        print('File ' + file_path + ' already exists\n')
        continue
    else:
        print('File not found at path ' + file_path)


    print('Downloading [' + str(i+1) + '/' + str(total) + ']')
    try:
      save(track['url'], file_path)
    except HTTPError:
      print('ERROR: ' + escaped_filename)
    except ssl.SSLError:
      print('SSL ERROR: ' + escaped_filename + ', launching again...')
      try:
        save(track['url'], escaped_filename +'.mp3')
      except:
        print('Failed to save track after 2 tries [' + str(i+1) + '/' + str(total) + ']')
        exit()
    time.sleep(1)

    print()
    sys.stdout.flush()

if __name__ == '__main__': main()
