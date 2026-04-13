from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="llama-3.1-8b-instant"
)

response = llm.invoke("Say 'Setup complete!' if you can hear me.")

print(response.content)