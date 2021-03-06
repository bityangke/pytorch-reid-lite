import random
import math
import logging
import os
import numpy as np
import PIL

import torch
from folder import ImageFolder
import torchvision.transforms as transforms
from samplers import TripletSampler


def init_data_loader(config, num_processes=4):
    if os.path.exists(os.path.join(config["batches_dir"],
                                   "class_mapping.json")):
        import json
        with open(os.path.join(config["batches_dir"],
                               "class_mapping.json"), "r") as f:
            obj = json.loads(f.read())
            config["num_labels"] = len(obj)
    else:
        # The number of labels is the number of dirs in batches_dir
        label_dirs = [p for p in os.listdir(config["batches_dir"])
                      if os.path.isdir(os.path.join(config["batches_dir"], p))]
        config["num_labels"] = len(label_dirs)

    # init dataset
    logging.info("Initializing data loader, this might take a while.....")
    all_transforms = _init_transforms(config["img_h"], config["img_w"],
                                      config["data_augmentation"])
    train_dataset = ImageFolder(config["batches_dir"],
                                transform=all_transforms)

    # init data loader
    # configure sampling strategy
    class_balanced_sampling = config["tri_loss_params"]["margin"] > 0 or \
        config["batch_sampling_params"]["class_balanced"]
    if class_balanced_sampling:
        logging.info("Using class_balanced sampling strategy.")

    # construct data loader
    batch_size = config["batch_size"] if (not class_balanced_sampling) else None
    shuffle = not class_balanced_sampling
    sampler = TripletSampler(config["batch_sampling_params"], train_dataset) \
        if class_balanced_sampling else None
    data_loader = torch.utils.data.DataLoader(
        train_dataset,
        shuffle=shuffle,
        batch_size=batch_size,
        num_workers=num_processes,
        batch_sampler=sampler
    )

    # log training set info
    count = len(train_dataset)
    iterations_per_epoch = len(data_loader)
    logging.info(
        "[TRAINING SET INFO] number of example: %s, number of labels: %s, "
        "iterations_per_epoch: %s" %
        (count, config["num_labels"], iterations_per_epoch)
    )
    return data_loader


def _init_transforms(img_h, img_w, aug_params):
    transforms_list = []

    # Resize only
    transforms_list.append(transforms.Resize((img_h, img_w)))

    # Randomly flip the image horizontally.
    if aug_params["mirror"]:
        transforms_list.append(transforms.RandomHorizontalFlip())

    # Randomly rotate the image
    if aug_params["rotation"] != 0:
        degrees = aug_params["rotation"]
        transforms_list.append(transforms.RandomRotation(degrees))

    # Color jiterring
    if aug_params.get("colour_jiterring", False):
        transforms_list.append(transforms.ColorJitter())

    # Random erasing
    if aug_params.get("random_erasing", False):
        transforms_list.append(RandomErasing())

    # Convert the images to tensors and perform normalization
    normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406],
                                     std=[0.229, 0.224, 0.225])
    transforms_list.append(transforms.ToTensor())
    transforms_list.append(normalize)

    # Pack all transforms together
    all_transforms = transforms.Compose(transforms_list)

    return all_transforms


class RandomErasing(object):
    """
    Class that performs Random Erasing in Random Erasing Data Augmentation
    by Zhong et al.
    ---------------------------------------------------------------------------
    probability: The probability that the operation will be performed.
    sl: min erasing area
    sh: max erasing area
    r1: min aspect ratio
    mean: erasing value
    """
    def __init__(self, probability=0.6, sl=0.02, sh=0.1, r1=0.3,
                 mean=[0.4914, 0.4822, 0.4465]):
        self.probability = probability
        self.mean = mean
        self.sl = sl
        self.sh = sh
        self.r1 = r1

    def __call__(self, img):
        if random.uniform(0, 1) > self.probability:
            return img

        img = np.asarray(img).copy()
        img = np.transpose(img, [2, 0, 1])
        img_c, img_h, img_w = img.shape

        for attempt in range(100):
            # area = img.size()[1] * img.size()[2]
            area = img_h * img_w

            target_area = random.uniform(self.sl, self.sh) * area
            aspect_ratio = random.uniform(self.r1, 1/self.r1)

            h = int(round(math.sqrt(target_area * aspect_ratio)))
            w = int(round(math.sqrt(target_area / aspect_ratio)))

            if w < img_w and h < img_h:
                x1 = random.randint(0, img_h - h)
                y1 = random.randint(0, img_w - w)
                if img_c == 3:
                    img[0, x1:x1+h, y1:y1+w] = self.mean[0]
                    img[1, x1:x1+h, y1:y1+w] = self.mean[1]
                    img[2, x1:x1+h, y1:y1+w] = self.mean[2]
                else:
                    img[0, x1:x1+h, y1:y1+w] = self.mean[0]

                img = np.transpose(img, [1, 2, 0])
                img = PIL.Image.fromarray(img)
                return img

        img = np.transpose(img, [1, 2, 0])
        img = PIL.Image.fromarray(img)
        return img
