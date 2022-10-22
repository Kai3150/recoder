import pyaudio
import numpy as np
import wave
import time
import os
import merge
import convert


class AudioLight():
    def __init__(self):
        # オーディオに関する設定
        self.p = pyaudio.PyAudio()

        for i in range(self.p.get_device_count()):
            name = self.p.get_device_info_by_index(i)['name']

            if name == 'Soundflower (2ch)':
                # 録音デバイスのインデックス番号（デフォルト1）
                index = self.p.get_device_info_by_index(i)['index']
                break

        self.channels = 1 # ステレオの場合は2
        #self.rate = 44100 #55MB/２時間
        #self.rate = 22050 #27.5MB/２時間
        self.rate = 11025 #15MB/２時間
        self.format = pyaudio.paInt16
        self.stream = self.p.open(
                        format=self.format,
                        channels=self.channels,
                        rate=self.rate,
                        output=True,
                        input=True,
                        input_device_index=index,
                        stream_callback=self.callback)
        self.threshold = 1000
        self.wf = None
        self.status = 0 # 0: norec, 1: rec
        self.start_at = time.time()
        self.file_count = 0
        self.stop_flag = True

    # コールバック関数
    def callback(self, in_data, frame_count, time_info, status):
        if self.wf is not None:
            self.wf.writeframes(in_data)
        amp = np.fromstring(in_data, np.int16)
        self.rec_check(amp)
        out_data = in_data
        return (out_data, pyaudio.paContinue)

    def rec_check(self, amp):
        # 停止中で大きい音がしたら、新しいファイルを作成して開始時刻を設定
        if (self.status == 0) and (amp.max() > self.threshold):
            self.status = 1
            self.open_file()
            self.start_at = time.time()
            print("Start Rec")

        # 録音中で大きい音がしたら、開始時刻を更新
        elif (self.status == 1) and (amp.max() > self.threshold):
            self.start_at = time.time()

        # 録音中で大きい音がしなくなってから10秒経ったら、ファイルを閉じる
        elif (self.status == 1) and (amp.max () <= self.threshold):
            if (time.time() - self.start_at) > 60:
                self.status = 0
                self.close_file()
                self.file_count = self.file_count + 1
                print("Rec is done.")


        #録音終了後20秒後に終了
        elif (self.status == 0):
            if (time.time() - self.start_at) > 420:
                self.stop_flag = False


    def open_file(self):
        self.wf = wave.open("audio/output" + str(self.file_count) + ".wav", "wb")
        print("start output"+str(self.file_count)+".wav")
        self.wf.setnchannels(self.channels)
        self.wf.setsampwidth(2)
        self.wf.setframerate(self.rate)

    def close_file(self):
        self.wf.close()
        self.wf = None

    def close(self):
        self.p.terminate()

if __name__ == "__main__":
    #前のファイルを削除
    dir = 'audio'
    for f in os.listdir(dir):
        os.remove(os.path.join(dir, f))


    # AudioFilterのインスタンスを作る場所
    af = AudioLight()

    # ストリーミングを始める場所
    af.stream.start_stream()

    while af.stop_flag:
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    # ストリーミングを止める場所
    af.stream.stop_stream()
    af.stream.close()
    af.close()
    print("complete recoding")

    convert.convert()
    print('convert complete')

    merge.merge()
    print('merge complete')
