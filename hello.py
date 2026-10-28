"""This is just a check that Python can talk to Ollama"""
from ollama import chat

response = chat(
    model="llama3.2",
    messages=[{"role": "user", "content": "Hi, how are you?"}],
    options={"num_predict": 100},
)

print(response.message.content)
print("Input tokens:", response.prompt_eval_count)
print("Output tokens:", response.eval_count)
if response.eval_count and response.eval_duration:
    print("Tokens/second:", round(response.eval_count / response.eval_duration * 1e9, 1))
else:
    print("No statistics in the response")