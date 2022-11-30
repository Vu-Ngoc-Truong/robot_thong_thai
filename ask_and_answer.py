#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
from gtts import gTTS
import playsound
import audioop
import speech_recognition as sr
from text_to_speech import text_to_speech
from speech_to_text import listen_audio
from database_mongodb import MongodbStorage
import random
from PIL import Image, ImageDraw


if __name__ == "__main__":

    mydb = MongodbStorage("mongodb://coffee:coffee@localhost:27017")
    # Linh vuc van hoc
    mycol = mydb.vanhocCollection
    # Linh vuc lich su
    mycol = mydb.lichsuCollection
    ask_num = 1
    ask_id_list = []
    ask_id_min = 1
    ask_id_max = 10
    num_of_ask = 3
    num_of_correct = 0
    language = 'vi'
    # img_path = '/home/pi/code_ws/toan_01.jpg'
    # pil_image = Image.open(img_path).convert("RGB")
    # draw = ImageDraw.Draw(pil_image)
    # # Display the resulting image
    # pil_image.show()
    # text_to_speech('Câu hỏi số  1: Mời bạn đọc câu hỏi bằng hình ảnh trên màn hình.')
    # time.sleep(1)
    # text_to_speech('Thời gian trả lời bắt đầu.')
    # try:
    #     user_talk = listen_audio(language).lower()
    #     _answer1 = 'phương án c'
    #     _answer2 = 'đáp án c'
    #     # _answer1 =  str(x['Đáp án']).lower()
    #     # _answer2 =  str(x['Đáp án']).lower()
    #     if  (_answer1 in user_talk) or ( _answer2 in user_talk) :
    #         num_of_correct += 1
    #         print("Chúc mừng bạn đã trả lời đúng!")
    #         text_to_speech("Chúc mừng bạn đã trả lời đúng!")
    #         text_to_speech('Đáp án đúng là: c')
    #     else:
    #         print("Xin chia buồn vì bạn đã trả lời sai!")
    #         text_to_speech("Xin chia buồn vì bạn đã trả lời sai!")
    #         text_to_speech('Đáp án đúng là: c')
    # except:
    #     print("Lỗi khi nghe câu trả lời")

    # Print collection before update
    for i in  range(num_of_ask):
        text_to_speech('Câu hỏi số {}:'.format(i+1))
        ask_idx = random.randint(ask_id_min, ask_id_max)
        # lay cau hoi khac neu cau hoi da nam trong danh sach da hoi
        count = 0
        get_ask_result = True
        while ask_idx in ask_id_list:
            ask_idx = random.randint(ask_id_min, ask_id_max)
            count +=1
            # Neu so cau hoi nhieu hon trong danh sach
            if len(ask_id_list) > (ask_id_max - ask_id_min):
                print("Số câu hỏi cần lấy nhiều hơn số câu hỏi trong thư viện.")
                get_ask_result = False
                break
            # lay ngau nhien toi da 100 lan
            if count > 100:
                print("Lấy ngẫu nhiên quá số lần quy định.")
                get_ask_result = False
                break
        # Nếu lấy câu hỏi thành công
        if get_ask_result:
            ask_id_list.append(ask_idx)
            # print("ask idx : ", ask_idx)
        else:
            print("Lỗi khi lấy câu hỏi từ thư viện!")
            break
        try:
            x = mycol.find_one({"STT": str(ask_idx)})
            print('Câu hỏi: ' + x['Câu hỏi'])
            print("A. " + x['Phương án A'])
            print("B. " + x['Phương án B'])
            print("C. " + x['Phương án C'])
            print("D. " + x['Phương án D'])
            text_to_speech(x['Câu hỏi'])
            text_to_speech('Phương án A .' + x['Phương án A'])
            text_to_speech('Phương án B .' + x['Phương án B'])
            text_to_speech('Phương án C .' + x['Phương án C'])
            text_to_speech('Phương án D .' + x['Phương án D'])
        except:
            print("Lỗi khi tìm câu hỏi trong database!")
            break

        # Đợi câu trả lời
        time.sleep(1)
        text_to_speech('Thời gian trả lời bắt đầu.')

        try:
            user_talk = listen_audio(language).lower()
            _answer1 = 'phương án ' +  str(x['Đáp án']).lower()
            _answer2 = 'đáp án ' +  str(x['Đáp án']).lower()
            # _answer1 =  str(x['Đáp án']).lower()
            # _answer2 =  str(x['Đáp án']).lower()
            if  (_answer1 in user_talk) or ( _answer2 in user_talk) :
                num_of_correct += 1
                print("Chúc mừng bạn đã trả lời đúng!")
                text_to_speech("Chúc mừng bạn đã trả lời đúng!")
                text_to_speech('Đáp án đúng là: ' + x['Đáp án'] + "." +  x['Phương án '+ x['Đáp án']])
            else:
                print("Xin chia buồn vì bạn đã trả lời sai!")
                text_to_speech("Xin chia buồn vì bạn đã trả lời sai!")
                text_to_speech('Đáp án đúng là: ' + x['Đáp án'] + "." +  x['Phương án '+ x['Đáp án']])
        except:
            print("Lỗi khi nghe câu trả lời")
            break

    # Tuyên bố kết quả
    text_to_speech("Chúc mừng bạn đã kết thúc bài kiểm tra. Bạn đã trả lời đúng {} trên {} câu hỏi".format(num_of_correct, num_of_ask ))