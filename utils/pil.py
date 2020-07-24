from PIL import Image, ImageChops

def crop(im, margin=None):
    """
    Margin: int or (left, top, right, bottom)
    """
    bg = Image.new(im.mode, im.size, im.getpixel((0,0)))
    diff = ImageChops.difference(im, bg)
    #Bounding box given as a 4-tuple defining the left, upper, right, and lower pixel coordinates.
    #If the image is completely empty, this method returns None.
    bbox = diff.getbbox()
    if bbox:
        if margin is not None:
            if isinstance(margin, int):
                margin = (margin, margin, margin, margin)
            bbox = (bbox[0]-margin[0], bbox[1]-margin[1], bbox[2]+margin[2], bbox[3]+margin[3])
        return im.crop(bbox)
