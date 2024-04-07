import gradio as gr
from openai import OpenAI
client = OpenAI(api_key="your key")
import os
import threading

### 사용자 정의 함수 기능
def check_notepad_keywords(txt):
    weather_keywords = ['메모장', '메모장 열어줘', '메모장 열어']  # 날씨 관련 키워드 리스트
    for keyword in weather_keywords:
        if keyword in txt:
            return True
    return False

### 기능 동작
def open_notepad(txt):
    os.startfile('notepad.exe')
    return "메모장 열었어😄"

#오디오 출력
import time
from pathlib import Path
speech_file_path = Path(__file__).parent / "speech.mp3"
def stream_to_speakers(chat_response) -> None:
    import pyaudio

    player_stream = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1, rate=24000, output=True)

    start_time = time.time()

    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="nova",
        response_format="pcm",  # similar to WAV, but without a header chunk at the start.
        input=chat_response,
    ) as response:
        print(f"Time to first byte: {int((time.time() - start_time) * 1000)}ms")
        for chunk in response.iter_bytes(chunk_size=1024):
            player_stream.write(chunk)

    print(f"Done in {int((time.time() - start_time) * 1000)}ms.")

#AI채팅
def chat_with_gpt(input, history):
    history.append({"role": "user", "content": input})
  
    if check_notepad_keywords(input):
        note_info = open_notepad(input)
        history.append({"role": "assistant", "content": note_info})  # 기능 함수 리턴값 메세지를 대화기록에 추가
     
    else:
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k", #원하는 ai모델 설정가능
            messages=history
        )
        response = gpt_response.choices[0].message.content
        # ai응답에 취소선이 있을경우 제거
        if response.startswith('<s>'):
            response = response[3:]

        history.append({"role": "assistant", "content": response})

    messages = [(history[i]["content"], history[i+1]["content"]) for i in range(1, len(history), 2)]

    #ai응답 음성 
    if len(history) > 0 and history[-1]["role"] == "assistant":
        threading.Thread(target=stream_to_speakers, args=(history[-1]["content"],)).start()
 
    return messages, history 


#그라디오 인터페이스
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="ChatBot")

    state = gr.State([{
        "role": "system",
        "content": """
AI페르소나 설정 
"""
    }])
    #그라디오 인터페이스
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="챗봇에게 아무거나 물어보세요").style(container=False)
    #제출버튼
    txt.submit(chat_with_gpt, [txt, state], [chatbot, state])
    #텍스트제출후 입력창 내용 초기화 
    txt.submit(lambda x: gr.update(value=''), [],[txt])
#share = ture 공개링크 생성
demo.launch(debug=True, share=True)