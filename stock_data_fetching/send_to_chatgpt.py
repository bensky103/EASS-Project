from openai import OpenAI

#Use a different model for better stock prediction performance if applicable
def send_features_to_gpt(payload: dict, api_key: str, model="gpt-4") -> str:
    client = OpenAI(api_key=api_key)
    
    prompt = f"Analyze the following stock data:\n\n{payload}"
    
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content 