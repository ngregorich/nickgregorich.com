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
It's been a while since I've *actually* used a [Raspberry Pi](https://www.raspberrypi.com), maybe a decade. That would mean the last model I have used would be a [Model 1 B](https://www.raspberrypi.com/products/raspberry-pi-1-model-b-plus/) or maybe even a [Model 1 A](https://www.raspberrypi.com/products/raspberry-pi-1-model-a-plus/). It's probably around here somewhere, we'll see if this post motivates me to dig it out and do something fun with it

## Background

I'm working on an AI / ML / buzzword bingo project and wanted to use a Raspi for data acquisition. In this case the data being acquired is images for computer vision research, so it sounds a lot like I want to [reinvent the webcam](https://en.wikipedia.org/wiki/Trojan_Room_coffee_pot). Hmmm, that could be a fun computer vision project too: why send an image of a coffee pot when all you want to know is how full it is?

### Objectives

I often find myself working on loosely defined research projects and this was no exception. I knew I wanted to collect color photos of an object either periodically (maybe at a max of 1 second interval) or triggered by motion detection

The resolution is not particularly important, especially since I will be down-sampling for the computer vision. Something like 1920 x 1080 pixels ([1080p](https://en.wikipedia.org/wiki/1080p)) would be swell

I wanted to avoid storing the images to the boot SD card to mitigate [SD card corruption](https://hackaday.com/2022/03/09/raspberry-pi-and-the-story-of-sd-card-corruption/) or filling up the card. I would ultimately need to retrieve the images for ML development, so I opted to send them straight to an [Amazon S3 bucket](https://en.wikipedia.org/wiki/Amazon_S3) by way of [API Gateway](https://aws.amazon.com/api-gateway/) and a Python [Lambda](https://en.wikipedia.org/wiki/AWS_Lambda), although I think you could probably upload straight to S3

