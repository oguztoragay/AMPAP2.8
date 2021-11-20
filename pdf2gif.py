from pdf2image import convert_from_path
from PIL import Image
import glob
def make_gif_for_me(foldername):
    list_of_pngs = glob.glob(foldername+'*.png')
    my_poppler_path = r'C:/Users/ozt0008/Desktop/rere/poppler-0.68.0_x86/poppler-0.68.0/bin'
    frames = []
    for i in list_of_pngs:
        new_frame = Image.open(i)
        frames.append(new_frame)
    pngname = str(foldername+'loopinggif.gif')
    frames[0].save(pngname, format='GIF', append_images=frames[1:], save_all=True, duration=2000, loop=0)
    return 0
# foldername = 'C:/Users/ozt0008/Desktop/rere/meeting/2021-09-22/11'
# make_gif_for_me(foldername)