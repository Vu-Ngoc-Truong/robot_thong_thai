#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import sys
import speech_recognition as sr
import time
import audioop
import playsound

def listen_audio(language='vi'):
    c = sr.Recognizer() # Khởi tạo biến nhận dạng giọng nói
    c.energy_threshold = 600  # Ngưỡng năng lượng để xác định có lấy âm hay không.
    c.pause_threshold = 1 # Thời gian xác nhận đã dừng nói để kết thúc nghe.
    c.dynamic_energy_threshold = False  # Tự động xác định ngưỡng năng lượng
    try:
        with sr.Microphone() as source: # Lấy nguồn nói từ Microphone

            #c.pause_threshold = 1 # Dừng 2s trước khi nhận lệnh mới
            c.adjust_for_ambient_noise(source, duration= 1.0)

            print("energy_threshold: ", c.energy_threshold)
            buffer = source.stream.read(source.CHUNK)
            energy = audioop.rms(buffer, source.SAMPLE_WIDTH)  # energy of the audio signal
            print("energy: ", energy)
            seconds_per_buffer = (source.CHUNK + 0.0) / source.SAMPLE_RATE
            damping = c.dynamic_energy_adjustment_damping ** seconds_per_buffer  # account for different chunk sizes and rates
            print("damping: ", damping )
            playsound.playsound('/home/pi/code_ws/robot_thong_thai/logon.mp3', True)
            print('Listening...')
            audio = c.listen(source) # Biến audio là giá trị dạng chuỗi sau khi máy nghe và nhận dạng từ nguồn vào

        print("Recognizing")
        # nhan dang tieng viet thi dung 'vi'
        query = c.recognize_google(audio, language=language)

        # print('3')
        print(query)

        return query # Tra ve text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
        return 'None'
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return 'None'
    except KeyboardInterrupt:
        print ('Keyboard Interrupted')
        return 'None'


def giao_tiep_voi_khach():

    while(True):

        query = listen_audio().lower()
        time.sleep(0.1)
        if KeyboardInterrupt:
            break

if __name__ == '__main__':

    giao_tiep_voi_khach()
