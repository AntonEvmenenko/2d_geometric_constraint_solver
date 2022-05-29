from PIL import Image

icons = {
    (0, 0): "segment.png",
    (0, 1): "arc.png",
    (0, 2): "circle.png",

    (1, 0): "coincidence.png",
    (1, 1): "perpendicularity.png",
    (1, 2): "parallelity.png",
    (1, 3): "equal_length.png",
    (1, 4): "tangency.png",

    (2, 0): "horizontality.png",
    (2, 1): "verticality.png",
    (2, 2): "fixed.png",
    (2, 3): "length.png",
    (2, 4): "concentricity.png",
}

def box(i, j, size):
    return (j * size, i * size, (j + 1) * size, (i + 1) * size)

def split(icons_set_filename, icon_size, grid_size, output_folder):
    image = Image.open(icons_set_filename)
    width, height = image.size
    assert width == height

    icons_set_size = width / grid_size

    for (i, j), icon_name in icons.items():
        icon = image.crop(box(i, j, icons_set_size))
        icon.thumbnail((icon_size, icon_size), Image.BICUBIC)

        try:
            icon.save(f'{output_folder}/{icon_name}')
        except Exception as e:
            print (str(e))

split(icons_set_filename = "icons/icons_set_128x128.png", icon_size = 32, grid_size = 5, output_folder = "icons/32x32/")
split(icons_set_filename = "icons/icons_set_128x128.png", icon_size = 20, grid_size = 5, output_folder = "icons/20x20/")