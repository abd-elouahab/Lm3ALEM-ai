from app.ai.chat import chat_with_ai
import traceback

try:
    r = chat_with_ai(
        'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
        [],
        True
    )
    print('SUCCESS:', r)
except Exception as ex:
    traceback.print_exc()
