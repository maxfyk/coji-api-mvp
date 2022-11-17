from os.path import join as path_join
import numpy as np
import cv2
import onnxruntime
from statics.constants import STYLES_PATH_FULL

# STYLES_PATH_FULL = '..\statics\styles\geom-original'
# style_module = {}
#
# style_module['style-info'] = {
#     'name': 'geom-original',
#     'size': 600,
#     'rows': 4,
#     'pieces-row': 4,
#     'background-color': (26, 26, 26),
#     'border': {
#         'border-size': 15,
#         'border-color': (255, 191, 0),  # 'yellow',
#     },
#     'template': {
#         'add-template': True,
#         'template-offset': (30, 30),
#     }
# }
#
# style_module['style-info']['total-length'] = \
#     style_module['style-info']['rows'] * style_module['style-info']['pieces-row']
#
# style_module['name-to-key'] = {
#     'circle': 'a',
#     'd-arrow': 'b',
#     'e-circle': 'c',
#     'e-rhombus': 'd',
#     'e-square': 'e',
#     'e-triangle': 'f',
#     'l-arrow': 'g',
#     'minus': 'h',
#     'plus': 'i',
#     'r-arrow': 'j',
#     'rhombus': 'k',
#     'square': 'l',
#     'triangle': 'm',
#     'u-arrow': 'n',
#     'v-bar': 'o',
#     'x': 'p'
# }
# style_module['key-to-name'] = {v: k for k, v in style_module['name-to-key'].items()}
#
# style_module['names'] = list(style_module['name-to-key'].keys())
# style_module['keys'] = list(style_module['key-to-name'].keys())
#
# style_module['object-detection-model'] = {
#     'supported': True,
#     'num-items': 18,
#     'name-to-key': {'circle': 0, 'd-arrow': 1, 'e-circle': 2, 'e-rhombus': 3, 'e-square': 4, 'e-triangle': 5,
#                     'l-arrow': 6, 'minus': 7, 'plus': 8, 'r-arrow': 9, 'rhombus': 10, 'square': 11, 'triangle': 12,
#                     'u-arrow': 13, 'v-bar': 14, 'x': 15, 'coji-code': 16, 'coji-frame': 17}
# }
# style_module['object-detection-model']['key-to-name'] = {v: k for k, v in
#                                                          style_module['object-detection-model']['name-to-key'].items()}
#

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

    img_in = cv2.resize(img_in, (640, 640))

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

            img_in = cv2.rectangle(img_in, (int(r[1]), int(r[2])), (int(r[3]), int(r[4])), (36, 255, 12), 1)
            cv2.putText(img_in,
                        f'''{piece_name}: {str(round(r[-1], 2))}''',
                        (int(r[1]), int(r[2]) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (36, 255, 12), 1)

    [print(c) for c in codes]
    print('------------')
    [print(p) for p in pieces]
    result = process_results(codes, pieces)
    if result:
        result = result[0]
        out_code = ''
        for p in result['pieces']:
            out_code += style_module['name-to-key'][p[-2]]
        print('!!------')
        [print(p) for p in result['pieces']]
        print('!!------')
        print(len(result['pieces']))
        print(len(pieces))
        print(out_code)


    else:
        print('No code detected')


if __name__ == '__main__':
    img = cv2.imread(
        #    "C:\\Users\\maxfyk\\Documents\\coji\\coji-object-detector\\data\\out\\generate_coji_codes\\Taipei\\partitioned\\images\\train\\aaaamejkjijdhblh.jpg")
        # "C:\\Users\\maxfyk\\Desktop\\test.jpg")
        "C:\\Users\\maxfyk\\Desktop\\test3.jpg")
    # "C:\\Users\\maxfyk\\Desktop\\download (4).jpg")

    yolo_detector(img, style_module)
