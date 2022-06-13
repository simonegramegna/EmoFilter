import cv2
from cv2 import threshold
#this class is defined to load all the filters
#every filter is loaded and ready to use, plus the scaling,offset_x and offset_y used to set the coordinates of the filter based on the face
#insert new filters here: path,scaling,offset_x,offset_y
class Filters:
  def __init__(self):
      self.anger = [cv2.imread('filters_folder/filters_img/anger.png'),1,0,0]
      self.veryAnger = [cv2.imread('filters_folder/filters_img/veryAnger.png'),1,0,20]
      self.disgust = [cv2.imread('filters_folder/filters_img/disgust.png'),1,0,0]
      self.veryDisgust = [cv2.imread('filters_folder/filters_img/veryDisgust.png'),1,0,25]
      self.fear = [cv2.imread('filters_folder/filters_img/fear.png'),1,0,0]
      self.veryFear = [cv2.imread('filters_folder/filters_img/veryFear.png'),1,0,20]
      self.happiness = [cv2.imread('filters_folder/filters_img/happiness.png'),1,0,20]
      self.veryHappiness = [cv2.imread('filters_folder/filters_img/veryHappiness.png'),1,0,20]
      self.neutral = [cv2.imread('filters_folder/filters_img/neutral.png'),1,0,5]
      self.veryNeutral = [cv2.imread('filters_folder/filters_img/veryNeutral.png'),1,0,20]
      self.sadness = [cv2.imread('filters_folder/filters_img/sadness.png'),1,0,20]
      self.verySadness = [cv2.imread('filters_folder/filters_img/verySadness.png'),1,0,10]
      self.surprise = [cv2.imread('filters_folder/filters_img/surprise.png'),1,0,20]
      self.verySurprise = [cv2.imread('filters_folder/filters_img/verySurprise.png'),1,0,20]

class Filter:
   def __init__(self,path,offset_w,offset_y1):
       self.path = path
       self.offset_w = offset_w
       self.offset_y1 = offset_y1

