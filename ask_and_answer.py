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


if __name__ == "__main__":

    mydb = MongodbStorage("mongodb://coffee:coffee@localhost:27017")
    # Linh vuc van hoc
    mycol = mydb.vanhocCollection
    ask_num = 1

    # Print collection before update
    for i in  range(3):
        text_to_speech('Câu hỏi số {}:'.format(i+1))
        x = mycol.find_one({"STT": str(i+1)})
        print(x)
        text_to_speech(x['Câu hỏi'])
        text_to_speech('Phương án A .' + x['Phương án A'])
        text_to_speech('Phương án B .' + x['Phương án B'])
        text_to_speech('Phương án C .' + x['Phương án C'])
        text_to_speech('Phương án D .' + x['Phương án D'])
