import re
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template

LINE_PARSER = re.compile(r'(?P<order>[\d]+).[\s]*(?P<name>.+?)[\s]*-[\s]*(?P<title>.+?)$')

# Test parser
test='6. Kieryn Darkwater - Visual Storytelling (comics!)'
group = LINE_PARSER.match(test).groupdict()
if group != {'order': '6', 'name': 'Kieryn Darkwater', 'title': 'Visual Storytelling (comics!)'}:
    raise Exception("parser needs work: %s" % group)

app = Flask(__name__)

def scrap(url):
    html = requests.get(url).content
    soup = BeautifulSoup(html, "html.parser")
    talks = {}
    for p in soup.find_all('p'):
        match = LINE_PARSER.finditer(p.text)
        if match:
            for m in match:
                data = m.groupdict() 
                talks[int(data['order'])] = data
    return talks

@app.route('/<int:speaker_number>/')
def hello_world(url="https://noisebridge.net/wiki/Five_Minutes_of_Fame_2017_01_26", speaker_number=0):
    talks = scrap(url)

    try:
        current_talk = talks[speaker_number]
        title = current_talk.get('title', '').strip('"\'')
        title = title.split('(')[0]
    except KeyError:
        current_talk = None
        title = 'Welcome to Five Minutes of Fame. First Talk Tonight @ 8pm' if speaker_number == 0 else \
            "Join us again next week | 5mof.com"

    return render_template('index.html', 
        talks=talks, speaker_number=speaker_number, current_talk=current_talk, title=title)


if __name__ == '__main__':
    app.run('0.0.0.0')

