# -*- coding: utf-8 -*-
import asyncio
import edge_tts

async def main():
    texts = [
        "Đặc biệt, mở lối vào các trường đại học top đầu",
        "Bộ đề thi Đánh giá năng lực và Đánh giá tư duy",
        "Các kỳ thi riêng như H S A, T S A và V A C T",
        "Tư duy định lượng, định tính và khoa học"
    ]
    for i, t in enumerate(texts):
        try:
            c = edge_tts.Communicate(t, voice="vi-VN-NamMinhNeural")
            await c.save(f"test_out_{i}.mp3")
            print(f"Index {i} OK: {t}")
        except Exception as e:
            print(f"Index {i} FAIL: {e}")
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
