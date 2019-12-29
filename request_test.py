img_src = "https://pbs.twimg.com/media/EMZQzy6UwAEnZZ8.jpg:large"

# from skimage import io
# image = io.imread(img_src)
# io.imshow(image)
# io.show()

import requests as req
from PIL import Image
from io import BytesIO
response = req.get(img_src)
image = Image.open(BytesIO(response.content))
image.show()
