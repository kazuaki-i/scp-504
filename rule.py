import re
import urllib.parse
from bs4 import BeautifulSoup
import urllib
from difflib import SequenceMatcher
import math
from collections import Counter

try:
    from .cotoha import *
except:
    from cotoha import *

rw = re.compile('[!-/:-@\\[-`{-~.。？！（）「」＃％＠『』【】＝＋・…〜～]')

class Google:
    def __init__(self):
        self.GOOGLE_SEARCH_URL = 'https://www.google.co.jp/search'
        self.session = requests.session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:73.0) Gecko/20100101 Firefox/73.0'
        })

    def search_cnt(self, keyword):
        query = 'https://www.google.co.jp/search?q={}'.format(urllib.parse.quote(keyword))
        soup = BeautifulSoup(self.session.get(query).text, 'lxml')
        div = soup.find('div', id='result-stats')

        if div:
            count = div.text.split('件')[0].replace('約', '').replace(',', '').strip()
            if count.isdigit():
                return int(count)
        return -1


class scp504:
    cotoha = COTOHA()
    google = Google()

    def __init__(self, sentence, alpha=1.):
        self.sentence = sentence
        self.norm_sentence = rw.sub('', sentence)

        self.parsed_sentence = self.cotoha.parse(self.norm_sentence)

        self.kanas = [m.get('kana', '') for c in self.parsed_sentence for m in c.get('tokens',[])]
        self.forms = [m.get('form', '') for c in self.parsed_sentence for m in c.get('tokens',[])]

        self.x_form = ''
        self.y_form = ''
        self.x_kana = ''
        self.y_kana = ''

        self.token_ratio = self.dajaratio()
        self.similairty_ratio = -1
        self.google_search_count = 0

        self.alpha = alpha

        self.speed = self.speed_check()

    def single_character_occupancy(self):
        return Counter(self.norm_sentence).most_common(1)[0][-1] / len(''.join(self.forms))

    def tokens_occupancy(self, x_kana, y_kana):
        x_len, y_lex = len(x_kana), len(y_kana)
        total_len = len(''.join(self.kanas))

        return (x_len + y_lex) / total_len

    def dajaratio(self):
        START, END = 0, 3
        max_ratio = -1
        length = len(self.kanas)
        for s, e in [(i, h)for i in range(0, length) for h in range(START, END)]:
            if not s+e < length-1:
                continue
            x_kana = ''.join(self.kanas[s:s+e+1])
            x_form = ''.join(self.forms[s:s+e+1])
            if len(x_kana) < 2:
                continue
            for t, f in [(j, k) for j in range(s+e+1, length) for k in range(START, END)]:
                if not t+f < length:
                    continue
                y_kana = ''.join(self.kanas[t:t+f+1])
                y_form = ''.join(self.forms[t:t+f+1])
                if len(y_kana) < 2:
                    continue
                tr = SequenceMatcher(None, x_kana, y_kana).ratio()
                if tr > max_ratio:
                    max_ratio = tr
                    self.x_form, self.y_form = x_form, y_form
                    self.x_kana, self.y_kana = x_kana, y_kana

        return max_ratio

    def tokens_similarity(self, x_form, y_form):
        return self.cotoha.similarity(x_form, y_form)

    def speed_check(self):
        if self.token_ratio < 0.5:
            return -1

        if 0.5 < self.single_character_occupancy():
            return -2

        self.similairty_ratio = self.tokens_similarity(self.x_form, self.y_form)
        if self.similairty_ratio > 0.9:
            return -3

        self.google_search_count = self.google.search_cnt(' '.join(self.forms))
        unrelated_char_ratio = 1. - self.tokens_occupancy(self.x_kana, self.y_kana)
        if self.google_search_count > 10:
            speed = (math.log10(self.google_search_count) + len(self.forms) * self.alpha) * unrelated_char_ratio
        else:
            speed = len(self.forms) * self.alpha * unrelated_char_ratio


        return speed


if __name__ == '__main__':
    l = []
    l.append('アルミ缶の上にあるみかん')
    l.append('布団が吹っ飛んだ')
    l.append('アイスはあーいいっすねぇ')
    l.append('ピクルスがぴっくるするほどおいしい')
    l.append('モーターが動かなくなってもうた')
    l.append('ナシは無しな')
    l.append('ナシは漢字でナシと書く')
    l.append('あああああああああああああああ')
    l.append('すもももももももものうち')

    for sentence in l:
        tomato = scp504(sentence)
        print('{}\t🍅{} ({})'.format(sentence, ''.join(['=']*int(tomato.speed)), tomato.speed))
