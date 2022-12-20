import numpy as np
import cv2
import face_recognition
from sklearn import neighbors
import os
import os.path
import pickle
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
i=0
def save_face(frame):
    global i
    i+=1
    # crop = frame[top:bottom, left:right]
    # cv2.rectangle(frame,(left,top),(right,bottom), (255, 0, 0), 2)
    # cv2.imwrite("file_crop{}.png".format(i),crop)
    cv2.imwrite("file{}.png".format(i),frame)
    return

def predict( X_img, knn_clf=None, distance_threshold=0.4):
    """
    Recognizes faces in given image using a trained KNN classifier

    :param image :  True if file is image, False if file is folder
    :param X_img_path: path to image to be recognized
    :param knn_clf: (optional) a knn classifier object. if not specified, model_save_path must be specified.
    :param model_path: (optional) path to a pickled knn classifier. if not specified, model_save_path must be knn_clf.
    :param distance_threshold: (optional) distance threshold for face classification. the larger it is, the more chance
           of mis-classifying an unknown person as a known one.
    :return: a list of names and face locations for the recognized faces in the image: [(name, bounding box), ...].
        For faces of unrecognized persons, the name 'unknown' will be returned.
    """

    X_face_locations = face_recognition.face_locations(X_img) #,number_of_times_to_upsample=1)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(X_img, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))] # True or False

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]

if __name__ == '__main__':

    camera = cv2.VideoCapture(0)
    # Load a trained KNN model (if one was passed in)
    with open(os.path.join(dir_path, "model","trained_knn_model.clf"), 'rb') as f:
        knn_clf = pickle.load(f)

    image_predict = 0
    predictions = ()
    fps = 0
    pre_time = time.time()
    while (True):
        ret, img = camera.read()
        fps +=1
        image_predict += 1
        if ret:
            # Chuyen gray
            # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            img_draw = img
            if image_predict >= 5:
                image_predict = 0
                predictions = predict(img, knn_clf)
                # print(predictions)

                # Print results on the console
            for name, (top, right, bottom, left) in predictions:
                # print("- Found {} at ({}, {}) ".format(name, left, top))
                # print("A face is located at pixel location Top: {}, Left: {}, Bottom: {}, Right: {}".format(top, left, bottom, right))
                img_draw = cv2.rectangle(img_draw,(left,top),(right,bottom),(0,255,0),2)
                # See if the face is a match for the known face(s)
                (text_width, text_height) = cv2.getTextSize(name, cv2.FONT_HERSHEY_SIMPLEX,1,2)[0]
                cv2.rectangle(img_draw,(left,bottom),(right,bottom + text_height + 20),(255,100,0), -1)
                cv2.putText(img_draw, name, (left + 10, bottom + text_height + 10),cv2.FONT_HERSHEY_SIMPLEX, 0.8,(0,0,255), 2, cv2.LINE_AA)

            cv2.imshow("Picture", img_draw)
        key = cv2.waitKey(1)
        if key==ord('q'):
            break
        elif key==ord('s'):
            save_face(img)

        if(time.time() - pre_time) >= 1.0:
            print("fps = {}".format(fps))
            fps = 0
            pre_time = time.time()


    camera.release()
    cv2.destroyAllWindows()
