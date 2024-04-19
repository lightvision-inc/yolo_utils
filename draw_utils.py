import cv2


font = cv2.FONT_HERSHEY_COMPLEX_SMALL

W = (255, 255, 255)
R = (0, 0, 255)
G = (0, 255, 0)
B = (255, 0, 0)
Z = (0, 0, 0)


def draw_nav_string(img, img_list, idx):
    msg = "{}/{}".format(idx + 1, len(img_list))
    msg_sz, _ = cv2.getTextSize(msg, font, 1, 1)

    cv2.rectangle(img, (0, 0), (msg_sz[0], msg_sz[1] + 4), W, -1)
    cv2.putText(img, msg, (0, msg_sz[1] + 2), font, 1, B, 1)


def draw_file_path(img, file_path):
    cv2.putText(img, file_path, (5, 15), font, 0.7, W, 2)
    cv2.putText(img, file_path, (5, 15), font, 0.7, R, 1)


def draw_annot(img, name, tl, br, draw_label=True):
    txt_sz, _ = cv2.getTextSize(name, font, 1, 1)

    cv2.rectangle(img, tl, br, R, 1)
    if draw_label:
        cv2.rectangle(img, (tl[0], tl[1] - txt_sz[1] - 4),
                      (tl[0] + txt_sz[0], tl[1]), R, -1)
        cv2.putText(img, name, (tl[0], tl[1] - 4), font, 1, W, 1)


def draw_polygon(img, polygon, name):
    for i in range(len(polygon) - 1):
        cv2.line(img, polygon[i], polygon[i + 1], R, 1)
    cv2.line(img, polygon[0], polygon[-1], R, 1)

    if name is None:
        return

    name_sz, _ = cv2.getTextSize(name, font, 1, 1)

    avg = [0, 0]
    for i in range(len(polygon)):
        avg[0] += polygon[i][0]
        avg[1] += polygon[i][1]

    avg = [int(e / len(polygon)) for e in avg]
    avg[0] -= int(name_sz[0] / 2)
    avg = tuple(avg)

    cv2.putText(img, name, avg, font, 1, W, 5)
    cv2.putText(img, name, avg, font, 1, R, 1)


def draw_crosshair(img, pt):
    cv2.line(img, (0, pt[1] - 1), (img.shape[1], pt[1] - 1), W, 1)
    cv2.line(img, (0, pt[1]), (img.shape[1], pt[1]), Z, 1)
    cv2.line(img, (0, pt[1] + 1), (img.shape[1], pt[1] + 1), W, 1)

    cv2.line(img, (pt[0] - 1, 0), (pt[0] - 1, img.shape[0]), W, 1)
    cv2.line(img, (pt[0], 0), (pt[0], img.shape[0]), Z, 1)
    cv2.line(img, (pt[0] + 1, 0), (pt[0] + 1, img.shape[0]), W, 1)
