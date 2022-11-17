from os.path import join as path_join
import numpy as np
import cv2
import onnxruntime
from statics.constants import STYLES_PATH_FULL


def preprocess(img):
    img = cv2.resize(img, (640, 640))
    img = img.transpose((2, 0, 1))
    img = img.reshape(1, 3, 640, 640)
    mean_vec = np.array([0.485, 0.456, 0.406])
    stddev_vec = np.array([0.229, 0.224, 0.225])
    norm_img_data = np.zeros(img.shape).astype('float32')
    for i in range(img.shape[0]):
        # for each pixel and channel
        # divide the value by 255 to get value between [0, 1]
        norm_img_data[i, :, :] = (img[i, :, :] / 255 - mean_vec[i]) / stddev_vec[i]
    return norm_img_data


def piece_in_code(p1, p2, point):
    x1, y1 = p1
    x2, y2 = p2
    x, y = point

    if x1 <= x <= x2 and y1 <= y <= y2:
        return True
    elif x2 <= x <= x1 and y2 <= y <= y1:
        return True
    else:
        return False


def process_results(codes, pieces):
    all_codes = {code_id: {'code-data': code, 'pieces': []} for code_id, code in enumerate(codes)}

    for piece in pieces:
        piece_center = ((piece[2] + piece[0]) / 2, (piece[3] + piece[1]) / 2)
        for code_id, code in enumerate(codes):
            if piece_in_code((code[0], code[1]), (code[2], code[3]), piece_center):
                all_codes[code_id]['pieces'].append([piece_center] + piece)
                break
    out_codes = []
    for code_id, code in all_codes.items():
        if len(code['pieces']) == 16:  # == 16
            code['pieces'] = sorted(code['pieces'], key=lambda p: p[0][0])
            rows = [
                sorted(code['pieces'][:4], key=lambda p: p[0][1]),
                sorted(code['pieces'][4:8], key=lambda p: p[0][1]),
                sorted(code['pieces'][8:12], key=lambda p: p[0][1]),
                sorted(code['pieces'][12:16], key=lambda p: p[0][1]),
            ]
            sorted_pieces = []
            for index in range(4):
                sorted_pieces.append(rows[0][index])
                sorted_pieces.append(rows[1][index])
                sorted_pieces.append(rows[2][index])
                sorted_pieces.append(rows[3][index])
            code['pieces'] = sorted_pieces
            out_codes.append(code)
    return out_codes


def yolo_detector(img, style_module):
    img_in = img.copy()
    # Preprocess the image
    img = preprocess(img)

    model_dir = STYLES_PATH_FULL.format(style_module['style-info']['name'])
    model = path_join(model_dir, 'model.onnx')

    session = onnxruntime.InferenceSession(model, None)
    input_name = session.get_inputs()[0].name
    output_name = session.get_outputs()[0].name

    results = session.run([output_name], {input_name: img})
    print(results)
    pieces, codes = [], []
    for r in results[0]:
        piece_name = style_module['object-detection-model']['key-to-name'][r[-2]]
        if piece_name == 'coji-frame':
            continue

        if piece_name == 'coji-code':
            codes.append(list(r)[1:])
            codes[-1][-2] = piece_name
        else:
            pieces.append(list(r)[1:])
            pieces[-1][-2] = piece_name

    [print(c) for c in codes]
    print('------------')
    [print(p) for p in pieces]
    result = process_results(codes, pieces)
    if result:
        result = result[0]
        out_code = ''
        for p in result['pieces']:
            out_code += style_module['name-to-key'][p[-2]]
        return out_code

    else:
        print('No code detected')
        return None


if __name__ == '__main__':
    img = cv2.imread(
        #    "C:\\Users\\maxfyk\\Documents\\coji\\coji-object-detector\\data\\out\\generate_coji_codes\\Taipei\\partitioned\\images\\train\\aaaamejkjijdhblh.jpg")
        # "C:\\Users\\maxfyk\\Desktop\\test.jpg")
        "C:\\Users\\maxfyk\\Desktop\\test3.jpg")
    # "C:\\Users\\maxfyk\\Desktop\\download (4).jpg")

    yolo_detector(img, style_module)
