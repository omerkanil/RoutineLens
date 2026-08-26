# -*- coding: utf-8 -*-
"""VisionEngine: YOLO modelleri + tek kare tespit mantığı."""
from dataclasses import dataclass

import cv2
from ultralytics import YOLO

from core.config import ISKELET_BAGLANTILARI

# Telefon tespitini zamansal sabitleme: son N karede en az M karede telefon
# görülürse "telefon var" sayılır (titremeyi azaltır).
TELEFON_PENCERE = 3
TELEFON_ESIK = 2


@dataclass
class TespitSonucu:
    """Tek kare tespit çıktısı."""
    current_state: str
    text_color: tuple
    postur_durumu: str
    postur_renk: tuple
    annotated_frame: object
    telefon_var_mi: bool
    kambur_sayac: int


class VisionEngine:
    """Çift motorlu YOLO: iskelet (pose) + telefon (object) tespiti.

    Modeller yalnızca bir kez (__init__'te) yüklenir; kare döngüsünde
    asla yeniden oluşturulmaz.
    """

    def __init__(self, pose_model_path="yolov8n-pose.pt", object_model_path="yolov8n.pt"):
        # GPU varsa CUDA kullan; yoksa CPU'ya düş. Böylece FPS düşmez.
        import torch
        self.device = 0 if torch.cuda.is_available() else "cpu"
        print(f"[INFO] YOLO cihazı: {'GPU (CUDA)' if self.device == 0 else 'CPU'}")

        self.pose_model = YOLO(pose_model_path)      # 1. Beyin: İskelet ve Postür (her kare)
        self.object_model = YOLO(object_model_path)  # 2. Beyin: Telefon Tespiti (kişi varken her kare)
        self.telefon_gecmisi = []                    # telefon tespit geçmişi (zamansal sabitleme)

    def tespit(self, frame, kambur_araliksiz_sayac):
        """Tek kare üzerinde tespit yapar; TespitSonucu döndürür."""
        # 1. BEYİN: İskelet Tespiti (her kare)
        pose_results = self.pose_model.predict(frame, conf=0.6, device=self.device, verbose=False)

        current_state = "Masada Yok (Away)"
        text_color = (0, 0, 255)
        postur_durumu = "Bilinmiyor"
        postur_renk = (255, 255, 255)

        # --- ANA KİŞİYİ SEÇ (en büyük kutu = kameraya en yakın kişi) ---
        ana_index = -1
        ana_bbox = None
        boxes_pose = pose_results[0].boxes
        if boxes_pose is not None and len(boxes_pose) > 0:
            en_buyuk_alan = -1.0
            for i in range(len(boxes_pose)):
                x1, y1, x2, y2 = boxes_pose.xyxy[i]
                alan = float((x2 - x1) * (y2 - y1))
                if alan > en_buyuk_alan:
                    en_buyuk_alan = alan
                    ana_index = i
            if ana_index >= 0:
                x1, y1, x2, y2 = boxes_pose.xyxy[ana_index]
                ana_bbox = (int(x1), int(y1), int(x2), int(y2))

        # Kutular yoksa ama keypoints varsa ilk kişiyi kullan
        if ana_index < 0 and pose_results[0].keypoints is not None and len(pose_results[0].keypoints) > 0:
            ana_index = 0

        kp_mevcut = (
            ana_index >= 0
            and pose_results[0].keypoints is not None
            and len(pose_results[0].keypoints) > ana_index
        )

        # Çerçeveyi temiz kopyala; sadece ana kişinin iskeletini çiz
        annotated_frame = frame.copy()

        if kp_mevcut:
            kp = pose_results[0].keypoints.xy[ana_index]
            kp_conf = pose_results[0].keypoints.conf[ana_index]
            for a, b in ISKELET_BAGLANTILARI:
                if float(kp_conf[a]) > 0.5 and float(kp_conf[b]) > 0.5:
                    pa = (int(kp[a][0]), int(kp[a][1]))
                    pb = (int(kp[b][0]), int(kp[b][1]))
                    cv2.line(annotated_frame, pa, pb, (0, 255, 0), 2)
            for j in range(len(kp)):
                if float(kp_conf[j]) > 0.5:
                    cv2.circle(annotated_frame, (int(kp[j][0]), int(kp[j][1])), 3, (0, 255, 0), -1)
            if ana_bbox is not None:
                cv2.rectangle(annotated_frame, (ana_bbox[0], ana_bbox[1]), (ana_bbox[2], ana_bbox[3]), (0, 255, 0), 2)

        # --- 2. BEYİN: TELEFON TESPİTİ (kişi varken her kare; en yakın kişiye atanır) ---
        # Kişi yoksa nesne modeli çalıştırılmaz (telefon ataması zaten yapılamaz).
        telefon_var_mi = False
        if ana_index >= 0:
            obj_results = self.object_model.predict(frame, conf=0.25, imgsz=960, classes=[67], device=self.device, verbose=False)
            obj_boxes = obj_results[0].boxes if obj_results else []
            for box in obj_boxes:
                tx1, ty1, tx2, ty2 = map(int, box.xyxy[0])
                cv2.rectangle(annotated_frame, (tx1, ty1), (tx2, ty2), (255, 0, 0), 2)
                cv2.putText(annotated_frame, "TELEFON", (tx1, ty1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                tcx = (tx1 + tx2) / 2
                tcy = (ty1 + ty2) / 2

                en_yakin_kisi = -1
                en_yakin_mesafe = float("inf")
                if boxes_pose is not None and len(boxes_pose) > 0:
                    for i in range(len(boxes_pose)):
                        x1, y1, x2, y2 = boxes_pose.xyxy[i]
                        kisi_cx = float((x1 + x2) / 2)
                        kisi_cy = float((y1 + y2) / 2)
                        mesafe = (tcx - kisi_cx) ** 2 + (tcy - kisi_cy) ** 2
                        if mesafe < en_yakin_mesafe:
                            en_yakin_mesafe = mesafe
                            en_yakin_kisi = i

                if en_yakin_kisi == ana_index:
                    telefon_var_mi = True

        # --- TELEFON TESPİTİNİ ZAMANSAL SABİTLE (çoğunluk oyu) ---
        self.telefon_gecmisi.append(telefon_var_mi)
        if len(self.telefon_gecmisi) > TELEFON_PENCERE:
            self.telefon_gecmisi.pop(0)
        telefon_var_mi = self.telefon_gecmisi.count(True) >= TELEFON_ESIK

        if kp_mevcut:
            keypoints_xy = pose_results[0].keypoints.xy[ana_index]
            keypoints_conf = pose_results[0].keypoints.conf[ana_index]

            if len(keypoints_xy) >= 7:
                nose_conf = keypoints_conf[0].item()
                left_eye_conf = keypoints_conf[1].item()
                right_eye_conf = keypoints_conf[2].item()

                if nose_conf > 0.5 or (left_eye_conf > 0.5 and right_eye_conf > 0.5):
                    # --- DURUM KARAR AĞACI ---
                    if telefon_var_mi:
                        current_state = "Telefonda Vakit Geciriyor"
                        text_color = (255, 0, 255)  # Mor
                        kambur_araliksiz_sayac = 0
                    else:
                        nose_y = keypoints_xy[0][1].item()
                        shoulder_mid_y = (keypoints_xy[5][1].item() + keypoints_xy[6][1].item()) / 2.0
                        vertical_distance = shoulder_mid_y - nose_y

                        if vertical_distance > 35:
                            current_state = "Calisiyor (Working)"
                            text_color = (0, 255, 0)

                            if vertical_distance < 85:
                                postur_durumu = "KAMBUR DURUYOR"
                                postur_renk = (0, 0, 255)
                                kambur_araliksiz_sayac += 1
                            else:
                                postur_durumu = "DIK / SAGLIKLI"
                                postur_renk = (0, 255, 0)
                                kambur_araliksiz_sayac = 0
                        else:
                            current_state = "Dinleniyor / Uyukluyor (Resting)"
                            text_color = (0, 255, 255)
                            kambur_araliksiz_sayac = 0
                else:
                    current_state = "Odak Kaybi / Arkasi Donuk"
                    text_color = (0, 165, 255)
                    kambur_araliksiz_sayac = 0

        return TespitSonucu(
            current_state=current_state,
            text_color=text_color,
            postur_durumu=postur_durumu,
            postur_renk=postur_renk,
            annotated_frame=annotated_frame,
            telefon_var_mi=telefon_var_mi,
            kambur_sayac=kambur_araliksiz_sayac,
        )

