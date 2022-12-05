import cv2
import numpy as np
import serial


def main():
    camera = cv2.VideoCapture(1)
    ret, image = camera.read()
    rr = 0   # +-mergin

    Serial port setting
    ser = serial.Serial("COM7", 9600)
    print(ser)

    h_min, s_min, v_min = (0, 0, 0)
    h_max, s_max, v_max = (0, 0, 0)

    while True:
        ret, image = camera.read()
        frame_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        if cv2.waitKey(10) & 0xFF is ord('c'):   # press 'c' to select new color
            roi = cv2.selectROI('Original', image, False)
            imCrop = image[int(roi[1]):int(roi[1] + roi[3]), int(roi[0]):int(roi[0] + roi[2])]
            hsv = cv2.cvtColor(imCrop, cv2.COLOR_BGR2HSV)
            # Split color
            h, s, v = cv2.split(hsv)
            # Get range of color
            h_min, s_min, v_min = int(np.min(h) + rr), int(np.min(s) + rr), int(np.min(v) + rr)
            h_max, s_max, v_max = int(np.max(h) - rr), int(np.max(s) - rr), int(np.max(v) - rr)

        thresh_HSV = cv2.inRange(frame_HSV, (h_min, s_min, v_min), (h_max, s_max, v_max))
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.morphologyEx(thresh_HSV, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
        cv2.drawContours(image, cnts, -1, color=(0, 0, 255), thickness=2)

        center = None
        # only proceed if at least one contour was found
        roi_area = (270, 200, 370, 300)
        
        cv2.rectangle(image, (int(roi_area[2]), int(roi_area[3])), (int(roi_area[0]), int(roi_area[1])), (0, 255, 0), 2)
      
        if len(cnts) > 0:
            c = max(cnts, key = cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))

            # only proceed if the radius meets a minimum size
            if radius > 2:   # r>2 pixel
                # draw the circle and centroid on the frame,
                # then update the list of tracked points
                cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
                cv2.circle(image, center, 3, (0, 255, 255), -1)
                cv2.putText(image, "centroid", (center[0] + 10, center[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 0), 1)
                cv2.putText(image, "(" + str(center[0]) + "," + str(center[1]) + ")", (center[0] + 10, center[1] + 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
                
                x = center[0]
                y = center[1]
                if((270 < x < 370) and (200 < y < 300)):
                    print("center(x,y), radius=", center, ",", radius)
                    print("Go!")
                    send serial data
                    ser.write(b"@")
                    print(ser.readline())

        else:
            print("no color")

        # show the frame to our screen
        cv2.imshow("Original", image)

        if cv2.waitKey(1) & 0xFF is ord('q'):
            ser.close()
            break

    # print again
    print("#min of H,S,V:", h_min, s_min, v_min)   # min of H,S,V
    print("#max of H,S,V:", h_max, s_max, v_max)   # max of H,S,V

if __name__ == '__main__':
    main()
