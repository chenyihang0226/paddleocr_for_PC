from paddleocr import PaddleOCR
from PIL import Image, ImageDraw

external_info = {
            "常规继电保护定值区号",
            "保护CT额定一次值：",
            "保护CT额定二次值：",
            "零序CT额定一次值：",
            "零序CT额定二次值：",
            "过流段投入：",
            "过流工段投入：",
            "零序过流段投入：",
            "一次重合闸投入：",
            "二次重合闸投入：",
            "过流I段定值：",
            "过流I段时间：",
            "过流II段定值：",
            "过流II段时间：",
            "零序过流I段定值：",
            "零序过流工段定值：",
            "零序过流I段时间：",
            "零序过流工段时间：",
            "一次重合闸时间：",
            "二次重合闸闭锁时间：",
            "二次重合闸时间：",
            "远方整定投入软压板",
            "重合闸投入软压板",
            "保护投入软压板",
            "保护跳闸出口",
            "保护合闸出口",
            "停用自动解列功能",
            "重合闸投入",
            "检修状态投入",
            "停用保护及FA功能",
            "停用同期合闸功能",
            "远方就地转换",
            "控制功能转换",
            "照明旋钮",
            "遥控/电动合闸出口",
            "遥控/电动分闸出口",
            "安全自动控制功能投入",
            # "分位",
            # "合位",
            # "过流",
            # "告警",
            # "充电",
            # "通讯",
            # "异常",
            # "电源",
            # "运行",
            # "未储能",
            # "远方",
            # "开关",
            # "传动",
            # "线路",
            # "故障",
            # "接地",
            # "智能",
            # "分布式",
            # "就地",
            # "FA",
            # "常规",
            # "隔离刀接地刀",
            # "保护",
            # "合闸",
            # "重合闸",
            # "故障",
            # "分布式",
            # "闭锁合位合位保护",
            # "动作动作",
            # "重合闸保护",
            # "合闸 隔离刀 接地刀",
            # "动作动作闭锁合位合位保护",
            # "闭锁合位合位",
            # "保护"
    }

ocr = PaddleOCR(lang="ch") # 通过 lang 参数来使用英文模型
ocr = PaddleOCR(device="gpu") # 通过 device 参数使得在模型推理时使用 GPU
ocr = PaddleOCR(
    det_model_dir="./PP-OCRv5_server_det_infer/",
    rec_model_dir="./PP-OCRv5_server_rec_infer/",
    use_doc_orientation_classify=False,
    use_doc_unwarping=False,
    use_textline_orientation=False,
) # 更换 PP-OCRv5_server 模型


img_path = "./test1.jpg"
result = ocr.predict(img_path)

# for res in result:
#     res.save_to_json("./ocr_result.json")  # 将 OCR 结果保存为 JSON 文件

# 匹配成功结果
filtered_rec = []

# 读取原图用于框选
img = Image.open(img_path).convert("RGB")
draw = ImageDraw.Draw(img)

for res in result:
    # 兼容字段：rec_texts / rec_text
    rec_texts = res.get("rec_texts")
    rec_polys = res.get("rec_polys")

    if rec_texts is None and "rec_text" in res:
        rec_texts = [res["rec_text"]]
        rec_polys = [res.get("rec_poly")] if res.get("rec_poly") is not None else [None]

    if not rec_texts:
        continue

    for i, txt in enumerate(rec_texts):
        txt = str(txt).strip()
        # 模式匹配：包含任一 external_info 关键词即视为命中
        hit = any(key in txt for key in external_info)
        if hit:
            filtered_rec.append(txt)

            # 画框（如果有坐标）
            if rec_polys and i < len(rec_polys) and rec_polys[i] is not None:
                poly = rec_polys[i]
                # poly 通常是4点多边形 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                pts = [(float(p[0]), float(p[1])) for p in poly]
                draw.line(pts + [pts[0]], fill=(255, 0, 0), width=3)

print("filtered_rec:")
for t in filtered_rec:
    print(t)

# 保存框选结果图
out_path = "./output_matched.jpg"
img.save(out_path)
print(f"已保存框选结果: {out_path}")

