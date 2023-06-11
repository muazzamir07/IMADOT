#@title *UNET*

import io
import os
import torch
import numpy as np
from PIL import Image
from torchvision import transforms
import torch.nn as nn
import torch.nn.functional as F
from flask import request

class DoubleConv(nn.Module):
    def __init__(self, in_channels, out_channels):
        super(DoubleConv, self).__init__()
        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        x = self.conv(x)
        return x


class UNet(nn.Module):
    def __init__(self):
        super(UNet, self).__init__()
        self.conv_down1 = DoubleConv(1, 64)
        self.conv_down2 = DoubleConv(64, 128)
        self.conv_down3 = DoubleConv(128, 256)
        self.conv_down4 = DoubleConv(256, 512)
        self.maxpool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.upsample = nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.conv_up3 = DoubleConv(256 + 512, 256)
        self.conv_up2 = DoubleConv(128 + 256, 128)
        self.conv_up1 = DoubleConv(128 + 64, 64)
        self.conv_last = nn.Conv2d(64, 2, kernel_size=1)

    def forward(self, x):
        print("UNET FORWARD")
        conv1 = self.conv_down1(x)
        x = self.maxpool(conv1)

        conv2 = self.conv_down2(x)
        x = self.maxpool(conv2)

        conv3 = self.conv_down3(x)
        x = self.maxpool(conv3)

        x = self.conv_down4(x)

        x = self.upsample(x)
        x = torch.cat([x, conv3], dim=1)
        x = self.conv_up3(x)

        x = self.upsample(x)
        x = torch.cat([x, conv2], dim=1)
        x = self.conv_up2(x)

        x = self.upsample(x)
        x = torch.cat([x, conv1], dim=1)
        x = self.conv_up1(x)

        out = self.conv_last(x)

        return out


def UNETPrediction(ct_images, pet_images):

    print("=================")
    print("UNET WORKING")
    print("=================")    

    # load the model
    model = UNet() # create an instance of your UNet model
    model.load_state_dict(torch.load('./static/unet_model.pt', map_location=torch.device('cpu')))

    # model = torch.load('./static/unet_model.pt', map_location=torch.device('cpu'))
    
    # ct_folder = None
    
    # if 'ctFolder' in request.files:
    #     ct_folder = request.files.getlist('ctFolder')
    
    # CT_IMAGES = []
    # counter = 0
    # for image in ct_folder:
    #     counter+=1
    #     image = Image.open(image)
    #     # image = image.read()
    #     # img = np.frombuffer(image, np.uint8)
    #     # img = cv.imdecode(img, cv.IMREAD_COLOR)
    #     # img = cv.resize(img, (128, 128))
    #     # cv.imwrite("Testing/" + str(counter) + ".jpeg", img)
    #     CT_IMAGES.append(image)

    # filename = "0.jpg"
    # print("===============================")
    
    # print(CT_IMAGES)
    
    # print("===============================")
    # image_path = os.path.join(ct_images, filename)
    
    # reads the image that we are to perform segmentation on
    # image = Image.open(image_path)
    # image = Image.open(image_path)

    # Set up the image transforms
    image_transforms = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.ToTensor(),
        transforms.Normalize((0.5,), (0.5,))
    ])

    # Apply the transforms to the image
    import torch.nn.functional as F

    # Apply the transforms to the image
    print("Type CT", type(ct_images[0]), ct_images[0].shape)
    ct_image = Image.fromarray(ct_images[0])
    input_tensor = image_transforms(ct_image).unsqueeze(0)
    
    print(input_tensor)
    print("=================")
    
    # Get the output tensor from the model
    output_tensor = model.forward(input_tensor)


    # Normalize the output tensor using softmax activation
    output_tensor = F.softmax(output_tensor, dim=1)

    print("=================")
    print("OUTPUT TENSOR")
    print(output_tensor)
    print("=================")

    # Convert the output tensor to a numpy array and postprocess it
    output_array = output_tensor.squeeze().detach().cpu().numpy()

    print("=================")
    print("OUTPUT ARRAY")
    print(output_array)
    print("=================")

    # Perform any necessary postprocessing such as resizing or color mapping
    # output_array[1]

    import numpy as np
    threshold_value = 0.5
    segmented_img = np.where(output_array[1] > threshold_value, 1, 0)



    ######### CHECK FOR GT MASK FOR ACCURACY #############
    ######################################################

    
    # Calculate accuracy by comparing predicted mask with ground truth mask
    #gt_mask = np.array(gt_mask)
    #accuracy = np.mean(segmented_img == gt_mask)


    ######################################################


    #import matplotlib.pyplot as plt
    # print(len(output_array))
    # print(np.shape(output_array[1]))
    #plt.imshow(segmented_img)

    # -----------------return img that is segmented----------------------------#
    # return segmented_img

    # Convert numpy array to PIL Image
    #pil_img = Image.fromarray(segmented_img)

    # Convert PIL Image to PNG byte stream
    #buffer = io.BytesIO()
    #pil_img.save(buffer, format='JPEG')
    #jpeg_segmented = buffer.getvalue()

    return segmented_img