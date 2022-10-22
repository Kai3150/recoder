import ffmpeg
import os
import glob

def convert_mp(input, output):
    # 入力
    stream = ffmpeg.input(input)
    # 出力
    stream = ffmpeg.output(stream, output)
    # 実行
    ffmpeg.run(stream)


def convert():
    file_list = glob.glob("../output/public/gijiroku/audio/output?.wav")
    for wav_file in file_list:
        mp3_file = wav_file.replace('wav', 'mp3')
        convert_mp(wav_file, mp3_file)
        os.remove(wav_file)
