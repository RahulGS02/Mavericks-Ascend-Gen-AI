from openai import OpenAI

endpoint = "https://mavericks-ai.services.ai.azure.com/openai/v1"
deployment_name = "gpt-4.1-mini"
api_key = "<your-api-key>"

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

completion = client.chat.completions.create(
    model=deployment_name,
    messages=[
        {
            "role": "user",
            "content": "What is the capital of France?",
        }
    ],
)

print(completion.choices[0].message)


from openai import OpenAI

endpoint = "https://mavericks-ai.services.ai.azure.com/openai/v1"
deployment_name = "gpt-4.1-mini"
api_key = "<your-api-key>"

client = OpenAI(
    base_url=endpoint,
    api_key=api_key
)

response = client.responses.create(
    model=deployment_name,
    input="What is the capital of France?",
)

print(f"answer: {response.output[0]}")