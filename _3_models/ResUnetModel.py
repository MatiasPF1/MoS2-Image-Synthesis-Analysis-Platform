import torch
import torch.nn as nn


# V1(getting a base) :From the Paper: Road Extraction for Dendrites using Deep Residual U-Net
# Table I – Network Structure of ResUNet Given in the Papper 
# --------------------------------------
# Input: 224×224×3
#
# Encoding:
# L1: Conv1 (3×3/64, s=1) → 224×224×64
#     Conv2 (3×3/64, s=1) → 224×224×64
# L2: Conv3 (3×3/128, s=2) → 112×112×128
#     Conv4 (3×3/128, s=1) → 112×112×128
# L3: Conv5 (3×3/256, s=2) → 56×56×256
#     Conv6 (3×3/256, s=1) → 56×56×256
#
# Bridge(Bottleneck):
# L4: Conv7 (3×3/512, s=2) → 28×28×512
#     Conv8 (3×3/512, s=1) → 28×28×512
#
# Decoding:
# L5: Conv9  (3×3/256, s=2) → 56×56×256
#     Conv10 (3×3/256, s=1) → 56×56×256
# L6: Conv11 (3×3/128, s=2) → 112×112×128
#     Conv12 (3×3/128, s=1) → 112×112×128
# L7: Conv13 (3×3/64, s=2) → 224×224×64
#     Conv14 (3×3/64, s=1) → 224×224×64
#
# Output:
# Conv15 (1×1/1, s=1) → 224×224×1




# --------------------------------------
# Batch and Relu In a Single Module
class BatchAndRelu(nn.Module):
    def __init__(self, ConvInput):
        super().__init__()
        self.bn=nn.BatchNorm2d(ConvInput)
        self.relu=nn.ReLU()

    def forward(self,input):
        x=self.bn(input)
        x=self.relu(x)
        return x

# --------------------------------------
# Residual Block       
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        '''Convolution Layer'''
        self.b1= BatchAndRelu(in_channels)
        self.c1= nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1, stride= stride) #Stride can be 1 or 2
        self.b2= BatchAndRelu(out_channels)
        self.c2= nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1, stride=1) # This Stride is always 1 

        '''Shortcut Connection'''
        self.s=nn.Conv2d(in_channels, out_channels, kernel_size=1, padding=0, stride=stride) # Adjusting dimensions
    
    def forward(self, input):
        x=self.b1(input)
        x=self.c1(x)
        x=self.b2(x)
        x=self.c2(x)
        skip=self.s(input)
        out=x+skip # Addition Last Part
        return out

class decoder_block(nn.Module):
    def __init__(self, in_c, out_c):
        super().__init__()

        self.upsample= nn.Upsample(scale_factor=2, mode='bilinear', align_corners=True)
        self.r = ResidualBlock(in_c + out_c, out_c)
    
    def forward(self, input, skip):
        x=self.upsample(input)
        x=torch.cat((x, skip), dim=1) # Concatenating along channel dimension
        x=self.r(x)
        


# --------------------------------------
# ResUnet Model
class ResUnet(nn.Module):
    def __init__(self):
        super()._init_()

        '''Encoder 1 - Different from other Layers'''
        #Input: 224x224x3
        self.conv1=nn.Conv2d(3, 64, kernel_size=3, padding=1, stride=1)
        self.bn_relu1=BatchAndRelu(64) #64 channels after conv1
        self.conv1_2=nn.Conv2d(64, 64, kernel_size=3, padding=1, stride=1)
        self.Residual1=nn.Conv2d(3, 64, kernel_size=1, padding=0, stride=1) #Residual
        ''' Encoder 2 and 3'''
        self.Encoder2=ResidualBlock(64, 128, stride=2) #Input: 224x224x64 --> Output: 112x112x128
        self.Encoder3=ResidualBlock(128, 256, stride=2) #Input: 112x112x128 --> Output: 56x56x256
        ''' Bridge(Bottleneck)'''
        self.Bridge=ResidualBlock(256, 512, stride=2) #Input: 56x56x256 --> Output: 28x28x512
        ''' Decoder Layers'''
        self.Decoder1=decoder_block(512, 256) #Input: 28x28x512 --> Output: 56x56x256
        self.Decoder2=decoder_block(256, 128) #Input: 56x56x256 --> Output: 112x112x128
        self.Decoder3=decoder_block(128, 64)  #Input: 112x112x128 --> Output: 224x224x64

        ''' Output Layer'''
        self.output_conv= nn.Conv2d(64, 1, kernel_size=1, padding=0, stride=1) #Input: 224x224x64 --> Output: 224x224x1
        self.sigmoid= nn.Sigmoid() #Using Sigmoid as Activation for Output Layer





    def forward(self, input):
        '''Encoder 1 Forward'''
        x=self.conv1(input) # 224x224x3 --> 224x224x64
        x=self.bn_relu1(x)
        x=self.conv1_2(x) # 224x224x64 --> 224x224x64
        residual= self.Residual1(input) # 224x224x3 --> 224x224x64
        Skip1 = x + residual  # Adding Residual, also saving Connection for Decoding 
        '''Encoder 2 & 3 Forward'''
        Skip2= self.Encoder2(Skip1) # 224x224x64 --> 112x112x128  -- This is the Skip Connection that is the output of Encoder 2
        Skip3= self.Encoder3(Skip2) # 112x112x128 --> 56x56x256  -- This is the Skip Connection that is the output of Encoder 3
        '''Bridge Forward'''
        BridgeOut= self.Bridge(Skip3) # 56x56x256 --> 28x28x512 -- This is the output of Bridge

        '''Decoder Forward'''
        D1= self.Decoder1(BridgeOut, Skip3) # 28x28x512 --> 56x56x256
        D2= self.Decoder2(D1, Skip2)        # 56x56x256 --> 112x112x128
        D3= self.Decoder3(D2, Skip1)        # 112x112x128 --> 224x224x64

        '''Output Layer Forward'''
        out=self.output_conv(D3)            # 224x224x64 --> 224x224x1
        out=self.sigmoid(out)               # Sigmoid Activation
        return out

 

#Iniatilization
if __name__ == "__main__":
    model= ResUnet()
    x=torch.randn((1,3,224,224)) #Batch Size of 1, 3 Channels, 224x224 Image
    out=model(x)
    print(out.shape) #Should be 1x1x224x224d



