# returns a new filename with extension and added word of choice
import numpy as np
import cv2
import dlib

detector = dlib.get_frontal_face_detector()
PREDICTOR_PATH = "shape_predictor_68_face_landmarks.dat"
predictor = dlib.shape_predictor(PREDICTOR_PATH)

def prepend_extension(path, ext, word):
    return ".".join(path.split(".")[:-1]) + word + ext

def add_margin_to_image(img, factor=1):
    w, h, a = img.shape
    leftright_margin = int(w*factor)
    topbottom_margin = int(h*factor)
    canvas = np.ones((w + ( 2 *  leftright_margin ) , h + ( 2 *  topbottom_margin ), a), dtype=img.dtype)*255
    canvas[leftright_margin:leftright_margin+w, topbottom_margin:topbottom_margin+h] = img
    return canvas

def has_faces(img):
    rects = detector(img)
    if len(rects) > 0: return True
    else: return False

def get_rects(img):
    return detector(img)

def draw_rects_and_save(_img, rects, out_path):
    img = _img.copy()
    for rect in rects:
        x, y, h, w = rect.left(), rect.top(), rect.width(), rect.height()
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 10)
    cv2.imwrite(out_path, img)

def cut_rect_with_margin_and_save_and_return_rect(img, rect, out_path, margin_factor=0):
    x, y, h, w = rect.left(), rect.top(), rect.width(), rect.height()
    x = int(x - margin_factor*w)
    y = int(y - margin_factor*h)
    w = int(w + 2*(margin_factor*w))
    h = int(h + 2*(margin_factor*h))
    crop_img = img[y:y+h,x:x+w]
    cv2.imwrite(out_path, crop_img)
    return {"x": x, "y": y, "w": w, "h": h}

def align_size(src_img, img):
    return cv2.resize(img, (src_img.shape[0], src_img.shape[1]))

def get_landmarks(img):
    rect = get_rects(img)[0]
    return np.matrix([[p.x, p.y] for p in predictor(img, rect).parts()])

def draw_landmarks_and_save(_img, landmarks, out_path):
    img = _img.copy()
    for point in landmarks:
        pos = (point[0, 0], point[0, 1])
        cv2.circle(img,pos, 1, (0,0,255), -1)
    cv2.imwrite(out_path, img)

def save_landmarks_to_text(landmarks, out_path):
    writer = open(out_path, 'w')
    for i in landmarks:
        writer.write(str(i[0,0]) + " "+ str(i[0, 1]) + "\n")    
    writer.close();


def create_and_save_triangle_info(_img, landmarks, out_path):
    img = _img
    size = img.shape
    rect = (0,0,size[1], size[0])

    subdiv = cv2.Subdiv2D(rect)

    points = []
    points_dict = {}

    for i, line in enumerate(landmarks, 0):
        x,y = line.split()
        points.append( ( int(x), int(y) ) )
        points_dict[ ( int(x), int(y) ) ] = i
    
    for p in points:
        subdiv.insert(p)

    triangle_list = subdiv.getTriangleList()
    writer = open(out_path, "w")
    for t in triangle_list:
	print t
        pt1 = (int(t[0]), int(t[1]))
        pt2 = (int(t[2]), int(t[3]))
        pt3 = (int(t[4]), int(t[5]))

        try:
            writer.write(str(points_dict[pt1]) + " " + str(points_dict[pt2]) + " " + str(points_dict[pt3]) + "\n")
        except: KeyError

    writer.close()

def draw_triangles_and_landmarks_and_save(_img, landmarks, triangles, out_path):
    img = _img
    points_dict = {}
    for i, line in enumerate(landmarks, 0):
        points_dict[i] = (line.split()[0], line.split()[1])
    for line in triangles:
        pt1, pt2, pt3 = line.split()
        pt1 = ( int(points_dict[int(pt1)][0]), int( points_dict[int(pt1)][1] ) )
        pt2 = ( int(points_dict[int(pt2)][0]), int( points_dict[int(pt2)][1] ) )
        pt3 = ( int(points_dict[int(pt3)][0]), int( points_dict[int(pt3)][1] ) )

        cv2.line(img, pt1, pt2, (255,255,255), 1, cv2.CV_AA, 0)
        cv2.line(img, pt2, pt3, (255,255,255), 1, cv2.CV_AA, 0)
        cv2.line(img, pt3, pt1, (255,255,255), 1, cv2.CV_AA, 0)

    for point in landmarks:
        x, y = point.split()
        pos = (int(x), int(y))
        cv2.circle(img,pos, 1, (0,0,255), -1)
    cv2.imwrite(out_path, img)

def process_landmarks_to_tuple_list(landmarks):
    points = list()
    for line in landmarks:
        x, y = line.split()
        points.append( (int(x), int(y)) )
    return points

# Apply affine transform calculated using srcTri and dstTri to src and
# output an image of size.
def applyAffineTransform(src, srcTri, dstTri, size) :
    
    # Given a pair of triangles, find the affine transform.
    warpMat = cv2.getAffineTransform( np.float32(srcTri), np.float32(dstTri) )
    
    # Apply the Affine Transform just found to the src image
    dst = cv2.warpAffine( src, warpMat, (size[0], size[1]), None, flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT_101 )

    return dst

def morph_triangle(src_img, canvas, src_t, dst_t):
    src_bound = cv2.boundingRect(np.float32([src_t]))
    dst_bound = cv2.boundingRect(np.float32([dst_t]))

    src_rect = list()
    dst_rect = list()

    for i in xrange(0, 3):
        src_rect.append( ( (src_t[i][0] - src_bound[0] ), ( src_t[i][1] - src_bound[1] ) ) )
        dst_rect.append( ( (dst_t[i][0] - dst_bound[0] ), ( dst_t[i][1] - dst_bound[1] ) ) )
    mask = np.zeros((dst_bound[3], dst_bound[2], 3), dtype = np.float32)
    cv2.fillConvexPoly(mask, np.int32(dst_rect), (1.0,1.0,1.0), 16, 0 )
    #  cv2.imshow("ds", mask)
    
    src_img_rect = src_img[ src_bound[1]:src_bound[1] + src_bound[3], src_bound[0]:src_bound[0] + src_bound[2] ] 

    size = ( dst_bound[2], dst_bound[3] )
    warp_src = applyAffineTransform( src_img_rect, src_rect, dst_rect, size )
    imgRect = (1.0 - 0.5) * warp_src + 0.5 * warp_src

    canvas[ dst_bound[1]:dst_bound[1] + dst_bound[3], dst_bound[0]:dst_bound[0]+dst_bound[2] ] = canvas[ dst_bound[1]:dst_bound[1] + dst_bound[3], dst_bound[0]:dst_bound[0] + dst_bound[2] ] * (1-mask) + warp_src * mask
    

def morph(_src_img, src_landmarks, dst_landmarks, dst_triangles, _dst_img):
    src_img = np.float32(_src_img)
    src_points = process_landmarks_to_tuple_list(src_landmarks) 
    dst_points = process_landmarks_to_tuple_list(dst_landmarks)
    
    canvas = np.zeros( _dst_img.shape, dtype = _dst_img.dtype )
    #  anvas = src_img.copy()
    mask2 = np.zeros( ( _dst_img.shape[0], _dst_img.shape[1], 3 ), dtype = np.float32 )
    for line in dst_triangles:
        x,y,z = line.split()
        x = int(x)
        y = int(y)
        z = int(z)
        
        cv2.fillConvexPoly(mask2, np.int32([ dst_points[x], dst_points[y], dst_points[z] ]), (1.0,1.0,1.0), 16, 0 )

        src_t = [ src_points[x], src_points[y], src_points[z] ]
        dst_t = [ dst_points[x], dst_points[y], dst_points[z] ]
        
        morph_triangle(src_img, canvas, src_t, dst_t)

        #  cv2.imshow("ds", np.uint8(canvas))
        #  cv2.waitKey(0)
    img = _dst_img.copy()
    img = img * (1-mask2) + canvas * mask2
    #  cv2.imshow('sda', np.uint8(img))
    #  cv2.waitKey(0)
    return np.uint8(img)
    
