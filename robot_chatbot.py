#! /usr/bin/env python3
# -*- coding: utf-8 -*-

# pip install ChatterBot
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer
import os
import time
from gtts import gTTS
import playsound
import audioop
import speech_recognition as sr
from text_to_speech import text_to_speech
from speech_to_text import listen_audio

class RobotChatter:
    def __init__(self,  bot_name, language='vi', *args, **kwargs):

        self.language = language
        self.name = bot_name
        self.chatbot = ChatBot(
            self.name,
            storage_adapter='chatterbot.storage.SQLStorageAdapter',
            logic_adapters=[
                'chatterbot.logic.MathematicalEvaluation',
                {
                    'import_path': 'chatterbot.logic.BestMatch',
                    'maximum_similarity_threshold': 0.80
                }
            ],
            database_uri='sqlite:///database.db',

        )

    def training(self):
        """ Training for chatbot
        """
        # Creat trainer for chatbot
        self.trainer = ListTrainer(self.chatbot)

        # Training for chatbot
        if self.language=="vi":
            conversation = [
                "Xin chào",
                "Chào bạn",
                "Bạn tên là gì?",
                self.name,
                "Bạn có khỏe không",
                "Tôi khỏe, cảm ơn bạn",
                "Bạn đến từ đâu?",
                "Tôi ở hà nội, còn bạn?",
                "Tôi ở thanh hóa",
                "Bạn bao nhiêu tuổi",
                "Tôi năm nay 32 tuổi",
                "Cảm ơn",
                "Cảm ơn bạn",
                "Tạm biệt",
                "Tạm biệt."
            ]
            self.trainer.train(conversation)

        if self.language=="en":
            self.trainer.train([
                "Hello",
                "Hi",
                "How are you?",
                "I'm good. How are you?",
                "Good. Do you speak English?",
                "A little. Are you American?",
                "Yes.",
                "Where are you from?",
                "I'm from California.",
                "Nice to meet you.",
                "Nice to meet you too."
            ])

            self.trainer.train([
                "Greetings!",
                "Hello",
            ])

            self.trainer.train([
                "Hello",
                "Hi there!",
                "How are you doing?",
                "I'm doing great.",
                "That is good to hear",
                "Thank you.",
                "You're welcome."
            ])

    def giao_tiep(self):

        print("____________Start conversation!___________")
        user_talk = ""
        if  self.language == "vi":
            text_to_speech("Xin chào", self.language)
        if  self.language == "en":
            text_to_speech("Hello", self.language)

        while True:
            print("User \t>>", end=" ")
            # user_talk = input()
            user_talk = listen_audio(self.language).lower()

            if self.language == "vi" and ("tạm biệt" in user_talk ):
                print("Chatbot <<","Tạm biệt!")
                text_to_speech("Tạm biệt!", self.language)
                break
            if self.language == "en" and ("goodbye" in user_talk ):
                print("Chatbot <<","Goodbye!")
                text_to_speech("Goodbye!", self.language)
                break
            response = self.chatbot.get_response(user_talk)
            print("Chatbot <<",response)
            text_to_speech(str(response), self.language)
            time.sleep(0.1)
            # if KeyboardInterrupt:
            #     break

if __name__ == '__main__':
    # Khởi tạo chatbot
    my_chat_bot = RobotChatter("Bình Minh", "en")
    my_chat_bot.training()
    my_chat_bot.giao_tiep()
