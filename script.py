import cv2
import numpy as np
import tools as t
import sys, os, time, shutil
from pprint import pprint
from subprocess import call
import visually_similar as vs


def run_script(path):
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
    max_width = max_height = 1500

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
        #  sys.exit()
        return False

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
        rect_with_frame = t.cut_rect_with_margin_and_save_and_return_rect(margin, rect, path_local_original_face_with_frame, margin_factor=0.40)
        
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


    for i, face in enumerate(found_faces, 0):
        path_public_no_frame = face["public_original_face_no_frame"]
        links = vs.get_vs_links(path_public_no_frame)
        print "GOT THESE LINKS:", links
        face["local_similar_links"] = links
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
                #  sys.exit()
                return False
            pick = links[-1]
            links = links[:-1]
            
            path_similar_face = os.path.join(path_local_similar_testground, "face_"+str(i)+"_similar_"+str(test_count)+".jpg")
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

            #  quickly draw rect for the record. ACTUALLY LETS DO THIS AFTER RESIZING
            #  path_similar_face_margin_with_rects = t.prepend_extension(path_similar_face_margin, '.jpg', '.with_rests')
            #  t.draw_rects_and_save(similar_img_margin, [rect], path_similar_face_margin_with_rects)

            path_similar_face_margin_with_frame = t.prepend_extension(path_similar_face_margin, '.jpg', '.with_frame')
            t.cut_rect_with_margin_and_save_and_return_rect(similar_img_margin, rect, path_similar_face_margin_with_frame, margin_factor=0.40)
            face["downloads"].append(path_similar_face_margin_with_frame)

            # resize to have the same size as the original face with frame
            similar_face_with_frame = cv2.imread(path_similar_face_margin_with_frame)
            original_face_with_frame = cv2.imread(face["local_original_face_with_frame"])
            
            similar_face_resized = t.align_size(original_face_with_frame, similar_face_with_frame)
            path_similar_face_margin_with_frame_resized = t.prepend_extension(path_similar_face_margin_with_frame, '.jpg', '.resized')
            cv2.imwrite(path_similar_face_margin_with_frame_resized, similar_face_resized)
            face["downloads"].append(path_similar_face_margin_with_frame_resized)

            # check if there the face is still found:
            new_rects = t.get_rects(similar_face_resized)

            # still figuering out if I need one more test here if new rects are found etc.
            print "NEW RECTS"
            print len(new_rects)
            for r in new_rects:
                print r
            #  [(22, 50) (280, 308)]



            if len(new_rects) == 0:
                print "seems like after resizing, no face was found anymore"
                continue
            
            # seems like this is the face we are going for
            path_selected_similar = os.path.join(project_path, "selected_similar_face_resized_"+str(i)+".jpg")
            cv2.imwrite(path_selected_similar, similar_face_resized)
            face["selected_similar_face"] = path_selected_similar


            # also draw with rect:
            path_selected_similar_with_rects = t.prepend_extension(path_selected_similar, ".jpg", ".with_rect")
            t.draw_rects_and_save(similar_face_resized, [new_rects[0]], path_selected_similar_with_rects)
            face["selected_similar_face_with_rects"] = path_selected_similar_with_rects

            img_landmarks = t.get_landmarks(original_face_with_frame)
            similar_landmarks = t.get_landmarks(similar_face_resized)
            
            path_img_with_landmarks = t.prepend_extension(face["local_original_face_with_frame"], '.jpg', '.with_landmarks')
            t.draw_landmarks_and_save(original_face_with_frame, img_landmarks, path_img_with_landmarks)
            face["local_original_face_with_frame_with_landmarks"] = path_img_with_landmarks

            path_selected_similar_with_landmarks = t.prepend_extension(path_selected_similar, '.jpg', '.with_landmarks')
            t.draw_landmarks_and_save(similar_face_resized, similar_landmarks, path_selected_similar_with_landmarks)
            face["selected_similar_face_with_landmarks"] = path_selected_similar_with_landmarks

            path_img_landmarks_text = t.prepend_extension(face["local_original_face_with_frame"], '.txt', '.landmarks')
            path_similar_landmarks_text = t.prepend_extension(path_selected_similar, '.txt', '.landmarks')
            face["original_face_landmarks"] = path_img_landmarks_text
            face["selected_similar_face_landmarks"] = path_similar_landmarks_text

            t.save_landmarks_to_text(img_landmarks, path_img_landmarks_text)
            t.save_landmarks_to_text(similar_landmarks, path_similar_landmarks_text)
            

            print "dont with this while loop, on to the next"
            break
        





    # create the triangle txt file for the 'destination' faces aka the faces from the original image
    for i, face in enumerate(found_faces, 0):
        if len(face["local_similar_links"]) == 0: continue
        img = cv2.imread(face["local_original_face_with_frame"])  
        landmarks = open(face["original_face_landmarks"]).read().splitlines()
        path_img_triangles_txt = t.prepend_extension(face["local_original_face_with_frame"], ".txt", ".triangles")

        t.create_and_save_triangle_info(img, landmarks, path_img_triangles_txt)
        face["original_face_triangles"] = path_img_triangles_txt

        triangles = open(path_img_triangles_txt).read().splitlines()
        path_img_triangles_and_landmarks = t.prepend_extension(face["local_original_face_with_frame"], ".jpg", ".triangles_and_landmarks")
        t.draw_triangles_and_landmarks_and_save(img, landmarks, triangles, path_img_triangles_and_landmarks)

        face["original_face_with_triangles_and_landmarks"] = path_img_triangles_and_landmarks
        
        original_with_margin_and_landmarks = cv2.imread(all_paths["local_original_resized_margin"])    
        rectangle = face["local_original_face_with_frame_rect"]
        original_face_with_landmarks = cv2.imread(path_img_triangles_and_landmarks)
        original_with_margin_and_landmarks[rectangle["y"]:rectangle["y"]+rectangle["h"], rectangle["x"]:rectangle["x"] + rectangle["w"]] = original_face_with_landmarks
        path_original_margin_with_landmarks_in_one_face = t.prepend_extension(path_img_triangles_and_landmarks, '.jpg', '.on_original')
        cv2.imwrite(path_original_margin_with_landmarks_in_one_face, original_with_margin_and_landmarks)

        face["original_face_with_triangles_on_full_image"] = path_original_margin_with_landmarks_in_one_face


    orig = cv2.imread(all_paths["local_original_resized_margin"])
    new = orig.copy()
    new2 = orig.copy()

    # morphtime
    for i, face in enumerate(found_faces, 0):
        if len(face["local_similar_links"]) == 0: continue

        img = cv2.imread(face["local_original_face_with_frame"])  
        similar = cv2.imread(face["selected_similar_face"])
        similar_landmarks = open(face["selected_similar_face_landmarks"]).read().splitlines()
        img_landmarks = open(face["original_face_landmarks"]).read().splitlines()
        triangles = open(face["original_face_triangles"]).read().splitlines()
        
        r = face["local_original_face_with_frame_rect"]
        
        new, new2 = t.morph(similar, similar_landmarks, img_landmarks, triangles, img, new, r , new2, cv2.imread(face["original_face_with_triangles_and_landmarks"]) )
        
    to_cut_x = int((new.shape[0] - resized.shape[0]) * 0.5)
    to_cut_y = int((new.shape[1] - resized.shape[1]) * 0.5)
    new_faces = new[ to_cut_x:to_cut_x + resized.shape[0] , to_cut_y: to_cut_y + resized.shape[1] ]
    with_triangles = new2[ to_cut_x:to_cut_x + resized.shape[0] , to_cut_y: to_cut_y + resized.shape[1] ]
    clean = orig[ to_cut_x:to_cut_x + resized.shape[0] , to_cut_y: to_cut_y + resized.shape[1] ]


    path_to_output = os.path.join(project_path, "output1.jpg")
    cv2.imwrite(path_to_output, new_faces)
    path_to_output = os.path.join(public_project_path, "output1.jpg")
    cv2.imwrite(path_to_output, new_faces)

    path_to_output = os.path.join(project_path, "output2.jpg")
    cv2.imwrite(path_to_output, with_triangles)
    path_to_output = os.path.join(public_project_path, "output2.jpg")
    cv2.imwrite(path_to_output, with_triangles)

    path_to_output = os.path.join(project_path, "output3.jpg")
    cv2.imwrite(path_to_output, clean)
    path_to_output = os.path.join(public_project_path, "output3.jpg")
    cv2.imwrite(path_to_output, clean)
    
    import imageio
    path_to_output = os.path.join(public_project_path, "output.gif")
    imageio.mimsave(path_to_output, [ clean, with_triangles, new_faces  ])
    
    #  pprint(found_faces)
    return public_project_path

if __name__ == "__main__":
    path = sys.argv[1]
    output = run_script(path)
    print "DONE and putput =", output








