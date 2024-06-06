---
title: "A decent Python logger"
date: 2024-06-04T19:57:48-07:00
description: ""
categories: []
tags: ["python", "raspi", "camera", "vision"]
toc: true
math: false
draft: true
---
It's been a while since I've *actually* used a [Raspberry Pi](https://www.raspberrypi.com), maybe a decade. That would mean the last model I  used is a [Model 1 B](https://www.raspberrypi.com/products/raspberry-pi-1-model-b-plus/) or maybe even a [Model 1 A](https://www.raspberrypi.com/products/raspberry-pi-1-model-a-plus/). It's probably around here somewhere, we'll see if this post motivates me to dig it out and do something fun with it

Now I'm using a [Model 4 B](https://www.raspberrypi.com/products/raspberry-pi-4-model-b/) with 8 GB RAM (up from 256 MB), WiFi, Bluetooth, USB-C power, better software support. We're not in Kansas anymore

## Background

I'm working on an AI / ML / buzzword bingo project and wanted to use a Raspi for data acquisition. In this case the data being acquired is images for computer vision research, so it sounds a lot like I want to [reinvent the webcam](https://en.wikipedia.org/wiki/Trojan_Room_coffee_pot)

Hmmm, that could be a fun computer vision project too: why send an image of a coffee pot when all you want to know is how full it is?

### Objectives

I often find myself working on loosely defined research projects and this was no exception. I knew I wanted to collect color photos of an object either periodically (maybe at a max of 1 second interval) or triggered by motion detection

The resolution is not particularly important, especially since I will be down-sampling for the computer vision aspect. Something like 1920 x 1080 pixels ([1080p](https://en.wikipedia.org/wiki/1080p)) would be swell

I wanted to avoid storing the images to the boot SD card to mitigate [SD card corruption](https://hackaday.com/2022/03/09/raspberry-pi-and-the-story-of-sd-card-corruption/) or filling up the card

Ultimately, I would need to retrieve all the images for ML development, so I opted to send them straight to an [Amazon S3 bucket](https://en.wikipedia.org/wiki/Amazon_S3) by way of [API Gateway](https://aws.amazon.com/api-gateway/) and a Python [Lambda](https://en.wikipedia.org/wiki/AWS_Lambda), although I think you can upload straight to S3

We can distill the [MVP](https://en.wikipedia.org/wiki/Minimum_viable_product) requirements down to:

1. Periodically take a photo
2. Upload the photo via an [HTTP POST API](https://en.wikipedia.org/wiki/POST_(HTTP))
3. `GOTO 1` 

How hard could it be?

## Development

The specific hardware used isn't critical, any Raspi with a camera module will do. I used the mentioned Raspi 4, started with a [Camera Module v1](https://www.raspberrypi.com/documentation/accessories/camera.html#hardware-specification) and later used a [Camera Module 3](https://www.raspberrypi.com/documentation/accessories/camera.html#hardware-specification). I am running `Debian GNU/Linux 12 (bookworm)` [headless](https://en.wikipedia.org/wiki/Headless_computer) and connecting via [SSH](https://en.wikipedia.org/wiki/Secure_Shell)

### Taking a photo

There are seemingly large number of ways to take a photo on a Raspi using a camera module, here's one:

`libcamera-still --immediate -o test.jpg`

The `--immediate` flag doesn't seem to be in most tutorials. Without it, the command output appears to be streaming video:

```
#0 (0.00 fps) exp 32680.00 ag 4.15 dg 1.00
#1 (30.01 fps) exp 32680.00 ag 3.88 dg 1.05
#2 (30.01 fps) exp 32680.00 ag 3.95 dg 1.03
```

The `libcamera-still --help` command specifies:

`--immediate [=arg(=1)] (=0)           Perform first capture immediately, with no preview phase`

Given that I am running headless, it makes sense that I want to skip the preview phase

The `-o test.jpg` sets the output file name to `test.jpg`. Instead of saving to a file, we may want to send the image data to [stdout](https://en.wikipedia.org/wiki/Standard_streams#Standard_output_(stdout)) by specifying `-` as the filename, so we can [pipe](https://en.wikipedia.org/wiki/Pipeline_(Unix)) the file to another command:

`libcamera-still --immediate -o -`



### The true MVP


