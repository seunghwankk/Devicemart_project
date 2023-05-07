# python3 detect_main.py --weights img256.pt --source 0
# sudo chmod a+rw /dev/ttyACM0

import argparse
import os
import platform
import sys
from pathlib import Path
import torch

FILE = Path(__file__).resolve()
ROOT = FILE.parents[0]  # YOLOv5 root directory
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))  # add ROOT to PATH
ROOT = Path(os.path.relpath(ROOT, Path.cwd()))  # relative

from models.common import DetectMultiBackend
from utils.dataloaders import IMG_FORMATS, VID_FORMATS, LoadImages, LoadScreenshots, LoadStreams
from utils.general import (LOGGER, Profile, check_file, check_img_size, check_imshow, check_requirements, colorstr, cv2,
                           increment_path, non_max_suppression, print_args, scale_boxes, strip_optimizer, xyxy2xywh)
from utils.plots import Annotator, colors, save_one_box
from utils.torch_utils import select_device, smart_inference_mode

import serial#<<pip install pyserial로 설치
import time
import socket

HOST = '10.10.141.186'
PORT = 5000

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)# 소켓 객체를 생성합니다.
client_socket.connect((HOST, PORT))# 지정한 HOST와 PORT를 사용하여 서버에 접속

# 시리얼 포트와 baud rate 지정
ser = serial.Serial('/dev/ttyACM0', 9600) # 컴퓨터와 통신 시험 시 'COM4'
time.sleep(2)  # 접속 대기


@smart_inference_mode()
def run(
        weights=ROOT / 'yolov5s.pt',  # model path or triton URL
        source=ROOT / 'data/images',  # file/dir/URL/glob/screen/0(webcam)
        data=ROOT / 'data/coco128.yaml',  # dataset.yaml path
        imgsz=(640, 640),  # inference size (height, width)
        conf_thres=0.8,  # confidence threshold
        iou_thres=0.8,  # NMS IOU threshold
        max_det=1000,  # maximum detections per image
        device='',  # cuda device, i.e. 0 or 0,1,2,3 or cpu
        view_img=False,  # show results
        save_txt=False,  # save results to *.txt
        save_conf=False,  # save confidences in --save-txt labels
        save_crop=False,  # save cropped prediction boxes
        nosave=False,  # do not save images/videos
        classes=None,  # filter by class: --class 0, or --class 0 2 3
        agnostic_nms=False,  # class-agnostic NMS0
        augment=False,  # augmented inference
        visualize=False,  # visualize features
        update=False,  # update all models
        project=ROOT / 'runs/detect',  # save results to project/name
        name='exp',  # save results to project/name
        exist_ok=False,  # existing project/name ok, do not increment
        line_thickness=3,  # bounding box thickness (pixels)
        hide_labels=False,  # hide labels
        hide_conf=False,  # hide confidences
        half=False,  # use FP16 half-precision inference
        dnn=False,  # use OpenCV DNN for ONNX inference
        vid_stride=1,  # video frame-rate stride
):
    source = str(source)
    save_img = not nosave and not source.endswith('.txt')  # save inference images
    is_file = Path(source).suffix[1:] in (IMG_FORMATS + VID_FORMATS)
    is_url = source.lower().startswith(('rtsp://', 'rtmp://', 'http://', 'https://'))
    webcam = source.isnumeric() or source.endswith('.streams') or (is_url and not is_file)
    screenshot = source.lower().startswith('screen')

    # 디렉토리
    save_dir = increment_path(Path(project) / name, exist_ok=exist_ok)  # increment run
    (save_dir / 'labels' if save_txt else save_dir).mkdir(parents=True, exist_ok=True)  # make dir

    # 하중 모델
    device = select_device(device)
    model = DetectMultiBackend(weights, device=device, dnn=dnn, data=data, fp16=half)
    stride, names, pt = model.stride, model.names, model.pt
    imgsz = check_img_size(imgsz, s=stride)  # check image size

    # 데이터 로더
    bs = 1  # batch_size

    view_img = check_imshow(warn=True)
    dataset = LoadStreams(source, img_size=imgsz, stride=stride, auto=pt, vid_stride=vid_stride)
    bs = len(dataset)

    # 추론 실행
    model.warmup(imgsz=(1 if pt or model.triton else bs, 3, *imgsz))  # warmup
    windows, dt = [], (Profile(), Profile(), Profile())

    read_adu = 0# 아두이노에서 받은 값 저장용 변수

    for path, im, im0s, vid_cap, s in dataset:
				 # 만약 아두이노에서 값이 들어 왔다면
        if ser.in_waiting > 0: 
						# read_adu에 값 저장
            read_adu = ser.read()  

        with dt[0]:
            im = torch.from_numpy(im).to(model.device)
            im = im.half() if model.fp16 else im.float()  # uint8 to fp16/32
            im /= 255  # 0 - 255 to 0.0 - 1.0
            if len(im.shape) == 3:
                im = im[None]  # expand for batch dim

        # Inference
        with dt[1]:
            visualize = increment_path(save_dir / Path(path).stem, mkdir=True) if visualize else False
            pred = model(im, augment=augment, visualize=visualize)

        # NMS
        with dt[2]:
            pred = non_max_suppression(pred, conf_thres, iou_thres, classes, agnostic_nms, max_det=max_det)

        # 프로세스 예측
        for i, det in enumerate(pred):  # per image

            p, im0, frame = path[i], im0s[i].copy(), dataset.count
            annotator = Annotator(im0, line_width=line_thickness, example=str(names))

            if len(det):
                #상자를 img_size에서 im0 크기로 재조정
                det[:, :4] = scale_boxes(im.shape[2:], det[:, :4], im0.shape).round()

                #결과
                for *xyxy, conf, cls in reversed(det):
                    if save_img or save_crop or view_img:  #image에 박스 처줌
                        c = int(cls)  # integer class
                        label = None if hide_labels else (names[c] if hide_conf else f'{names[c]} {conf:.2f}')
                        annotator.box_label(xyxy, label, color=colors(c, True))

                    if read_adu == b'S':  # read_adu가 'S' 라면
                        if names[int(cls)] == "person":  # 테스트용 조건문
                            ser.write(b'1')  # 아두이노로 1' 보냄
                            print("person")
                        elif names[int(cls)] == "Pterophyllum":
                            ser.write(b'1')
                            print("Pterophyllum")
                        elif names[int(cls)] == "Arapaima gigas":
                            ser.write(b'2')
                            print("Arapaima gigas")
                        elif names[int(cls)] == "ikan-mas":
                            ser.write(b'3')
                            print("ikan-mas")
                        else:
                            ser.write(b'4')
                            print("no detect")
                        print(read_adu)
                        read_adu = '0'  # read_adu를 0으로 초기화하여 한번만 인식 하도록 함

            # 화면 보여줌
            im0 = annotator.result()
            if view_img:
                if platform.system() == 'Linux' and p not in windows:
                    windows.append(p)
                    cv2.namedWindow(str(p), cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)  # allow window resize (Linux)
                    cv2.resizeWindow(str(p), im0.shape[1], im0.shape[0])
                cv2.imshow(str(p), im0)
                cv2.waitKey(1)  # 1 millisecond

        if read_adu == b'A':  # read_adu가 'A' 라면
            print("ex) Raspberry : 1++")  # 테스트 프린트
            client_socket.send(b'1') # RaspBerry로 데이터 전송
            read_adu = '0'  # read_adu를 0으로 초기화하여 한번만 인식 하도록 함
        elif read_adu == b'B':
            print("ex) Raspberry : 2++")
            client_socket.send(b'2')
            read_adu = '0'
        elif read_adu == b'C':
            print("ex) Raspberry : 3++")
            client_socket.send(b'3')
            read_adu = '0'
        elif read_adu == b'D':
            print("ex) Raspberry : 4++")
            client_socket.send(b'4')
            read_adu = '0'

def parse_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--weights', nargs='+', type=str, default=ROOT / 'yolov5s.pt', help='model path or triton URL')
    parser.add_argument('--source', type=str, default=ROOT / 'data/images', help='file/dir/URL/glob/screen/0(webcam)')
    parser.add_argument('--data', type=str, default=ROOT / 'data/coco128.yaml', help='(optional) dataset.yaml path')
    parser.add_argument('--imgsz', '--img', '--img-size', nargs='+', type=int, default=[640], help='inference size h,w')
    parser.add_argument('--conf-thres', type=float, default=0.85, help='confidence threshold')
    parser.add_argument('--iou-thres', type=float, default=0.45, help='NMS IoU threshold')
    parser.add_argument('--max-det', type=int, default=1000, help='maximum detections per image')
    parser.add_argument('--device', default='', help='cuda device, i.e. 0 or 0,1,2,3 or cpu')
    parser.add_argument('--view-img', action='store_true', help='show results')
    parser.add_argument('--save-txt', action='store_true', help='save results to *.txt')
    parser.add_argument('--save-conf', action='store_true', help='save confidences in --save-txt labels')
    parser.add_argument('--save-crop', action='store_true', help='save cropped prediction boxes')
    parser.add_argument('--nosave', action='store_true', help='do not save images/videos')
    parser.add_argument('--classes', nargs='+', type=int, help='filter by class: --classes 0, or --classes 0 2 3')
    parser.add_argument('--agnostic-nms', action='store_true', help='class-agnostic NMS')
    parser.add_argument('--augment', action='store_true', help='augmented inference')
    parser.add_argument('--visualize', action='store_true', help='visualize features')
    parser.add_argument('--update', action='store_true', help='update all models')
    parser.add_argument('--project', default=ROOT / 'runs/detect', help='save results to project/name')
    parser.add_argument('--name', default='exp', help='save results to project/name')
    parser.add_argument('--exist-ok', action='store_true', help='existing project/name ok, do not increment')
    parser.add_argument('--line-thickness', default=3, type=int, help='bounding box thickness (pixels)')
    parser.add_argument('--hide-labels', default=False, action='store_true', help='hide labels')
    parser.add_argument('--hide-conf', default=False, action='store_true', help='hide confidences')
    parser.add_argument('--half', action='store_true', help='use FP16 half-precision inference')
    parser.add_argument('--dnn', action='store_true', help='use OpenCV DNN for ONNX inference')
    parser.add_argument('--vid-stride', type=int, default=1, help='video frame-rate stride')
    opt = parser.parse_args()
    opt.imgsz *= 2 if len(opt.imgsz) == 1 else 1  # expand
    print_args(vars(opt))
    return opt
def main(opt):
    check_requirements(exclude=('tensorboard', 'thop'))
    run(**vars(opt))

if __name__ == '__main__':
    opt = parse_opt()
    main(opt)

ser.close()