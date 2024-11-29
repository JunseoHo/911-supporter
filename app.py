# streamlit run app.py로 실행합니다.

import streamlit as st
import datetime
from transformers import AutoModelForTokenClassification, AutoTokenizer, pipeline
from ChatGPTAPI import ChatGPTAPI

# NER(개체명 인식) 모델 초기화
# 개체명 인식은 텍스트 문장으로부터 사람, 장소 등의 명칭을 식별하기 위해 사용합니다.
model_name = "dslim/bert-base-NER"
model = AutoModelForTokenClassification.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)
nlp = pipeline("ner", model=model, tokenizer=tokenizer)

# ChatGPTAPI를 사용하기 위한 클래스.
# 클래스 정의는 ChatGPTAPI.py 파일을 참고해주세요.
chatgptapi = ChatGPTAPI()

# 대화 내용을 저장해두기 위한 전역변수
trans_script = ""


# streamlit 세션 상태 초기화
def init_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'caller_active' not in st.session_state:
        st.session_state.caller_active = False
    if 'operator_active' not in st.session_state:
        st.session_state.operator_active = False
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'caller_clicked' not in st.session_state:
        st.session_state.caller_clicked = False
    if 'operator_clicked' not in st.session_state:
        st.session_state.operator_clicked = False


# 콜백 함수
def caller_callback():
    st.session_state.caller_clicked = True


def operator_callback():
    st.session_state.operator_clicked = True


# 버튼 클릭 핸들러
def handle_caller():
    script = st.session_state.script
    ner_results = estimate_info(script)
    print(ner_results)
    for entity in ner_results:
        if entity['entity'] == 'B-PER':
            st.session_state.name = entity['word']
        elif entity['entity'] == 'B-LOC':
            st.session_state.location = entity['word']
    st.session_state.script = ""
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    global trans_script
    trans_script += f"[{current_time}] Caller: {script}" + '\n'
    st.session_state.chat_history.append(f"[{current_time}] Caller: {script}")
    infer_situation()
    infer_armed()
    create_report()


def handle_operator():
    script = st.session_state.script
    st.session_state.script = ""
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    global trans_script
    trans_script += f"[{current_time}] Operator: {script}" + '\n'
    st.session_state.chat_history.append(f"[{current_time}] Operator: {script}")


# estimate_info: NER 모델을 활용하여 사람, 장소 등의 명칭을 식별한 뒤 반환합니다.
def estimate_info(text):
    ner_results = nlp(text)
    return ner_results


# infer_situation: 프롬프트 엔지니어링을 통해 사전 정의된 상황 중 하나로 현재 상황을 분류합니다.
def infer_situation():
    global trans_script
    messages = [
        {"role": "user", "content": f"{trans_script}\n\n위 대화를 아래 상황 중 하나로 분류하라. "
                                    f"답변은 반드시 아래 상황 중 하나로만 답하라."
                                    f"* Kidnapping Attempt"
                                    f"* Home Invasion"
                                    f"* Armed Robbery"
                                    f"* Unknown"}
    ]
    try:
        response = chatgptapi.chat_completion(messages)

        # 응답 출력
        if response:
            assistant_message = response.choices[0].message.content
            st.session_state.type = assistant_message
    except Exception as e:
        print(f"오류 발생: {str(e)}")


# infer_armed: 프롬프트 엔지니어링을 통해 범인의 무장 여부를 판단합니다.
def infer_armed():
    global trans_script
    messages = [
        {"role": "user", "content": f"{trans_script}\n\n위 대화에서 범죄자의 무장 여부를 Yes, No, Unknown으로 답하라."}
    ]
    try:
        response = chatgptapi.chat_completion(messages)
        # 응답 출력
        if response:
            assistant_message = response.choices[0].message.content
            st.session_state.armed = assistant_message
    except Exception as e:
        print(f"오류 발생: {str(e)}")


# create_report: 출동 오퍼레이터(Dispatcher)에게 전달할 리포트를 생성합니다.
def create_report():
    global trans_script
    messages = [
        {"role": "user",
         "content": f"{trans_script}\n\nBased on the above conversation, specify the reporter's name and location, explain the situation, and write a report to deliver to dispatchers."}
    ]
    try:
        response = chatgptapi.chat_completion(messages)
        # 응답 출력
        if response:
            assistant_message = response.choices[0].message.content
            st.session_state.report = assistant_message
    except Exception as e:
        print(f"오류 발생: {str(e)}")

# 메인 함수
def main():
    st.set_page_config(layout="wide")

    # 세션 상태 초기화
    init_session_state()

    # 클릭 상태 처리
    if st.session_state.caller_clicked:
        handle_caller()
        st.session_state.caller_clicked = False

    if st.session_state.operator_clicked:
        handle_operator()
        st.session_state.operator_clicked = False

    # CSS 스타일 추가
    # CSS 스타일 부분만 수정합니다
    st.markdown("""
        <style>
        [data-testid="column"] {
            padding: 0px !important;
            margin: 0px !important;
        }
        .stButton > button {
            width: 100%;
            margin: 0px !important;
            border-radius: 0px !important;
        }
        .chat-container {
            background-color: black;
            height: 400px;
            overflow-y: auto;
            border: 1px solid #333;
            padding: 10px;
            margin-bottom: 10px;
        }
        .chat-message {
            margin: 0;
            padding: 5px 0;
            font-family: 'Courier New', Courier, monospace;
            color: #00ff00;
        }
        /* 스크롤바 스타일링 */
        .chat-container::-webkit-scrollbar {
            width: 10px;
        }
        .chat-container::-webkit-scrollbar-track {
            background: #1a1a1a;
        }
        .chat-container::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 5px;
        }
        .chat-container::-webkit-scrollbar-thumb:hover {
            background: #444;
        }
        </style>
    """, unsafe_allow_html=True)

    # 전체 컨테이너
    with st.container():
        # 두 개의 컬럼으로 분할
        left_col, right_col = st.columns([2, 1])

        with left_col:
            chat_container = st.container()
            with chat_container:
                messages_html = ""
                for message in st.session_state.chat_history:
                    messages_html += f'<p class="chat-message">{message}</p>'

                st.markdown(f"""
                   <div class="chat-container">
                       {messages_html}
                   </div>
               """, unsafe_allow_html=True)

            # 버튼 영역 부분만 수정
            text_col, button_col1, button_col2, _ = st.columns([4, 1, 1, 0.000001])  # 텍스트 입력 컬럼 비율을 2로 증가
            with text_col:
                st.text_input("Path", key="script", label_visibility="collapsed")
            with button_col1:
                st.button(
                    "Caller",
                    on_click=caller_callback,
                    type="primary" if st.session_state.caller_active else "secondary",
                    key="caller_button"
                )
            with button_col2:
                st.button(
                    "Operator",
                    on_click=operator_callback,
                    type="primary" if st.session_state.operator_active else "secondary",
                    key="operator_button"
                )

        # 오른쪽 컬럼
        with right_col:
            info_col1, info_col2 = st.columns(2)
            with info_col1:
                st.text_input("Name", key="name", placeholder="Unknown", disabled=True)
            with info_col2:
                st.text_input("Location", key="location", placeholder="Unknown", disabled=True)

            info_col3, info_col4 = st.columns(2)
            with info_col3:
                st.text_input("Gender", key="gender", placeholder="Unknown", disabled=True)
            with info_col4:
                st.text_input("Type", key="type", placeholder="Unknown", disabled=True)

            info_col5, info_col6 = st.columns(2)
            with info_col5:
                st.text_input("Age", key="age", placeholder="Unknown", disabled=True)
            with info_col6:
                st.text_input("Armed", key="armed", placeholder="Unknown", disabled=True)

            st.text_area("Report", key="report", height=150)


if __name__ == "__main__":
    main()
