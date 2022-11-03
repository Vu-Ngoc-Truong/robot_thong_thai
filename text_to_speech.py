#!/usr/bin/env python
# -*-coding:utf-8-*-

import os
import playsound
from gtts import gTTS
# import time
# import sys
# import wikipedia
# wikipedia.set_lang('vi')

def text_to_speech(text, language='vi'):
    output = gTTS(text,lang=language, slow=False)
    output.save("output.mp3")
    playsound.playsound('output.mp3', True)
    os.remove("output.mp3")

# speak("Xin chào buổi tối")