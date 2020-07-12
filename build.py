from lib import NotionWebsiteBuilder
from secret import token
import regex as re

import os
import argparse

import sys

parser = argparse.ArgumentParser()
parser.add_argument('--push', action='store_true', help='Commit and push new changes')
parser.add_argument('--forcepush', action='store_true', help='Commit and push new changes')
parser.add_argument('--serve', action='store_true', help='Commit and push new changes')
args = parser.parse_args()

website = NotionWebsiteBuilder(token_v2=token)

sitedata = {
    'wordcount': 0,
    'pagecount': 0,
    'glossary': {}
}

def addGlossaryItem(data):
    match = re.match(r'(.+)\((.+)\):(.+)', data['block']['rawtext'])
    if match != None:
        item, category, glossary_text = match.groups()
        if category not in sitedata['glossary']:
            sitedata['glossary'][category] = {}
        
        sitedata['glossary'][category.strip()][item.strip()] = glossary_text.strip()

def countwords(data):
    block = data['block']
    page = data['page']

    if block['type'] not in ['code', 'callout'] and 'rawtext' in block:
        if not block['rawtext']: 
            print(block['rawtext'])
            block['rawtext'] = ''
        count = len(block['rawtext'].split())
        sitedata['wordcount'] += count

        #page['wordcount'] = page['wordcount'] + count if 'wordcount' in page else count
        page['wordcount'] += count

def countpages(page):
    # reset wordcount (for cached pages)
    page['wordcount'] = 0

    sitedata['pagecount'] += 1

    if 'edited' in page:
        print(page['edited'])

def setflags(page):
    page['flags'] = {
        'new': page['flags'] == 'new',
        'updated': page['flags'] == 'updated'
    }

def test(page):
    if 'cover' in page:
        print(page['cover'])
    if 'thumbnail' in page:
        print(page['thumbnail'])


website.templates['blocks']['callout']['👉'] = """
<a class="pagecover" href="{{ href }}">
    <img src="{{cover_image}}" />
</a>
"""

# website.templates['blocks']['page'] = """
# {% if id in cache %}
# <a class="pagelink" href="{{ cache[id].path }}">
#     {% if cache[id].thumbnail %}
#         <div class="pagelink-icon" style="background-image: url({{ cache[id].thumbnail[0] }})"></div>
#     {% else %}
#         <div class="pagelink-icon" style="background-image: url(/thumbnail.png)"></div>
#     {% endif %}

#     <div class="pagelink-text">
#         <div class="pagelink-text-title">{{ cache[id].name }}</div>
#         <div class="pagelink-text-description">{% if cache[id].description %}{{ cache[id].description }}{% endif %}</div>
#     </div>

#     <svg class="pagelink-arrow" width="104" height="104" viewBox="0 0 104 104" fill="none" xmlns="http://www.w3.org/2000/svg">
#         <path d="M52.1739 2L100 52M100 52L52.1739 102M100 52H0" stroke="black" stroke-width="5"/>
#     </svg>
# </a>
# {% elif id %}
# ERROR {{ id }}
# {% endif %}
# """
# website.templates['blocks']['link_to_page'] = website.templates['blocks']['page']

def test2(data):
    page_id = data['block']['text'][0][1][0][1]
    if page_id in website.cache:
        data['block']['cover_image'] = website.cache[page_id]['cover'][0]
        data['block']['href'] = website.cache[page_id]['path']
    else:
        print('COVER FOR PAGE ' + page_id + ' NOT FOUND')

website.listen('blocks/callout/🔮', addGlossaryItem)
website.listen('blocks/callout/👉', test2)
website.listen('blocks', countwords)
website.listen('pages', countpages)
website.listen('pages', setflags)
website.listen('pages', test)


website.addCollection('pages', 'https://www.notion.so/xiqo/d4bc1e0d76644a58b31dea6159354538?v=55bdd5f4295847d295d83d97c42d7ff2', folder='')
website.addCollection('projects', 'https://www.notion.so/xiqo/fbe593a66bcc45388a455934a73459d9?v=279245a2926f4cf5b497dd327cd6841b')
website.addCollection('blog', 'https://www.notion.so/xiqo/b4d0b773477a4f008d6397d2dbdc19af?v=c5e1f2be13a041babd4da4231bb1661f')
website.addCollection('offerings', 'https://www.notion.so/xiqo/00b6c2c4a2fb4c53ae98a87cb7da4634?v=0887bfaee7e44bdea2e465a4527d9732')

#for page in website.cache.values():
#    page['flags'] = {
#        'new': False,
#        'updated': False
#    }

from datetime import datetime
def fromiso(iso):
    if type(iso) == str:
        return datetime.fromisoformat(iso)
    elif type(iso) == datetime:
        return iso
    else:
        print(iso)
        print(type(iso))
        print('ERROR WRONG fromiso FORMAT %s' % iso)
        #return datetime.now()
        
website.env.globals['datetime'] = datetime
website.env.globals['fromiso'] = fromiso

#def wordcount_to_freq(wordcount):
#   return 
website.env.filters['wordcount_to_freq'] = lambda x: int(min(200.0 + max(x, 0) / 5000.0 * 19700.0, 19900.0) / 100.0) * 100

cwd = os.getcwd()

os.chdir(os.path.join(os.getcwd(), 'notes'))
import importlib
notes = importlib.import_module('notes.build')

os.chdir(cwd)

sitedata['wordcount'] += notes.wordcount
sitedata['pagecount'] += notes.pagecount

website.render({
    'site': sitedata
})

# generate glossary in .ndtl format for Merveille's collaborative wiki
with open(os.path.join('public', 'glossary.ndtl'), 'w') as f:
    for category in sitedata['glossary']:
        f.write(category.upper() + '\n')

        for term, definition in sitedata['glossary'][category].items():
            f.write('  {} : {}\n'.format(term, definition))



website.saveCache()

print(sitedata['glossary'])

import subprocess, sys
import random

messages = [
    "AUTOMAGIC BUILD",
    "RETICULATING SPLINES",
    "TRANSFERRING VITAL INFORMATION",
    "WRITING WORDS",
    "WORDS HAVE BEEN WRITTEN",
    "NEW CONTENT REPLACES OLD",
    "IN WITH THE NEW OUT WITH THE OLD",
    "THE GIT THAT KEEPS ON GIVING",
    "MAY THE --FORCE BE WITH YOU",
    "CECI N'EST PAS UNE COMMIT",
    "TO UPDATE ONE'S WEBSITE SHOWS TRUE COMMITMENT",
    "ADDED ANOTHER PAGE ABOUT GIRAFFES",
    "RECONCEPTUALIZING MEMEX SOFTWARE PROTOCOL",
    "ADJUSTING BELL CURVES",
    "ALIGNING COVARIANCE MATRICES",
    "INSERTING SUBMLIMINAL MESSAGES",
    "REARRANGING PLANCK UNITS",
    "DECONSTRUCTING CONCEPTUAL PHENOMENA",
    "DECIPHERING SQUIGGLY SYMBOLS",
    "QUARANTINING RADIOACTIVE PAGES",
    "MULTIPLYING UNKNOWN CONSTANTS",
    "REDESCRIBING THE UNDESCRIBABLE",
    "¿COMMIT GIT OR GIT COMMIT?",
    "UNRAVELLING THE ENCYCLOPEDIA",
    "INITIALIZING LINGUISTIC SUPERPOSITION",
    "UPDATING MIND CONTROL MANTRAS",
    "CORRECT HORSE BATTERY STAPLE",
    
]

#if (args.push and did_anything_change) or (args.forcepush):
if args.push:
    subprocess.run(['git', 'add', '-A'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    subprocess.run(['git', 'commit', '-m', '🤖 {} 🤖'.format(random.choice(messages))], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    subprocess.run(['git', 'push'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

if args.serve:
    cmd = "cd {}; python -m http.server 8000 --bind 127.0.0.1 ".format(website.public_dir)
    print(cmd)
    p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    while True:
        out = p.stderr.read(1)
        """if out == '' and p.poll() != None:
            break
        if out != '':
            sys.stdout.write(out)
            sys.stdout.flush()"""