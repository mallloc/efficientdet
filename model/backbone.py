import torch
import torch.nn as nn
import torch.nn.functional as F

from model.efficientnet import EfficientNet as EffNet


class EfficientNet(nn.Module):
    """ Backbone Wrapper """
    def __init__(self, model_name):
        super(EfficientNet, self).__init__()
        model = EffNet.from_pretrained(model_name)
        del model._bn1, model._conv_head, model._fc
        del model._avg_pooling, model._dropout
        self.model = model

    def forward(self, x):
        x = self.model._swish(self.model._bn0(self.model._conv_stem(x)))

        features = []
        for idx, block in enumerate(self.model._blocks):
            drop_connect_rate = self.model._global_params.drop_connect_rate
            if drop_connect_rate:
                drop_connect_rate *= float(idx) / len(self.model._blocks)
            x = block(x, drop_connect_rate=drop_connect_rate)
            if block._depthwise_conv.stride == [2, 2]:
                features.append(x)

        return features[1:]

    def get_channels_list(self):
        channels = []
        for block in self.model._blocks:
            if block._block_args.stride == [2]:
                channels.append(block._block_args.output_filters)

        return channels[1:]


if __name__ == '__main__':
    ''' quick test '''
    # 3.595388M

    backbone = EfficientNet('')
