import discogs_client
import sys
from discogs_client.exceptions import HTTPError

music_style_to_search = 'punk'
music_country_origin = ''
music_release_year = '1981'


class Helper(object):
    client = None
    consumer_key = 'ktuXipaSlddjupSgzquo'
    consumer_secret = 'FhwRbJosOIjvroiKjrqfMjQjOAFZaMmI'
    user_agent = 'lostelectro-data-mining/1.0'
    access_token = "mVlXRwKrsQZNaTZItixcsDMUYGknKSmxWqePqJpN"
    access_secret = "ooGDdOtaRMLSONcBjBRAucCtzWPccuRwaCMVypOV"

    def __init__(self):
        self.client = discogs_client.Client(self.user_agent)
        self.client.set_consumer_key(self.consumer_key, self.consumer_secret)

    # запрашиваем новый токен, переходим по ссылке, вводим логин и пароль, получаем код верификации
    def request_new_token(self):
        token, secret, url = self.client.get_authorize_url()
        print(' == Request Token == ')
        print('    * oauth_token        = {0}'.format(token))
        print('    * oauth_token_secret = {0}'.format(secret))
        print()
        print('Please browse to the following URL {0}'.format(url))

        accepted = 'n'
        while accepted.lower() == 'n':
            print()
            accepted = input('Have you authorized me at {0} [y/n] :'.format(url))

        oauth_verifier = input('Verification code :')

        try:
            self.access_token, self.access_secret = self.client.get_access_token(oauth_verifier)
            print('access_token = {0}'.format(self.access_token))
            print('access_secret = {0}'.format(self.access_secret))
        except HTTPError as error:
            print('Unable to authenticate. {0}'.format(error))
            sys.exit(1)
        return

    def authorize(self):
        try:
            self.client.set_token(self.access_token, self.access_secret)
            test_auth = self.client.identity()
            print(test_auth)
        except HTTPError:
            self.request_new_token()

    def search(self, request, artist, track, page_number):
        try:
            results = self.client.search(request,
                                      type='release',
                                      artist=artist)
            return results.page(page_number - 1)
        except HTTPError as error:
            print('HTTPError {0}'.format(error))
            return []
