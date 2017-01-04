from rauth.service import OAuth1Service, OAuth1Session
from argparse import ArgumentParser
import xml.etree.ElementTree as ET
import distance 
import sys

# get keys from goodreads 
# MY_KEY = GET CONSUMER KEY FROM GOODREADS.COM
# MY_SECRET = GET CONSUMER SECRET FROM GOODREADS.COM

goodreads = OAuth1Service(
    consumer_key= MY_KEY,
    consumer_secret= MY_SECRET,
    name='goodreads',
    request_token_url='http://www.goodreads.com/oauth/request_token',
    authorize_url='http://www.goodreads.com/oauth/authorize',
    access_token_url='http://www.goodreads.com/oauth/access_token',
    base_url='http://www.goodreads.com/')

request_token, request_token_secret = goodreads.get_request_token(header_auth=True)
authorize_url = goodreads.get_authorize_url(request_token)

#authorize this app 
print 'Visit this URL in your browser: ' + authorize_url
accepted = 'n'
while accepted.lower() == 'n':
    accepted = raw_input('Have you authorized me? (y/n) ')
session = goodreads.get_auth_session(request_token, request_token_secret)

#read through the text file, each line is parsed as a separate entry 
file_name = raw_input('Enter name of .txt file with book titles: ')
with open(file_name) as f:
    for book in f:
        first_match = None 
        data = {'q': book, 'page':1 ,'key': MY_KEY,'search[field]':'title'}
        book_xml = session.get('https://www.goodreads.com/search/index.xml', params = data)
        tree = ET.fromstring(book_xml.content)
        # these values are what you need to save for subsequent access.
        ACCESS_TOKEN = session.access_token
        ACCESS_TOKEN_SECRET = session.access_token_secret
        new_session = OAuth1Session(
            consumer_key = MY_KEY,
            consumer_secret = MY_SECRET,
            access_token = ACCESS_TOKEN,
            access_token_secret = ACCESS_TOKEN_SECRET,
        )
        #try to locate an exact match on the title 
        exact_match = False
        for node in tree.findall('.//best_book'):
            title = node.find(".//title").text
            author = node.find(".//name").text
            book_id = int(node.find(".//id").text)
            if title.lower() == book.lower(): 
                book_data = {'name': 'to-read', 'book_id': book_id}
                response = new_session.post('http://www.goodreads.com/shelf/add_to_shelf.xml', data = book_data)
                if response.status_code == 201:
                    print('\x1b[6;30;42m' + "Successfully added " + title + " by " + author + '\x1b[0m')
                    exact_match = True
                    break
            if first_match is None:
                    #save first match 
                    first_match = (title, author, book_id)
        #no exact match exists so we choose the first match returned by the API
        if exact_match is False:
            #we will select the first match with a warning
            if first_match: 
                book_data = {'name': 'to-read', 'book_id': first_match[2]}
                response = new_session.post('http://www.goodreads.com/shelf/add_to_shelf.xml', data = book_data)
                if response.status_code == 201:
                    print('\x1b[6;30;43m' + "Warning: No exact matches found. Added " + first_match[0] + " by " + first_match[1] + '\x1b[0m')
                else: 
                    print('\x1b[6;30;41m' + "Error adding " + book + '\x1b[0m')
            else:
                print('\x1b[6;30;41m' + "Error adding " + book + '\x1b[0m')
