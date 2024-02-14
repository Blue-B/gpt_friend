import gradio as gr
from openai import OpenAI
client = OpenAI(api_key="your key")
import os

###키워드 체크
def check_note_keywords(txt):
    note_keywords = ['메모장 열어줘', '메모장 열어']  # 날씨 관련 키워드 리스트
    for keyword in note_keywords:
        if keyword in txt:
            return True
    return False

###기능1
def open_notepad():
    os.startfile('notepad.exe')
    return "메모장이 열렸습니다."

def chat_with_gpt(input, history):
    #user input 기록 추가
    history.append({"role": "user", "content": input})
    if check_notepad_keywords(input):
        note_info = open_notepad(input)
        history.append({"role": "assistant", "content": note_info})  # 메모장 응답을 대화 기록에 추가

    else: #gpt api 호출
        gpt_response = client.chat.completions.create(
            model="gpt-3.5-turbo-16k",
            messages=history
        ) #GPT응답 RESPONSE변수에 저장 및 대화기록에 추가
        response = gpt_response.choices[0].message.content
        history.append({"role": "assistant", "content": response})
        print(history)

    
    messages = [(history[i]["content"], history[i+1]["content"]) for i in range(1, len(history), 2)]
#메세지및 기록 반환
    return messages, history

#그라디오 인터페이스
with gr.Blocks() as demo:
    chatbot = gr.Chatbot(label="ChatBot")

    state = gr.State([{
        "role": "system",
        "content": """
gpt prompt
"""
    }])

    #그라디오 하단 인터에피스
    with gr.Row():
        txt = gr.Textbox(show_label=False, placeholder="챗봇에게 아무거나 물어보세요").style(container=False)
        
    #제출버튼
    txt.submit(chat_with_gpt, [txt, state], [chatbot, state])

    #텍스트 입력후 입력창 내용 초기화 
    txt.submit(lambda x: gr.update(value=''), [],[txt])

#share = ture 공개링크 생성
demo.launch(debug=True, share=True)