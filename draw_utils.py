import cv2


font = cv2.FONT_HERSHEY_COMPLEX_SMALL

W = (255, 255, 255)
R = (0, 0, 255)
G = (0, 255, 0)
B = (255, 0, 0)


def draw_nav_string(img, img_list, idx):

    msg = "{}/{}".format(idx + 1, len(img_list))
    msg_sz, _ = cv2.getTextSize(msg, font, 1, 1)

    cv2.rectangle(img, (0, 0), (msg_sz[0], msg_sz[1] + 4), W, -1)
    cv2.putText(img, msg, (0, msg_sz[1] + 2), font, 1, B, 1)


def draw_file_path(img, file_path):

    cv2.putText(img, file_path, (5, 15), font, 0.7, W, 2)
    cv2.putText(img, file_path, (5, 15), font, 0.7, R, 1)


def draw_annot(img, name, tl, br):

    txt_sz, _ = cv2.getTextSize(name, font, 1, 1)

    cv2.rectangle(img, tl, br, R, 1)
    cv2.rectangle(img, (tl[0], tl[1] - txt_sz[1] - 4),
                  (tl[0] + txt_sz[0], tl[1]), R, -1)
    cv2.putText(img, name, (tl[0], tl[1] - 4), font, 1, W, 1)