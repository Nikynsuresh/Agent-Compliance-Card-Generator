import os
import google.generativeai as genai


class CustomerSupportAgent:
    """Low-risk FAQ Customer Support Assistant using Google Gemini."""

    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "mock-key"))
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    def answer_faq(self, user_query: str) -> str:
        prompt = f"Answer the customer question politely based on standard policies: {user_query}"
        response = self.model.generate_content(prompt)
        return response.text


if __name__ == "__main__":
    bot = CustomerSupportAgent()
    print(bot.answer_faq("What is your refund policy?"))
