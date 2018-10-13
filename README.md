## Overview

This codebase is for training/deploying models in pytorch (onnx), 
currently it provides basic protocols for model training, evaluation and deploying.


## Install Dependency

This code depends on pytorch v0.4 and torchvision, run the 
following command to install pytorch:

```
pip install --user torch==0.4 torchvision==0.2.1 tensorflow==1.8 tensorboardX lmdb -i https://pypi.douban.com/simple/
```

### Model Training

To train a model, clone the repo, modify params.json as you need, and run train.py.

```
cd pytorch-reid
# Modify params.json - specify your own working dir.
# sub_working_dir is optional
python train.py --operation start_train --config_path params.json --sub_working_dir SUB\_WORKING\_DIR\_NAME
```

### On-the-Fly Evaluation:

You can enable on-the-fly automatic evaluation by setting "type" under "evaluation_params" key in params.json (default is "None"). If set, after each epoch the code will run your evaluation, and only saves the best-performing model.

The code currently supports "market\_evaluate" for person-reid and "classification\_evaluate" for image classification, but it is easy to extend this to support other evalutiaons (like LFW). All you need to do is create a new file - say "lfw\_evaluate.py" in the evaluate folder, and expose a run\_eval method which takes in your training config and returns your evaluation result. See evaluate/market\_evalute.py for an example.

### Tensorboard visualization

You can visualize your training progress with tensorboardX (a pytorch integration of Tensorboard for Tensorflow), the code generates an event file in your sub working dir, to run tensorboard, do so as you would when using Tensorflow: 
```
cd ~/.local/bin
./tensorboard --logdir=YOUR_SUB_WORKING_DIR --port=YOUR_PORT
```

## Baselines
No. | backbone | imgSize | PCB | rank1  | map | augment | comment
--- | --- | --- | --- | --- | --- | --- | ---
1 | resnet-50 | 384 * 128 |1536/6 |0 | 0 |mirro | 
 



## Parameters

The params.json file contains the settings you need to run your model, here is a brief 
documentation of what they are about:

1. ***"batch\_size"***: The batch\_size PER GPU.
2. ***"batches\_dir"***: The path to your dataset generated by the open platform.
3. ***"data\_augmentation"*** contains the params related to data\_augmentation.
4. ***"epoch"***: How many epochs to train your model.
5. ***"imagenet\_pretrain"***: Whether to initialze your model with ImageNet pretrained network. Note that some networks might not support this.
6. ***"img\_h" and "img\_w"***: Size of the input image.
7. ***"lr"*** contains the params related to learning rate setting, where "base\_lr" denotes the initial learning rate for the base network and "fc\_lr" denotes the initial learning rate for the fc layers. Also note that "decay_step" here refers to training epochs.
8. ***"model\_params"*** contains the setting of network structure.
9. ***"optimizer"***: Which opitimization algorithm to use, default is is SGD.
10. ***"parallels"***: The GPU(s) to train your model on.
11. ***"pretrain\_snapshot"***: Path to pretrained model.
12. ***"weight\_decay"***: The l2-regularization parameter.
13. ***"fine\_tune"***: If set to "true", train only the final classification layer and freeze all layers before.
14. ***"evaluation\_params"***: Run different types of evaluation accordingly, now supports "market\_evaluate" and "classificaton\_evaluate".
15. ***"working\_dir"***: Where your model will be stored on disk.
19. ***"tri\_loss\_margin"***: If set, the model will be trained with the Triplet loss with batch-hard mining, set to "soft\_margin" to use the soft margin setting, and set to 0 to disbale.
20. ***"tri\_loss\_lambda\_cls"***: If set, the model will be trained with the Triplet loss and The Classicfication loss(softmax/AM-softmax) together, set to 0 to disbale.
21. ***"batch\_sampling\_params"***: If "class\_balanced" is set to true, then the code will sample each batch by first randomly selecting P classes and then randomly selecting K images for each class (batch\_size = P * K); set "class\_balanced" to false to use random sampling. Also note that if "class\_balanced" is set to true, the lr decay step will be counted as each iteration, as opposed to epoch for random sampling.