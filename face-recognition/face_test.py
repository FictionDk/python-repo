from core import FaceAccredit
import face_utils

def face_init(face_name):
    filepath = face_utils.get_assert_path(face_name + '.png')
    img = face_utils.read_image_from_file(filepath)
    img = img.convert('RGB')
    img_arr = face_utils.image_to_arr(img)
    face_acc = FaceAccredit(img_arr)
    return face_acc

def np_arr_save_test(face_name):
    face_acc = face_init('b')
    face_arr_list,face_in_img = face_acc.face_encoding()
    for index,face_arr in enumerate(face_arr_list):
        face_name = 'a' + '_' + str(index)
        face_utils.save_arr_to_file(face_arr,face_name)

def compare_test():
    face_acc_a = face_init('a')
    face_acc_b = face_init('b')
    face_acc_a.face_encoding()
    b_arr_list,face_in_img = face_acc_b.face_encoding()
    distances = face_acc_a.face_compare(b_arr_list)
    print(distances)

compare_test()
