from openai import OpenAI

client = OpenAI(
  base_url = "https://integrate.api.nvidia.com/v1",
  api_key = "$API_KEY_REQUIRED_IF_EXECUTING_OUTSIDE_NGC"
)

completion = client.chat.completions.create(
  model="nvidia/nvidia-nemotron-nano-9b-v2",
  messages=[{"role":"system","content":"/think"}],
  temperature=0.6,
  top_p=0.95,
  max_tokens=2048,
  frequency_penalty=0,
  presence_penalty=0,
  stream=True,
  extra_body={
    "min_thinking_tokens": 1024,
    "max_thinking_tokens": 2048
  }
)

for chunk in completion:
  reasoning = getattr(chunk.choices[0].delta, "reasoning_content", None)
  if reasoning:
    print(reasoning, end="")
  if chunk.choices[0].delta.content is not None:
    print(chunk.choices[0].delta.content, end="")
