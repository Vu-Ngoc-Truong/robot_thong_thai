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
import sys
import time
from ask_and_answer_ui import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.Qt import Qt
from face_recognition_knn_camera import predict
import cv2
import numpy as np
import pickle

# select camera source
use_picam2 = True

if use_picam2:
    # Use camera of raspberry #####################################################
    from picamera2 import Picamera2, Preview
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'RGB888', "size": (680, 400)}))
    picam2.start()

HOME = os.path.expanduser('~')
dir_path = os.path.dirname(os.path.realpath(__file__))

class AskAndAnswer():
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        self.ui = Ui_MainWindow()
        self.MainWindow = QtWidgets.QMainWindow()
        self.ui.setupUi(self.MainWindow)
        self.MainWindow.show()
        self.init_variable()
        sys.exit(self.app.exec_())

    def init_variable(self):

        self.mydb = MongodbStorage("mongodb://coffee:coffee@localhost:27017")
        # Linh vuc lich su
        self.mycol = self.mydb.lichsuCollection
        ask_num = 1
        self.ask_id_list = []
        self.ask_id_min = 1
        self.ask_id_max = 10
        self.num_of_ask = 3
        self.num_of_correct = 0
        self.language = 'vi'
        self.exit = False
        self.test_status = False
        self.linh_vuc = ""
        self.so_cau_hoi = ""
        self.list_so_cau_hoi = [1, 2, 5]
        self.list_mon_hoc = ["Toán học","Văn học","Tiếng Anh", "Lịch sử ","Địa lý"]
        self.list_img_path = ["Toan","Van","Anh","Su","Dia"]
        self.mon_hoc_index = 0
        self.ui.txtResult.setStyleSheet('color: red')

        self.dict_faces = {"Huy": "Huy", "Huong": "Hưởng", "Tien":"Tiến"}

        if not use_picam2:
            # Use laptop camera ####################################################
            self.camera = cv2.VideoCapture(0)

        # Load a trained KNN model (if one was passed in)
        with open(os.path.join(dir_path, "model","trained_knn_model.clf"), 'rb') as f:
            self.knn_clf = pickle.load(f)

        # Chọn môn học
        self.listCollection = [self.mydb.toanhocCollection,self.mydb.vanhocCollection,self.mydb.tienganhCollection, self.mydb.lichsuCollection,self.mydb.dialyCollection]
        self.listAskNum = [1, 3, 5]
        self.ui.cbbMonHoc.addItems(self.list_mon_hoc)
        self.ui.cbbSoCauHoi.addItems(['1', '3', '5'])
        # Xử lý sự kiện
        self.ui.btnStart.clicked.connect(self.run_test)
        self.ui.btnExit.clicked.connect(self.exit_app)
        self.ui.cbbMonHoc.currentIndexChanged.connect(self.chon_mon_hoc)
        self.ui.cbbSoCauHoi.currentIndexChanged.connect(self.chon_so_cau_hoi)

        self.chon_mon_hoc()
        self.chon_so_cau_hoi()

    def exit_app(self):
        self.exit = True
        if not self.test_status:
            print("Exit")
            self.MainWindow.destroy()
            self.app.quit()

    def face_detect(self):
        counter = 0
        image_predict = 0
        predictions = ()
        face_name =""
        find_face_ok = False
        print("start find face")

        while (counter< 100) and (not find_face_ok):
            counter += 1
            if use_picam2:
                # Use camera Pi ##############################################
                img = picam2.capture_array()
            else:
                # Use camera laptop  #######################################
                ret, img = self.camera.read()
            # print("img read")

            image_predict += 1
            # Chuyen gray
            # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            img_draw = img
            if image_predict >= 5:
                image_predict = 0
                predictions = predict(img, self.knn_clf)
                print(predictions)

                # Print results on the console
            for name, (top, right, bottom, left) in predictions:
                # print("- Found {} at ({}, {}) ".format(name, left, top))
                # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
                img_draw = cv2.rectangle(img_draw,(left,top),(right,bottom),(0,255,0),2)
                # See if the face is a match for the known face(s)
                (text_width, text_height) = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX,1,2)[0]
                cv2.rectangle(img_draw,(left,bottom),(right,bottom + text_height + 20),(255,100,0), -1)
                cv2.putText(img_draw, name, (left + 10, bottom + text_height + 10),cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,0,255), 2, cv2.LINE_AA)

                if name in self.dict_faces:
                    print("Tim thay face: ", name)
                    face_name = name
                    find_face_ok  = True

            cv2.imshow("Tìm khuôn mặt", img_draw)
            key = cv2.waitKey(1)
            if key==ord('q'):
                break
        # self.camera.release()
        cv2.destroyAllWindows()
        return face_name


    def chon_mon_hoc(self):
        print("field index: ", self.ui.cbbMonHoc.currentIndex())
        index = self.ui.cbbMonHoc.currentIndex()
        self.mon_hoc_index = index
        self.mycol= self.listCollection[index]
        self.linh_vuc = self.list_mon_hoc[index]
        print("linh vuc : ",self.linh_vuc)


    def chon_so_cau_hoi(self):
        print("num_of_ask index: ", self.ui.cbbSoCauHoi.currentIndex())
        index = self.ui.cbbSoCauHoi.currentIndex()
        self.num_of_ask = self.listAskNum[index]
        self.so_cau_hoi = self.list_so_cau_hoi[index]

    def run_test(self):
        self.test_status = True
        # Check face
        face_id = self.face_detect()
        print(face_id)
        if  not face_id == "":
            try:
                text_to_speech("Xin chào bạn {}".format(self.dict_faces[face_id]))
                print("Hello {}".format(self.dict_faces[face_id]))
            except:
                print("Lỗi khi phát âm")
                self.test_status = False
        else:
            try:
                text_to_speech("Xin lỗi chúng tôi không tìm thấy khuôn mặt hợp lệ!")
                self.test_status = False
                print("Khong thay mat hop le")
                return
            except:
                print("Lỗi khi phát âm")
                self.test_status = False

        # Print collection before update
        self.ui.txtResult.setText(str(self.num_of_correct) +"/"+  str(self.num_of_ask))
        print((str(self.num_of_correct) +"/"+  str(self.num_of_ask)))

        text_to_speech('Bạn đã chọn lĩnh vực {} với gói {} câu hỏi.'.format(self.linh_vuc, self.so_cau_hoi))
        for i in  range(self.num_of_ask):
            if self.exit :
                break
            text_to_speech('Câu hỏi số {}:'.format(i+1))
            self.ask_idx = random.randint(self.ask_id_min, self.ask_id_max)
            # lay cau hoi khac neu cau hoi da nam trong danh sach da hoi
            count = 0
            get_ask_result = True
            while self.ask_idx in self.ask_id_list:
                self.ask_idx = random.randint(self.ask_id_min, self.ask_id_max)
                count +=1
                # Neu so cau hoi nhieu hon trong danh sach
                if len(self.ask_id_list) > (self.ask_id_max - self.ask_id_min):
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
                self.ask_id_list.append(self.ask_idx)
                print("ask idx : ", self.ask_idx)
            else:
                print("Lỗi khi lấy câu hỏi từ thư viện!")
                break

            if self.linh_vuc == "Tiếng Anh":
                _language = 'en'
            else:
                _language = 'vi'
            try:
                x = self.mycol.find_one({"STT": str(self.ask_idx)})
                have_image = x["Hình ảnh"] if "Hình ảnh" in x else "Không"
                print("have image :", have_image)
                print(x)
                if have_image =="Có":

                    img_path = os.path.dirname(os.path.realpath(__file__)) + "/image/" +self.list_img_path[self.mon_hoc_index] +"/cau"+ str(self.ask_idx)+".jpg"
                    print(img_path)
                    img_resize = QtGui.QImage(img_path).scaledToWidth(630)
                    self.ui.txtImage.setPixmap(QtGui.QPixmap.fromImage(img_resize))
                    print("Hien thi anh")
                    text_to_speech('Mời bạn đọc câu hỏi bằng hình ảnh trên màn hình:')
                    time.sleep(3)

                else:

                    print('Câu hỏi: ' + x['Câu hỏi'])
                    print("A. " + x['Phương án A'])
                    print("B. " + x['Phương án B'])
                    print("C. " + x['Phương án C'])
                    print("D. " + x['Phương án D'])
                    self.ui.txtCauHoi.setText('Câu hỏi: \n  '+ x['Câu hỏi'])
                    text_to_speech(x['Câu hỏi'],_language)
                    self.ui.txtDapAnA.setText("A. " +x['Phương án A'])
                    text_to_speech('Phương án A .')
                    text_to_speech(x['Phương án A'], _language)
                    self.ui.txtDapAnB.setText("B. " +x['Phương án B'])
                    text_to_speech('Phương án B .')
                    text_to_speech(x['Phương án B'], _language)
                    self.ui.txtDapAnC.setText("C. " +x['Phương án C'])
                    text_to_speech('Phương án C .')
                    text_to_speech(x['Phương án C'], _language)
                    self.ui.txtDapAnD.setText("D. " +x['Phương án D'])
                    text_to_speech('Phương án D .')
                    text_to_speech(x['Phương án D'], _language)
            except:
                print("Lỗi khi tìm câu hỏi trong database!")
                text_to_speech("Lỗi khi tìm câu hỏi trong database!")
                break

            # Đợi câu trả lời
            time.sleep(1)
            text_to_speech('Thời gian trả lời bắt đầu.')

            try:
                user_talk = listen_audio(self.language).lower()
                get_anwer_ok = False
                re_try = 0
                while not get_anwer_ok:

                    if ('phương án' in user_talk) or ('đáp án' in user_talk):
                        get_anwer_ok = True
                    else:
                        re_try +=1
                        print("Retry:", re_try)
                        if re_try > 3:
                            break
                        # Nghe lai
                        user_talk = listen_audio(self.language).lower()
                print("get answer", get_anwer_ok)
                if get_anwer_ok:

                    _answer1 = 'phương án ' +  str(x['Đáp án']).lower()
                    _answer2 = 'đáp án ' +  str(x['Đáp án']).lower()
                    # _answer1 =  str(x['Đáp án']).lower()
                    # _answer2 =  str(x['Đáp án']).lower()
                    if  (_answer1 in user_talk) or ( _answer2 in user_talk) :
                        self.num_of_correct += 1
                        print("Chúc mừng bạn đã trả lời đúng!")
                        text_to_speech("Chúc mừng bạn đã trả lời đúng!")
                        text_to_speech('Đáp án đúng là: ' + x['Đáp án'] + ".")
                        text_to_speech(x['Phương án '+ x['Đáp án']],_language)
                    else:
                        print("Xin chia buồn vì bạn đã trả lời sai!")
                        text_to_speech("Xin chia buồn vì bạn đã trả lời sai!")
                        text_to_speech('Đáp án đúng là: ' + x['Đáp án'] + ".")
                        text_to_speech(x['Phương án '+ x['Đáp án']], _language)
                else:
                    print("Không nhận được câu trả lời hợp lệ.")
                    text_to_speech("Xin lỗi, chúng tôi không nhận được câu trả lời hợp lệ.")
            except:
                print("Lỗi khi nghe câu trả lời")
                break
            self.ui.txtResult.setText(str(self.num_of_correct) +"/"+  str(self.num_of_ask))
            self.ui.txtCauHoi.setText('')
            self.ui.txtDapAnA.setText('')
            self.ui.txtDapAnB.setText('')
            self.ui.txtDapAnC.setText('')
            self.ui.txtDapAnD.setText('')
        # Tuyên bố kết quả
        text_to_speech("Chúc mừng bạn đã kết thúc bài kiểm tra. Bạn đã trả lời đúng {} trên {} câu hỏi".format(self.num_of_correct, self.num_of_ask ))
        self.test_status = False

if __name__ == '__main__':
    AskAndAnswer()