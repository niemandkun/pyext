from os import path


# 10 MB ext4 image

TEST_DIR = path.dirname(path.abspath(__file__))
IMAGE_NAME = 'test_image.dd'
IMAGE_SIZE = 10 * 1024**2

SUPERBLOCK_OFFSET = 0x400
GROUP_DESC_OFFSET = 0x800

PATH_TO_IMAGE = path.join(TEST_DIR, IMAGE_NAME)
