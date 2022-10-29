from pydub import AudioSegment
import glob
import os

def merge():
    file_list = sorted(glob.glob("../output/public/gijiroku/audio/output?.mp3"))
    
    sound_list = []
    for mp3_file in file_list:
        # 音声ファイルの読み込み
        print(mp3_file)
        sound = AudioSegment.from_file(mp3_file, "mp3")
        sound_list.append(sound)
        #os.remove(mp3_file)

    merged_sound = sound_list[0]
    for sound in sound_list:
        if sound == merged_sound:
            continue
        # 連結
        merged_sound = merged_sound + sound

    # 保存
    merged_sound.export("../output/public/gijiroku/audio/output.mp3", format="mp3")

merge()
