import pyaudio

pa = pyaudio.PyAudio()
for i in range(pa.get_device_count()):
    name = pa.get_device_info_by_index(i)['name']
    print(pa.get_device_info_by_index(i))
    if name == 'teams audio':
        index = pa.get_device_info_by_index(i)['index']
        break
print(index)
