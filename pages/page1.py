import time
import numpy as np
import pandas as pd
import streamlit as st

st.markdown("# Page 1 ❄️")
st.sidebar.markdown("# Page 1 ❄️")



_LOREM_IPSUM = """
เกาะช้าง เป็นเกาะที่ใหญ่ที่สุดในฝั่งอ่าวไทย บนเกาะเพียบพร้อมและครบครันไปด้วยการบริการและสิ่งอำนวยความสะดวกอย่างมากมาย การเดินทางไปเกาะช้างยังสะดวกสบายเพราะมีเรือเฟอรี่ลำใหญ่ให้บริการวันละหลายเที่ยว ราคาค่าเรือข้ามเกาะคนละ 50 บาท ถ้านำรถไปด้วยก็ขับได้อย่างสะดวกสบายแต่ก็ต้องระวังในเรื่องของเส้นทางเพราะ เกาะช้างบางส่วนเส้นทางเลียบริมหน้าผา หรือถ้าใครอยากเดินทางด้วยรถสาธารณะก็มีรถสองแถว หรือจะเช่ามอเตอร์ไซต์ก็มีให้เลือกอีกเช่นกัน ในส่วนของห้องพักนั้นมีให้เลือกอย่างหลากหลาย เพราะด้วยความที่เป็นเกาะใหญ่นักท่องเที่ยวจึงไม่ต้องกังวลในเรื่องนี้

เกาะกระดาด เป็นหนึ่งใน 52 เกาะของหมู่เกาะทะเลตราด เป็นเกาะส่วนตัวที่ได้มีการออกโฉนดอย่างถูกต้องตามกฎหมายตั้งแต่สมัยรัชกาลที่ 5 เกาะกระดาดมีหน้าหาดที่ทอดเป็นแนวยาว ทรายขาวสะอาด บนชายหาดมีต้นมะพร้าวเรียงรายให้ความร่มรื่นเย็นสบาย นอกจากนี้เกาะแห่งนนี้ยังเป็นเมือนซาฟารีกลางทะเล เพราะบนเกาะแห่งนี้จะมีกวางน้อยใหญ่หลายสิบตัว ที่เจ้าของเกาะได้นำมาเลี้ยงไว้ ซึ่งจากเดิมมีเพียงแค่ 6 ตัว แต่เมื่อเวลาผ่านไปก็ได้ออกลูกออกหลานจนมีจำนวนเพิ่มขึ้นเป็นหลักร้อย สำหรับนักท่องเที่ยวที่ต้องการมาท่องเที่ยวบนเกาะกระดาด สามารถพักค้างแรมได้เพราะ บนเกาะแห่งนี้มีรีสอร์ทที่พักที่ค่อยอำนวยความสะดวกแก่นักท่องเที่ยว อีกทั้งยังมีกิจกรรมนั่งรถอีแต๊กชมวิวธรรมชาติรอบด้านของเกาะกระดาดได้อีกด้วย
"""


def stream_data():
    for word in _LOREM_IPSUM.split():
        yield word + " "
        time.sleep(0.02)

    yield pd.DataFrame(
        np.random.randn(5, 10),
        columns=["a", "b", "c", "d", "e", "f", "g", "h", "i", "j"],
    )

    for word in _LOREM_IPSUM.split():
        yield word + " "
        time.sleep(0.02)


if st.button("Stream data"):
    st.write_stream(stream_data)