from PIL import Image, ImageEnhance

in_path = "/Users/bgalk/Desktop/blurry_text.jpg"

def sharpen_image(in_path):
    image = Image.open(in_path)
    enhancer = ImageEnhance.Sharpness(image)

    factor = 2.0
    enhanced = enhancer.enhance(factor)

    out_path = in_path[:-4] + "_sharp.jpg"
    fp = open(out_path, 'w')
    enhanced.save(fp)





