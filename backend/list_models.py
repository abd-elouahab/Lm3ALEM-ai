from openai import OpenAI
from app.config import settings

client = OpenAI(
    api_key=settings.XAI_API_KEY,
    base_url="https://api.x.ai/v1",
)

models = client.models.list()
for m in models.data:
    print(m.id)
