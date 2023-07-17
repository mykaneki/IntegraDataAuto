@echo off
cd D:\project\PycharmProjects\atxserver2-android-provider
start D:\project\PycharmProjects\rethinkdb\Windows\rethinkdb.exe
cd C:\Users\27951
start appium
cd D:\project\PycharmProjects\atxserver2-master
start python .\main.py
cd D:\project\PycharmProjects\atxserver2-android-provider
start python main.py --server localhost:4000
