from openai import OpenAI
import os
from typing import Optional, Dict, Any


class ChatGPTAPI:
    def __init__(self, api_key: Optional[str] = None):
        """
        ChatGPT API 클라이언트 초기화

        Args:
            api_key: OpenAI API 키. 없으면 환경변수에서 가져옴
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("API 키가 필요합니다. 환경변수 OPENAI_API_KEY를 설정하거나 직접 입력해주세요.")

        self.client = OpenAI(api_key=self.api_key)

    def chat_completion(
            self,
            messages: list[Dict[str, str]],
            model: str = "gpt-3.5-turbo",
            temperature: float = 0.7,
            max_tokens: int = 1000
    ) -> Dict[str, Any]:
        """
        ChatGPT API를 호출하여 응답을 받습니다.

        Args:
            messages: 대화 메시지 목록
            model: 사용할 모델
            temperature: 응답의 무작위성 (0.0 ~ 1.0)
            max_tokens: 최대 토큰 수

        Returns:
            API 응답 딕셔너리
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens
            )
            return response

        except Exception as e:
            print(f"오류 발생: {str(e)}")
            raise


# 사용 예시
# if __name__ == "__main__":
#     # API 클라이언트 초기화
#     client = ChatGPTAPI()
#
#     # 대화 메시지 구성
#     messages = [
#         {"role": "user", "content": "Java에 대해 설명하라"}
#     ]
#
#     # API 호출
#     try:
#         response = client.chat_completion(messages)
#
#         # 응답 출력
#         if response:
#             assistant_message = response.choices[0].message.content
#             print("ChatGPT 응답:", assistant_message)
#
#     except Exception as e:
#         print(f"오류 발생: {str(e)}")