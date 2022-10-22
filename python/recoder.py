import re

from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

import pandas as pd
import datetime

# scikit-learnのTF-IDFライブラリをインポート
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import CountVectorizer

import MeCab

import numpy as np

from sklearn.metrics.pairwise import cosine_similarity

import pkg_resources, imp
import spacy
from spacy import displacy

import urllib.request
import urllib.parse
import json
import requests

import gensim

from difflib import SequenceMatcher

from ginza import *
import spacy_transformers
import time

from urllib.request import Request, urlopen
from urllib.parse import urlencode
from urllib.error import URLError, HTTPError

import pickle
import os


def read_clova_txt(clova_txt_path):
    text_dict = {}
    speaker = ""
    speaker_counted = "" #辞書のキー
    speak_counter_dict = {}

    with open(clova_txt_path) as f:
     #ヘッダーを消して参加者 1まで読み込む
        while True:
            last_point = f.tell()
            line = f.readline()
            if re.search(r'^参加者', line):
                f.seek(last_point)
                break

        for line in f:
            line = line.rstrip()  # 読み込んだ行の末尾には改行文字があるので削除
            if re.search(r'^参加者', line):
                if speaker != line:  #話者が変わるとき
                    speaker = line   #話者を更新

                    #if speaker_counted not in text_dict.keys():
                    if speaker not in speak_counter_dict.keys(): #初めて喋る人
                        speak_counter_dict[speaker] = 0
                        speaker_counted = speaker + " " + str(speak_counter_dict[speaker])
                        text_dict[speaker_counted] = ""  # 喋る内容の準備

                    else: #前にも話していた時
                        speak_counter_dict[speaker] = speak_counter_dict[speaker] + 1 #会話数をプラス１
                        speaker_counted = speaker + " " + str(speak_counter_dict[speaker])
                        text_dict[speaker_counted] = ""
            else:
                text_dict[speaker_counted] += line
    return text_dict

def read_sloos_csv(sloos_csv_path):

    df = pd.read_csv(sloos_csv_path)

    text_dict = {}
    speaker = ""
    speaker_counted = "" #辞書のキー
    speak_counter_dict = {}


    for row in df.iterrows():

        if speaker != row[1]['speaker']:  #話者が変わるとき
            speaker = row[1]['speaker']   #話者を更新

            #if speaker_counted not in text_dict.keys():
            if speaker not in speak_counter_dict.keys(): #初めて喋る人
                speak_counter_dict[speaker] = 0
                speaker_counted = str(speaker) + str(speak_counter_dict[speaker])
                text_dict[speaker_counted] = ""  # 喋る内容の準備

            else: #前にも話していた時
                speak_counter_dict[speaker] = speak_counter_dict[speaker] + 1 #会話数をプラス１
                speaker_counted = str(speaker) + str(speak_counter_dict[speaker])
                text_dict[speaker_counted] = ""

        text_dict[speaker_counted] += row[1]['message'] + '。'

    return text_dict

def summarize(text: str, count=10) -> str:
    LANGUAGE = "japanese"  # 言語指定
    SENTENCES_COUNT = count  # 要約文数


    # parser = PlaintextParser.from_file("document.txt", Tokenizer(LANGUAGE))
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)

    sentences = ""
    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        sentences = sentences + sentence.__str__()

    return sentences

def preprocessor(text):
    text = re.sub(' ', '', text) ##空白削除

    text = text.replace('です', 'です。').replace('ます','ます。').replace('でした','でした。').replace('ません','ません。')##ますの後には必ず「。」
    text = re.sub(r'[、。](ただ|でも|いや|だが|しかし|対して|一方で|あるいは|けれども|けども|けど|が)[、。]', '#BUT', text) ##逆説->#BUT
    text = re.sub(r'[、。](たとえば|例えば)[、。]', '#EXAMPLE', text) ##具体例->#EXAMPLE
    text = re.sub(r'[、。](だって)[、。]', '#BECAUSE_REASON', text) ##理由1->#BECAUSE_REASON
    text = re.sub(r'[、。](だから|なので|従って)[、。]', '#REASON_BECAUSE', text) ##理由2->#REASON_BECAUSE
    text = re.sub(r'[、。](つまり|まとめると|ですから)[、。]', '#INANUT', text) ##まとめor重要->#INANUT
    text = re.sub(r'[、。](加えて|それと|そして|それから)[、。]', '#AND', text) ##加えて->#AND


    text = re.sub(r'[、].{0,5}[、。]', '、', text) ##削除
    text = re.sub(r'[。].{0,5}[、。]', '。', text) ##削除
    text = re.sub(r'(えー)', '', text) ##削除

    text = re.sub(r'(え[、。])', '、', text) ##誤字訂正


    text = re.sub(r'ます、', 'ます。', text) ##ますの後には必ず「。」
    #re.findall(r'[、。].{6}[、。]', text)

    #print(text)
    return text

def write1(file, str1):
    with open(file, 'w', encoding='utf-8') as f1:
        f1.write(str1)


def convert(text):
    # ノイズ削除
    text = re.sub(r'《.+?》', '', text)
    text = re.sub(r'［＃.+?］', '', text)
    text = re.sub(r'｜', '', text)
    text = re.sub(r'\r\n', '', text)
    text = re.sub(r'\u3000', '', text)
    text = re.sub(r'「', '', text)
    text = re.sub(r'」', '', text)
    text = re.sub(r'、', '', text)
    text = re.sub(r'。', '', text)

    return text

# Taggerオブジェクトを生成
tokenizer = MeCab.Tagger("-Ochasen")
tokenizer.parse("")

def extract(text):
    words = []

    # 単語の特徴リストを生成
    node = tokenizer.parseToNode(text)

    while node:
        # 品詞情報(node.feature)が名詞ならば
        if node.feature.split(",")[0] == u"名詞":
            if re.fullmatch(r'[\u3040-\u309F]+', node.surface)== None: #ひらがなだけはパス
                # 単語(node.surface)をwordsに追加
                words.append(node.surface)
        node = node.next

    # 半角スペース区切りで文字列を結合
    text_result = ' '.join(words)
    return text_result

def severe_extract(text):
    words = []

    # 単語の特徴リストを生成
    node = tokenizer.parseToNode(text)

    while node:
        # 品詞情報(node.feature)が名詞ならば
        if node.feature.split(",")[0] == u"名詞":
            #ひらがな、2文字以下のカタカナ　を　パス
            if (re.fullmatch(r'[\u3040-\u309F]+|[0-9]+|.', node.surface) == None)\
            and (re.fullmatch(r'[ァ-ヶ]{0,2}', node.surface) == None):
                # 単語(node.surface)をwordsに追加
                words.append(node.surface)
        node = node.next

    return words

#TfidVectorizer(全体的で見た時の特徴語抽出)  どうでもいい言葉が多い感じ. 両方使ってもいいかもしれない
def key_words(p_text_dict: dict) -> dict:
    docs = []
    for key, value in p_text_dict.items():
        text = convert(value)
        text = extract(text)
        docs.append(text)

    # モデルを生成
    vectorizer = TfidfVectorizer(smooth_idf=False)
    X = vectorizer.fit_transform(docs)

    # データフレームに表現
    values = X.toarray()
    feature_names = vectorizer.get_feature_names()
    df = pd.DataFrame(values, columns = feature_names, index=p_text_dict.keys())

    top10_dict = {}
    for key in p_text_dict.keys():
        top10_dict[key] = df.T[key].sort_values(ascending=False).head(10).keys()
    return top10_dict


#文章を文脈で分割

#わかち書き関数
def wakachi(text):
    from janome.tokenizer import Tokenizer
    t = Tokenizer()
    tokens = t.tokenize(text)
    docs=[]
    for token in tokens:
        docs.append(token.surface)
    return docs

#文書ベクトル化関数
def vecs_array(documents):
    from sklearn.feature_extraction.text import TfidfVectorizer

    docs = np.array(documents)
    vectorizer = TfidfVectorizer(analyzer=wakachi,binary=True,use_idf=False)
    vecs = vectorizer.fit_transform(docs)
    return vecs.toarray()

def divide_text(text: str) -> list:
    #三文ごとに分割
    sample_slice = re.findall("[^。]+。?", text)

    i = 0
    new_slice = []
    temp_slice = []
    for sentence in sample_slice:
        temp_slice.append(sentence)

        if i % 3 == 2:
            new_slice.append(''.join(temp_slice))
            temp_slice = []
        i += 1

    docs = new_slice

    #類似度行列作成
    cs_array = np.round(cosine_similarity(vecs_array(docs), vecs_array(docs)),3)

    xy=np.where(cs_array < 0.3)

    x = xy[0][abs(xy[0] - xy[1]) == 1]
    y = xy[1][abs(xy[0] - xy[1]) == 1]

    diffs = pd.DataFrame([x, y])
    t = diffs.T
    t = t[t[0] > t[1]]

    #<h3>{key_words}</h3>
    #<p>{content}</p>

    #content = """ <h4>{speaker}</h4>
    #               <p>{naiyou}</p>           """

    #context_dict { key_words: contents}

    for _, item in t.iterrows():
        new_slice[item[0]] += '##DIV##'

    new_text = ''.join(new_slice)
    divided_list = new_text.split('##DIV##')

    #add_key_words(new_slice)
    #return context_dict
    return divided_list
def divide_text2(text: str) -> list:
    slice_list = re.findall("([^。]+。)", text)
    while len(slice_list) > 30:
        max_ratio = 0
        divide_list = []
        sames = []

        for i in range(len(slice_list)-1):

            str1 = slice_list[i]
            str2 = slice_list[i+1]


            s = SequenceMatcher(None, str1, str2)

            if s.ratio() > max_ratio:
                max_ratio = s.ratio()
                max_i = i
                divide_list = [str1, str2]

        slice_list[max_i] = slice_list[max_i] + slice_list.pop(max_i + 1)
    return slice_list


def add_key_words(new_slice):
    context_list = []
    key_word = 0
    contents = ''
    context_dict = {}


    for sentence3 in new_slice:
        if '##DIV##' in sentence3:
            sentence3 = sentence3.replace('##DIV##', '')
            contents = ''
            contents += sentence3

            ##キーワードの抽出するならここ
            key_word = key_word + 1

            #context_list.append(contents)
            context_dict[key_word] = contents
        else:
            contents += sentence3
    return context_dict


imp.reload(pkg_resources)
# モデルのロード
nlp = spacy.load("ja_core_news_md")
#nlp = spacy.load('ja_ginza')

def get_key_word2(input_sentence:str) -> str:
    # 解析対象のテキストa
    input_text = input_sentence

    input_text = re.sub(r'[#A-Z_]+', '', input_text)
    # モデルに解析対象のテキストを渡す
    doc = nlp(input_text)
    # 固有表現を抽出
    #for ent in doc.ents:
        #print(ent.text, ent.label_, ent.start_char, ent.end_char)

    # out -->
    ## 2018年 DATE 0 5
    ## 8月 DATE 6 8
    ## フランス GPE 12 16
    ## ルーヴル美術館 ORG 24 31
    key_words = []
    #for tok in doc:
     #モデルが ja_ginza の場合
        #if tok.pos_ == 'PROPN':
            #key_words.append(tok.text)
    for ent in doc.ents:
        #モデルが ja_core_news_md の場合
        if ent.label_ in ['ORG', 'PERSON', 'PRODUCT', 'GPE']:
            key_words.append(ent.text)
    key_words = list(set(key_words))#重複要素を削除
    key_str = '、'.join(key_words)
    return key_str


def clean_text_api(text):
    API="https://api.a3rt.recruit.co.jp/proofreading/v2/typo"
    KEY="DZZps9cHfJGAxGlvhqkYh0xHlIk8igKu"

    cleaned_text = ''
    text_list = re.findall("[^。]+。?", text)
    for sentence in text_list:
        quoted_text = sentence
        values = {
        'apikey': KEY,
        'sentence':quoted_text,
        'sensitivity':"low",
        }

        # パラメータをURLエンコードする
        params = urllib.parse.urlencode(values)
        # リクエスト用のURLを生成
        url = API + "?" + params

        #リクエストを投げて結果を取得
        r = requests.get(url)
        #辞書型に変換
        data = json.loads(r.text)

        if 'alerts' in data:

            for alert in data['alerts']:
                miss_word = alert['word']
                suggested_word = alert['suggestions'][0]
                quoted_text = quoted_text.replace(miss_word, suggested_word)
        cleaned_text = cleaned_text + quoted_text
    return cleaned_text
def text_clenging(text:str) -> str:

    text = re.sub(' ', '、', text) ##空白削除

    text = text.replace('です', 'です。').replace('ます','ます。').replace('でした','でした。').replace('ません','ません。').replace('さい','さい。')##ますの後には必ず「。」
    text = text.replace('っていうこと', 'こと').replace('っていう', 'という').replace('ていう', 'という').replace('かなと', 'かと')##ますの後には必ず「。」

    text = re.sub(r'(えー|えーと|えっと|そうですね|まあ|じゃあ|なんか|ちょっと|あの|ということで|っていうの|んじゃないか|一応|とりあえず)', '', text) ##削除
    text = re.sub(r'ま([^\u3040-\u309F])', r'\1', text) ##削除
    text = re.sub(r'という([、。])', r'\1', text) ##削除
    text = re.sub(r'(.)(.)(.)\1\2\3', r'\1\2\3', text)#繰り返し文字
    text = re.sub(r'([\u3400-\u9FFF\uF900-\uFAFF]|[\uD840-\uD87F][\uDC00-\uDFFF])([\u3400-\u9FFF\uF900-\uFAFF]|[\uD840-\uD87F][\uDC00-\uDFFF])\1\2', r'\1\2', text)

    while re.search(r'([ねえま][、。]|[、。].{0,2}[、。])', text):
        text = re.sub(r'([ねえま]、)', '、', text) ##誤字 語感　訂正
        text = re.sub(r'([ねえま]。)', '。', text) ##誤字　語感　訂正

        text = re.sub(r'[、].{0,2}[、。]', '、', text) ##削除
        text = re.sub(r'[。].{0,2}[、。]', '。', text) ##削除
        text = re.sub(r'^.{0,2}[、。]', '', text) ##削除


    return text

def keyword_clenging(key_str: str)->str:
    key_str = re.sub(r'(宮崎ゼミ|宮崎|ゼミ)', '', key_str)
    key_str = re.sub(r'(、、)', '、', key_str)
    key_str = re.sub(r'^、', '', key_str)
    return key_str

#s_text_dict -> よく喋る人を3つ残した同じdict
def delete_aizuti(s_text_dict: dict) -> dict:
    ##一番喋っている人を特定
    max_n = 0
    for key in s_text_dict.keys():
        if max_n < int(key.split(' ')[2]): #'参加者 ID N' をスプリット
            max_n = int(key.split(' ')[2])
            speaker_index = key.split()[1]

    fasili_dict = {}
    #ファシリテーターの相槌を消す。 上位3つだけ残す
    for key, value in s_text_dict.items():
        if key.split(' ')[1] == speaker_index:
            #ファシリテーターを特定
            fasili_dict[key] = value

    top3_key = []
    while len(top3_key) < 3:
        max_value = 0

        for key, value in fasili_dict.items():
            if len(value) > max_value:
                max_value = len(value)
                max_key = key
        fasili_dict.pop(max_key)
        top3_key.append(max_key)
    for delete_key in list(fasili_dict.keys()):
        s_text_dict.pop(delete_key)

    return s_text_dict

#話者が同じやつはくっつける
def text_merge(p_text_dict):
    speaker = ""
    speaker_counted = "" #辞書のキー
    speak_counter_dict = {}
    s_text_dict = {}
    for key, value in p_text_dict.items():
        if speaker != key.split(' ')[1]:  #話者が変わるとき
            speaker = key.split(' ')[1]   #話者を更新

            #if speaker_counted not in text_dict.keys():
            if speaker not in speak_counter_dict.keys(): #初めて喋る人
                speak_counter_dict[speaker] = 0
                speaker_counted = speaker + " " + str(speak_counter_dict[speaker])
                s_text_dict[speaker_counted] = ""  # 喋る内容の準備

            else: #前にも話していた時
                speak_counter_dict[speaker] = speak_counter_dict[speaker] + 1 #会話数をプラス１
                speaker_counted = speaker + " " + str(speak_counter_dict[speaker])
                s_text_dict[speaker_counted] = ""

        s_text_dict[speaker_counted] += value
    return s_text_dict

def main():
    text_dict = read_clova_txt('text/output.txt')
    # dictional = read_sloos_csv('text/sloos_sample.csv')

    # #グーグルの文字起こしデータ
    # with open("text/speech_to_text.pkl", "rb") as f:
    #     response1 = pickle.load(f)
    # result = response1.results[-1]
    # words_info = result.alternatives[0].words


    ###########################        文脈による分割      #####################  ->  context_dict { key_word : paragraph}
    all_text = ''
    for key, value in text_dict.items():
        all_text += value

    #全てのテキストを綺麗にする
    p_all_text = text_clenging(all_text)
    #テキストを分割
    divide_list = divide_text2(p_all_text)
    #分割したテキストを要約
    new_list = []
    for text in divide_list:
        new_list.append(summarize(text))
    divide_list = new_list
    #短すぎる文章を削除
    for text in divide_list:
        if len(re.findall('。', text)) == 1:
            divide_list.remove(text)
    #キーワードをくっつける
    context_dict = {}
    for sentence in divide_list:
        key_word = get_key_word2(sentence)
        #キーワードを整理
        p_key_word = keyword_clenging(key_word)
        context_dict[p_key_word] = sentence


    ###############################    発話者による分割      ##########################    ->  {参加者 : {キーワード : 要約内容}}

    #テキストクリーニングと相槌削除
    p_text_dict = {}
    for key, value in text_dict.items():
        value = text_clenging(value)
        #value = preprocessor(value)
        #value = summarize(value, 1)

        if len(value) > 100:
            p_text_dict[key] = value

    p_text_dict = delete_aizuti(p_text_dict)
    s_text_dict = text_merge(p_text_dict)

    #{参加者 1 0: キーワード}
    #{参加者 : {キーワード : 要約内容}}
    #key_text_dict = key_words(p_text_dict)


    #Wikipediaリンク用の単語を抽出
    words = []
    for key, value in s_text_dict.items():
        words.extend(severe_extract(value))
    #重複を削除
    words = list(set(words))



    #wikipediaに存在するか確認
    checked_words = []
    for word in words:
        request_url = 'https://ja.wikipedia.org/api/rest_v1/page/summary/' + urllib.parse.quote(word)
        req = Request(request_url)
        try:
            with urlopen(req) as res:
                res_json = res.read()
        except HTTPError as e:
            continue
        except URLError as e:
            continue
        else:
            wiki = json.loads(res_json.decode('utf-8'))
            if (wiki['type'] == 'disambiguation') or (len(wiki['extract']) < 7):
                continue

            checked_words.append(word)
        time.sleep(0.01)

    #リンクが貼れるように置換するための辞書を作成
    checked_dict = {}
    for word in checked_words:
        checked_dict[word] = "<span class=\"wmf-wp-with-preview\" data-wp-title=\""+ word + "\" data-wikipedia-preview>" + word + "</span>"


    key_text_dict = {}
    ss_text_dict = {}
    for key, value in s_text_dict.items():
        count = len(value.split('。'))

        value = summarize(value, round(count/5))  # 20%のこし
        if value == '':
            continue

        #長すぎる文章はClick to see more
        confirm_value = ""
        if len(value) > 500:
            count = len(value.split('。'))
            confirm_value = summarize(value, round(count/5))  # 20%のこし

        key_word = get_key_word2(value)
        p_key_word = keyword_clenging(key_word)

        #辞書をもとにhtml用に書き換え
        for word, read in checked_dict.items():
            value = value.replace(word, read)
            confirm_value = confirm_value.replace(word, read)

        #2回replaceされる単語を治す
        value = re.sub(r'<span class="wmf-wp-with-preview" data-wp-title="<span class="wmf-wp-with-preview" data-wp-title="([^"]+)" data-wikipedia-preview>[^>]+>([^"]+)[^>]+>[^>]+>[^<]+[^>]+.',
                    r'<span class="wmf-wp-with-preview" data-wp-title="\1\2" data-wikipedia-preview>\1', value)
        value = re.sub(r'</span>" data-wikipedia-preview>', '', value)

        confirm_value = re.sub(r'<span class="wmf-wp-with-preview" data-wp-title="<span class="wmf-wp-with-preview" data-wp-title="([^"]+)" data-wikipedia-preview>[^>]+>([^"]+)[^>]+>[^>]+>[^<]+[^>]+.',
                            r'<span class="wmf-wp-with-preview" data-wp-title="\1\2" data-wikipedia-preview>\1', confirm_value)
        confirm_value = re.sub(r'</span>" data-wikipedia-preview>', '', confirm_value)
        if confirm_value == '':
            div = '''
            <div class="confirm_value">
                <p>{value}</p>
            </div>'''.format(value=value)
        else:
            div = '''
            <div class="confirm_value" onclick="obj=document.getElementById('{key}').style; obj.display=(obj.display=='none')?'block':'none';">
                <p>{confirm_value}</p>
                <p class='see'>クリックして原文を表示</p>
            </div>
            <div class="more" id="{key}" style="display:none;clear:both;">
                <p>{value}</p>
            </div>'''.format(key=key, confirm_value=confirm_value, value=value)

        ss_text_dict[key] = (p_key_word, div)

    body = ""
    for key, value in ss_text_dict.items():  # 発話者による分割
        body = body + '''
        <h2>{key}</h2>
        <h3>{keyword}</h3>{div}'''.format(key=key, keyword=value[0], div=value[1])



    dt_now = datetime.datetime.now()
    date=dt_now.strftime('%Y年%m月%d日') + "の議事録"

    str1 = '''<!DOCTYPE html>
    <html lang="ja">
    <head>
        <meta charset="UTF-8">
        <title>{title}</title>
        <link rel="stylesheet" href="static/style.css">
    </head>
        <body>
            <h1>{date}</h1>
            <h1>画像アップロード</h1>
            <form action="/upload" method="post" enctype="multipart/form-data" class="form-img">
                <div id="drop-zone" style="border: 1px solid; padding: 30px; border-color: white;">
                    <p>ファイルをドラッグ＆ドロップもしくは</p>
                    <input type="file" name="file" id="file-input">
                </div>
                <h2>プレビュー</h2>
                <div id="preview"></div>
                <h2>アップロードした画像</h2>
                <div id="uploaded"></div>
                <input type="submit" style="margin-top: 50px">
            </form>
            {body}
            <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
            <script src="static/wikipedia-preview.development.js"></script>
            <script src="static/file.js"></script>
            <script type="text/javascript">wikipediaPreview.init({{lang: 'ja'}});</script>
        </body>
    </html>'''.format(title='議事録', date=date, body=body)

    write1(os.path.abspath("../output/public/gijiroku")+'/gijiroku'+ datetime.datetime.now().strftime('(%Y.%m.%d)') + '.html', str1)

if __name__ == "__main__":
    main()
