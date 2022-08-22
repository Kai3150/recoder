import re
text_dict = {}
speaker = ""
speaker_counted = "" #辞書のキー
speak_counter_dict = {}


with open('sample.txt') as f:

    for line in f:
        line = line.rstrip()  # 読み込んだ行の末尾には改行文字があるので削除
        if re.search(r'^参加者', line):
            if speaker != line:  #話者が変わるとき
                speaker = line   #話者を更新

                #if speaker_counted not in text_dict.keys():
                if speaker not in speak_counter_dict.keys(): #初めて喋る人
                    speak_counter_dict[speaker] = 0
                    speaker_counted = speaker + str(speak_counter_dict[speaker])
                    text_dict[speaker_counted] = ""  # 喋る内容の準備

                else: #前にも話していた時
                    speak_counter_dict[speaker] = speak_counter_dict[speaker] + 1 #会話数をプラス１
                    speaker_counted = speaker + str(speak_counter_dict[speaker])
                    text_dict[speaker_counted] = ""

        else:
            text_dict[speaker_counted] += line
print(text_dict)


