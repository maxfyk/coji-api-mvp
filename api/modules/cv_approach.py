import cv2
import numpy as np
import os
from statics.constants import STYLES_PATH_FULL

global STYLE_NAME


def change_brightness(img, value=40):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, value)
    v[v > 255] = 255
    v[v < 0] = 0
    final_hsv = cv2.merge((h, s, v))
    img = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
    return img


def get_trapeze_contour(trapeze):
    biliat_imge = cv2.bilateralFilter(trapeze, 5, 175, 175)

    edge_img = cv2.Canny(biliat_imge, 75, 200)

    contours, hierarchy = cv2.findContours(edge_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    perim = cv2.arcLength(contours[0], True)
    epsilon = 0.02 * perim
    corners = cv2.approxPolyDP(contours[0], epsilon, True)
    x, y = [], []
    for c in corners:
        x.append(c[0][0])
        y.append(c[0][1])
    x_min, x_max = min(x), max(x)
    y_min, y_max = min(y), max(y)
    corners = np.array([
        [[x_min, y_min]],
        [[x_min, y_max]],
        [[x_max, y_max]],
        [[x_max, y_min]],
    ])
    return corners


def get_best_match(img, area_t=20000, border_threshold=False, is_gray=False, center_score=True):
    """Find code square in the picture"""
    if area_t <= 1:
        area_t = img.shape[0] * img.shape[1] * area_t
    img = cv2.imread(img) if type(img) is str else img

    img_center = (int(img.shape[1] / 2), int(img.shape[0] / 2))

    if not is_gray:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        dilate = cv2.dilate(thresh, horizontal_kernel, iterations=2)
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        dilate = cv2.dilate(dilate, vertical_kernel, iterations=2)
    else:
        dilate = img
    contours = []
    cnts = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)[0]
    for c in cnts:
        area = cv2.contourArea(c)
        if area > area_t:
            x, y, w, h = cv2.boundingRect(c)
            if border_threshold and (x == 0 or y == 0):
                continue
            contours.append({'object': c})
            if center_score:
                dist_to_center = abs((x + w / 2) - img_center[0]) + abs((y + h / 2) - img_center[1])
                is_square_score = (min((w, h)) / max((w, h))) / 10
                contours[-1]['match-score'] = dist_to_center / is_square_score
                # print(w, h, is_square_score, contours[-1]['match-score'], area)
            else:
                contours[-1]['match-score'] = -area
    tops = sorted(contours, key=lambda d: d['match-score'])
    return tops[0] if tops else None


def order_points(pts):
    # initialzie a list of coordinates that will be ordered
    # such that the first entry in the list is the top-left,
    # the second entry is the top-right, the third is the
    # bottom-right, and the fourth is the bottom-left
    rect = np.zeros((4, 2), dtype="float32")

    # the top-left point will have the smallest sum, whereas
    # the bottom-right point will have the largest sum
    s = pts.sum(axis=1)
    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]

    # now, compute the difference between the points, the
    # top-right point will have the smallest difference,
    # whereas the bottom-left will have the largest difference
    diff = np.diff(pts, axis=1)
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    # return the ordered coordinates
    return rect


def four_point_transform(image, pts):
    # obtain a consistent order of the points and unpack them
    # individually
    rect = order_points(pts)
    (tl, tr, br, bl) = rect

    # compute the width of the new image, which will be the
    # maximum distance between bottom-right and bottom-left
    # x-coordiates or the top-right and top-left x-coordinates
    widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    maxWidth = max(int(widthA), int(widthB))

    # compute the height of the new image, which will be the
    # maximum distance between the top-right and bottom-right
    # y-coordinates or the top-left and bottom-left y-coordinates
    heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    maxHeight = max(int(heightA), int(heightB))

    # now that we have the dimensions of the new image, construct
    # the set of destination points to obtain a "birds eye view",
    # (i.e. top-down view) of the image, again specifying points
    # in the top-left, top-right, bottom-right, and bottom-left
    # order
    dst = np.array([
        [0, 0],
        [maxWidth - 1, 0],
        [maxWidth - 1, maxHeight - 1],
        [0, maxHeight - 1]], dtype="float32")

    # compute the perspective transform matrix and then apply it
    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))
    n_size = min(warped.shape[:2])
    warped = cv2.resize(warped, (n_size, n_size), interpolation=cv2.INTER_AREA)
    # return the warped image
    return warped


def remove_noise(img):
    """Remove noise from bw image"""
    inter = cv2.morphologyEx(img, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))

    # Find largest contour in intermediate image
    cnts, _ = cv2.findContours(inter, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cnt = max(cnts, key=cv2.contourArea)

    # Output
    out = np.zeros(img.shape, np.uint8)
    cv2.drawContours(out, [cnt], -1, 255, cv2.FILLED)
    return cv2.bitwise_and(img, out)


def decode_pieces(main_square, pieces_names):
    """Go through every code icon and try to determine its name
        returns detected char code"""
    tiles = []
    N, M = int(1.3 * main_square.shape[1] // 4), int(1.3 * main_square.shape[0] // 4)

    for y in range(0, main_square.shape[1], N):
        y_offset = int(y * 0.7)
        for x in range(0, main_square.shape[0], M):
            x_offset = int(x * 0.7)
            tile = main_square[x_offset:x_offset + M, y_offset:y_offset + N]
            tile = cv2.cvtColor(tile, cv2.COLOR_BGR2GRAY)
            tile = cv2.threshold(tile, 100, 255, cv2.THRESH_BINARY | cv2.THRESH_TRIANGLE)[1]
            tile_o = get_best_match(tile, area_t=(tile.shape[0] * 0.2) ** 2, border_threshold=True, is_gray=True,
                                    center_score=False)
            if tile_o:
                x_n, y_n, w_n, h_n = cv2.boundingRect(tile_o['object'])
                tile = tile[y_n:y_n + h_n, x_n:x_n + w_n]

            tile = cv2.resize(tile, (160 - 12 * 2, 160 - 12 * 2), interpolation=cv2.INTER_AREA)  # piece size - border
            tile_o = np.zeros((160, 160), np.uint8)
            tile_o[12:148, 12:148] = tile
            tile_o = remove_noise(tile_o)
            tiles.append(tile_o)

    bw_path = os.path.join(STYLES_PATH_FULL.format(STYLE_NAME), 'pieces/bw/')
    pieces = [{'img': cv2.imread(bw_path + p + '.png', 0), 'name': p} for p in pieces_names.keys()]

    codes = []
    for tile in tiles:
        stats = {}
        for piece in pieces:
            stats[piece['name']] = cv2.matchTemplate(tile, piece['img'], cv2.TM_CCOEFF_NORMED).max()
        stats = list(sorted(stats.items(), key=lambda item: -item[1]))
        codes.append(pieces_names[stats[0][0]])
    out_code = ''
    for i in range(4):
        for j in range(0, 16, 4):
            out_code += codes[i + j]
    return out_code


def cv_detector(img_orig, style_module):
    """Returns decoded char code"""
    global STYLE_NAME

    STYLE_NAME = style_module['style-info']['name']
    top_match = get_best_match(img_orig, area_t=0.01)
    x, y, w, h = cv2.boundingRect(top_match['object'])
    top_match = img_orig[y:y + h, x:x + w]

    trapeze = get_trapeze_contour(top_match)
    square = four_point_transform(top_match, trapeze.reshape(4, 2))

    square_no_border = get_best_match(square, area_t=0.6, border_threshold=True)

    if square_no_border:
        x, y, w, h = cv2.boundingRect(square_no_border['object'])
        x, y = int(x * 0.9), int(y * 0.9)
        w, h = int(w * 1.4), int(h * 1.4)
        square = square[y:y + h, x:x + w]
    square = change_brightness(square, value=40)  # increases
    # cv2.imshow('image', square)
    # cv2.waitKey(0)
    return decode_pieces(square, style_module['name_to_key'])


if __name__ == '__main__':
    code = cv_detector(cv2.imread(
        'C:\\Users\\maxfyk\\Downloads\\x-test-2.jpg'))  # C:\\Users\\maxfyk\\Downloads\\photo_2022-08-15_12-32-03.jpg
