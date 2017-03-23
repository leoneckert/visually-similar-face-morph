import cv2
import numpy as np
import tools as t
import sys, os, time, shutil
from pprint import pprint
from subprocess import call
import visually_similar as vs

path = sys.argv[1]

# get uplaoded folder and move it into timestamped directory
ts = int(time.time())

# create public and local dirs
project_path = os.path.join("local/images", str(ts))
public_project_path = os.path.join("static/images", str(ts))

if not os.path.isdir(project_path):
    os.makedirs(project_path)
if not os.path.isdir(public_project_path):
    os.makedirs(public_project_path)

#  this dict will collect ALL the paths of the project:
all_paths = {}

# copy the input image into the local project folder:
path_local_original = os.path.join(project_path, "original.jpg")
shutil.copy(path, path_local_original)

all_paths["local_original"] = path_local_original

# resize image to uniform size 
max_width = max_height = 2500

path_local_original_resized = t.prepend_extension(path_local_original, '.jpg', ".resized")
call(['ffmpeg', '-i', path_local_original, '-vf', 'scale=w='+str(max_width)+':h='+str(max_height)+':force_original_aspect_ratio=decrease', path_local_original_resized])

all_paths["local_original_resized"] = path_local_original_resized

# add margin in case faces are on the edge of the images
resized = cv2.imread(path_local_original_resized)
margin = t.add_margin_to_image(resized, factor=0.5)
path_local_original_resized_margin = t.prepend_extension(path_local_original_resized, ".jpg", ".with_margin")
cv2.imwrite(path_local_original_resized_margin, margin)

all_paths["local_original_resized_margin"] = path_local_original_resized_margin

# check Point!
# check if it contains faces
if not(t.has_faces(margin)):
    print "[-] No faces found in original. Exiting"
    sys.exit()

# detect faces and cut out 2 version
rects = t.get_rects(margin)

# draw rectangles onto face on 
path_local_original_resized_margin_with_rects = t.prepend_extension(path_local_original_resized_margin, '.jpg', ".with_rects")
t.draw_rects_and_save(margin, rects, path_local_original_resized_margin_with_rects)

all_paths["local_original_margin_with_rects"] = path_local_original_resized_margin_with_rects


found_faces = list()
for i, rect in enumerate(rects, 0):
    #  path_public_original_face_no_frame = t.prepend_extension(path_margin, ".jpg", ".face_no_frame_" + str(i))
    #  path_local_original_face_with_frame = t.prepend_extension(path_margin, ".jpg", ".face_with_frame_" + str(i))
    path_public_original_face_no_frame = os.path.join(public_project_path, "original_face_"+str(i)+"_no_frame.jpg")
    path_local_original_face_with_frame = os.path.join(project_path, "original_face_"+str(i)+"_with_frame.jpg") 
    
    rect_no_frame = t.cut_rect_with_margin_and_save_and_return_rect(margin, rect, path_public_original_face_no_frame)
    rect_with_frame = t.cut_rect_with_margin_and_save_and_return_rect(margin, rect, path_local_original_face_with_frame, margin_factor=0.25)
    
    temp = {}
    temp["public_original_face_no_frame"] = path_public_original_face_no_frame
    temp["public_original_face_no_frame_rect"] = rect_no_frame
    temp["local_original_face_with_frame"] = path_local_original_face_with_frame
    temp["local_original_face_with_frame_rect"] = rect_with_frame
    #  found_faces.append( {"rect_no_frame": rect_no_frame, "rect_with_frame": rect_with_frame, "no_frame": path_face_no_frame, "with_frame": path_face_with_frame} )
    found_faces.append( temp )


# now find visually similar faces with the no_frame images and save them;
#  for i, face in enumerate(found_faces, 0):
#      path_for_similar = os.path.join(project_path, "face_"+str(i)+"_similar_original.jpg")
#      path_for_downloads = os.path.join(project_path, "face_"+str(i)+"_similar_downloads")
#      rect_no_frame = face["no_frame"]
#      print rect_no_frame, "<<<"
#      if vs.download_vs_image(rect_no_frame, path_for_downloads, path_for_similar):
#          face["similar_original"] = path_for_similar
#      else:
#
#          print "didnt find simliar for", rect_no_frame
#          sys.exit()

for i, face in enumerate(found_faces, 0):
    path_public_no_frame = face["public_original_face_no_frame"]
    links = vs.get_vs_links(path_public_no_frame)
    print "GOT THESE LINKS:", links
    face["local_simnilar_links"] = links
    if len(links) == 0:
        print "NO links, continuing in case there are more faces"
        continue

    path_local_similar_testground = os.path.join(project_path, "similar_downloads")
    if not os.path.isdir(path_local_similar_testground):
        os.makedirs(path_local_similar_testground)


    test_count = -1
    face["downloads"] = list()
    while True:
        test_count += 1
        if len(links) == 0:
            print "tried all links, nothing found"
            sys.exit()
        pick = links[-1]
        links = links[:-1]
        
        path_similar_face = os.path.join(path_local_similar_testground, "similar_"+str(test_count)+".jpg")
        vs.download_file(pick, path_similar_face)
        
        similar_img = cv2.imread(path_similar_face)
        similar_img_margin = t.add_margin_to_image(similar_img, factor=0.5)
        
        rects = t.get_rects(similar_img_margin)
        if len(rects) == 0:
            print "no faces found in this similar image, on to the next"
            continue
        rect = rects[0]
        
        #  only track images with a face
        face["downloads"].append(path_similar_face)
        
        path_similar_face_margin = t.prepend_extension(path_similar_face, '.jpg', '.margin')
        cv2.imwrite(path_similar_face_margin, similar_img_margin)
        face["downloads"].append(path_similar_face_margin)

        path_similar_face_margin_with_frame = t.prepend_extension(path_similar_face_margin, '.jpg', '.with_frame')
        t.cut_rect_with_margin_and_save_and_return_rect(similar_img_margin, rect, path_similar_face_margin_with_frame)
        face["downloads"].append(path_similar_face_margin_with_frame)
        
        pprint(found_faces)
        sys.exit()



# save the similar images with margin
#  for i, face in enumerate(found_faces, 0):
#      path_similar = face["similar_original"]
#      similar = cv2.imread(path_similar)
#      similar_margin = t.add_margin_to_image(similar, factor=0.5)
#      path_similar_margin = t.prepend_extension(path_similar, ".jpg", ".with_margin")
#      cv2.imwrite(path_similar_margin, similar_margin)
#      face["similar_with_margin"] = path_similar_margin

# for each similar images, detect the first best face, draw it, cut with frame and save it.
#  for i, face in enumerate(found_faces, 0):
#      path_similar_margin = face["similar_with_margin"]
#      similar_margin = cv2.imread(path_similar_margin)
#      rect = t.get_rects(similar_margin)[0]
#
#      path_similar_margin_with_rects = t.prepend_extension(path_similar_margin, '.jpg', ".with_rects")
#      t.draw_rects_and_save(similar_margin, [rect], path_similar_margin_with_rects)
#
#      path_face_with_frame = t.prepend_extension(path_similar_margin, ".jpg", ".face_with_frame_" + str(i))
#      t.cut_rect_with_margin_and_save_and_return_rect(similar_margin, rect, path_face_with_frame, margin_factor=0.25)
#
#      face["similar_with_frame"] = path_face_with_frame


# resize the similar_with_frame to match the size of with_frame
#  for i, face in enumerate(found_faces, 0):
#      img = cv2.imread(face["with_frame"])
#      similar = cv2.imread(face["similar_with_frame"])
#      similar_resized = t.align_size(img, similar)
#      path_similar_resized = t.prepend_extension( face["similar_with_frame"], ".jpg", ".resized" )
#      cv2.imwrite(path_similar_resized, similar_resized)
#
#      face["similar_resized"] = path_similar_resized


# for each face find landmarks, draw them, then save them to a text file
#  for i, face in enumerate(found_faces, 0):
#      img = cv2.imread(face["with_frame"])
#      similar = cv2.imread(face["similar_resized"])
#
#      img_landmarks = t.get_landmarks(img)
#      similar_landmarks = t.get_landmarks(similar)
#
#      path_img_landmarks = t.prepend_extension(face["with_frame"], ".jpg", ".with_landmarks")
#      t.draw_landmarks_and_save(img, img_landmarks, path_img_landmarks)
#      path_similar_landmarks = t.prepend_extension(face["similar_resized"], ".jpg", ".with_landmarks")
#      t.draw_landmarks_and_save(similar, similar_landmarks, path_similar_landmarks)
#
#      path_img_landmarks_txt = t.prepend_extension(face["with_frame"], ".txt", ".landmarks")
#      path_similar_landmarks_txt = t.prepend_extension(face["similar_resized"], ".txt", ".landmarks")
#
#      t.save_landmarks_to_text(img_landmarks, path_img_landmarks_txt)
#      t.save_landmarks_to_text(similar_landmarks, path_similar_landmarks_txt)
#
#      face["similar_landmarks"] = path_similar_landmarks_txt
#      face["landmarks"] = path_img_landmarks_txt


# create the triangle txt file for the 'destination' faces aka the faces from the original image
for i, face in enumerate(found_faces, 0):
    img = cv2.imread(face["with_frame"])  
    landmarks = open(face["landmarks"]).read().splitlines()
    path_img_triangles_txt = t.prepend_extension(face["with_frame"], ".txt", ".triangles")

    t.create_and_save_triangle_info(img, landmarks, path_img_triangles_txt)

    triangles = open(path_img_triangles_txt).read().splitlines()
    path_img_triangles_and_landmarks = t.prepend_extension(face["with_frame"], ".jpg", ".triangles_and_landmarks")
    t.draw_triangles_and_landmarks_and_save(img, landmarks, triangles, path_img_triangles_and_landmarks)

    face["triangles"] = path_img_triangles_txt



orig = cv2.imread(path_margin)
new = orig.copy()

# morphtime
for i, face in enumerate(found_faces, 0):
    img = cv2.imread(face["with_frame"])  
    similar = cv2.imread(face["similar_resized"])
    similar_landmarks = open(face["similar_landmarks"]).read().splitlines()
    img_landmarks = open(face["landmarks"]).read().splitlines()
    triangles = open(face["triangles"]).read().splitlines()
    
    r = face["rect_with_frame"]
    
    new = t.morph(similar, similar_landmarks, img_landmarks, triangles, img, new, r )
    
to_cut_x = int((new.shape[0] - resized.shape[0]) * 0.5)
to_cut_y = int((new.shape[1] - resized.shape[1]) * 0.5)
new = new[ to_cut_x:to_cut_x + resized.shape[0] , to_cut_y: to_cut_y + resized.shape[1] ]

path_to_output = os.path.join(project_path, "output.jpg")
cv2.imwrite(path_to_output, new)


