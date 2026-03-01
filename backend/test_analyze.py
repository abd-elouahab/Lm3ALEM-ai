import asyncio
import io
from app.routers.jobs import analyze_job
from fastapi import UploadFile

async def test():
    file = UploadFile(filename='test.jpg', file=io.BytesIO(b'fake image'))
    try:
        res = await analyze_job(file, client_comment='test', city='agadir', db=None)
        print("SUCCESS:", res)
    except Exception as e:
        import traceback
        traceback.print_exc()

asyncio.run(test())
