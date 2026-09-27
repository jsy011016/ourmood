# app.py
import gradio as gr
from catvton import CatVTON

model = CatVTON()


def multi_fitting(person_img, bottom_img, top_img, outer_img):
    """다중 의상 순차 피팅"""

    result = person_img

    # 1단계: 하의 입히기
    if bottom_img is not None:
        result = model.inference(result, bottom_img)

    # 2단계: 상의 입히기 (하의 입은 결과에)
    if top_img is not None:
        result = model.inference(result, top_img)

    # 3단계: 아우터 입히기 (상의+하의 입은 결과에)
    if outer_img is not None:
        result = model.inference(result, outer_img)

    return result


demo = gr.Interface(
    fn=multi_fitting,
    inputs=[
        gr.Image(label="사용자 사진"),
        gr.Image(label="하의 (선택)", optional=True),
        gr.Image(label="상의 (선택)", optional=True),
        gr.Image(label="아우터 (선택)", optional=True)
    ],
    outputs=gr.Image(label="최종 결과")
)

demo.launch()