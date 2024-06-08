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

I'm working on an AI / ML / buzzword bingo project and wanted to use a Raspi for data acquisition. In this case the data is images for computer vision research, so it sounds a lot like I want to [reinvent the webcam](https://en.wikipedia.org/wiki/Trojan_Room_coffee_pot)

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

## Context

While this is not necessarily a tutorial on using Raspi as a webcam, I want to set a little context about what motivated me to write a better logging script and also this post

### Hardware

The specific hardware used isn't critical, any Raspi with a camera module will do. I used the mentioned Raspi 4, started with a [Camera Module v1](https://www.raspberrypi.com/documentation/accessories/camera.html#hardware-specification) and later used a [Camera Module 3](https://www.raspberrypi.com/documentation/accessories/camera.html#hardware-specification). I am running `Debian GNU/Linux 12 (bookworm)` [headless](https://en.wikipedia.org/wiki/Headless_computer) and connecting via [SSH](https://en.wikipedia.org/wiki/Secure_Shell)

### Taking a photo

There are many ways to take a photo on a Raspi using a camera module, here is one:

`libcamera-still --immediate -o test.jpg`

The `--immediate` flag doesn't seem to be in most tutorials. Without it, the command output appears to be streaming video as indicated by the `30.01 fps` clue:

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

**Note:** `libcamera-still` prints a lot to `stderr`:

```
[60:22:40.351472778] [7732]  INFO Camera camera_manager.cpp:284 libcamera v0.2.0+46-075b54d5
[60:22:40.390038630] [7736]  WARN RPiSdn sdn.cpp:39 Using legacy SDN tuning - please consider moving SDN inside rpi.denoise
[60:22:40.392101690] [7736]  INFO RPI vc4.cpp:447 Registered camera /base/soc/i2c0mux/i2c@1/imx708@1a to Unicam device /dev/media3 and ISP device /dev/media0
[60:22:40.392180281] [7736]  INFO RPI pipeline_base.cpp:1144 Using configuration file '/usr/share/libcamera/pipeline/rpi/vc4/rpi_apps.yaml'
Preview window unavailable
Mode selection for 4608:2592:12:P
    SRGGB10_CSI2P,1536x864/0 - Score: 10600
    SRGGB10_CSI2P,2304x1296/0 - Score: 8200
    SRGGB10_CSI2P,4608x2592/0 - Score: 1000
[60:22:40.393532260] [7732]  INFO Camera camera.cpp:1183 configuring streams: (0) 4608x2592-YUV420 (1) 4608x2592-SBGGR10_CSI2P
[60:22:40.393892125] [7736]  INFO RPI vc4.cpp:611 Sensor: /base/soc/i2c0mux/i2c@1/imx708@1a - Selected sensor format: 4608x2592-SBGGR10_1X10 - Selected unicam format: 4608x2592-pBAA
Still capture image received
```

This won't affect piping `stdout` to `base64` for encoding, but we can *mute* those messages with:

`libcamera-still --immediate -o - 2>/dev/null`

where `2>/dev/null` *redirects* `stderr` to `/dev/null` 

### Uploading a photo

If we thought there were a lot of ways to take a photo on a Raspi, there are effectively infinite ways to store the photo to the cloud / someone else's computer

When I started this project, I evaluated *smart* cameras like the [Aqara Camera Hub G2H Pro](https://www.aqara.com/en/product/camera-hub-g2h-pro/). While the form factor was a little big and bulky compared to a bare PCBA like the Camera Modules, it was really the lack of flexibility in the software side of things that put me down the Raspi path

The G2H Pro does have nice features like:
1. The ability to store images to microSD
   1. Physically retrieving the images felt a little 1999
2. The ability to store images to a [Samba](https://en.wikipedia.org/wiki/Samba_(software)) file share on a [NAS](https://en.wikipedia.org/wiki/Network-attached_storage)
   1. I don't want to manage a NAS
3. [HomeKit Secure Video](https://support.apple.com/guide/security/camera-security-sec525461d19/web)
   1. Again, a nice feature, but not for my application
   
Many of the smart cameras require accounts and subscriptions and still don't have the flexibility I was looking for

#### AWS S3

[AWS Simple Storage Service (S3)](https://en.wikipedia.org/wiki/Amazon_S3) is a fairly ubiquitous *object* store. There are some nuances of what an object store is versus a filesystem, but it's mostly irrelevant to this post

S3 is reasonably easy to setup and integrates nicely with other AWS services like [Lambda](https://en.wikipedia.org/wiki/AWS_Lambda) and [EC2](https://en.wikipedia.org/wiki/Amazon_Elastic_Compute_Cloud) via [Python boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) or other language SDKs, as well as AI / ML services like [SageMaker](https://en.wikipedia.org/wiki/Amazon_SageMaker). It's also easy to sync locally using the [AWS CLI](https://docs.aws.amazon.com/cli/latest/reference/s3/)

One detail about S3 of note is that it is technically flat without a folder / file hierarchy. In practice it seems like there's hierarchy since it can be organized and filtered using [prefix keys](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-prefixes.html)

A prefix key can look a lot like a path to a file, especially when the `/` character is used as the delimiter. The S3 web app will show these hierarchical folders even if they don't technically exist 

It's wise to think about your prefix key up front so that you can efficiently query and retrieve objects in the future. I chose something relatively simple:

`prefix_key = "experiments/experiment_#"`

where `#` is replaced with the experiment number

#### POSTing to S3

AWS provides [an example that uses HTTP POST to upload JPEG images](https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html) (what a coincidence!) to an S3 bucket

Instead, I opted to use [API Gateway](https://aws.amazon.com/api-gateway/) as the HTTP POST endpoint to trigger a Python [Lambda](https://en.wikipedia.org/wiki/AWS_Lambda) to store the image to S3. I did this for the additional flexibility and experience using [AWS Cloud Development Kit (CDK)](https://en.wikipedia.org/wiki/AWS_Cloud_Development_Kit)

I started with the [api-cors-lambda example](https://github.com/aws-samples/aws-cdk-examples/tree/main/python/api-cors-lambda) and:

1. Imported the `aws_s3` package
2. Added an S3 bucket
3. Gave write access to the bucket from the Lambda 
4. Updated the Lambda runtime from Python 3.7 (*wat?*) to Python 3.11
5. Changed the API `GET` method to `POST`
6. Changed the Python Lambda
   1. Imported the base64 package (I'll explain)
   2. Imported the boto3 package to interface to S3
   3. Grabbed the filename from the Event sent by API Gateway
   4. Decoded the base64 encoded file from the Event sent by API Gateway
   5. Stored the decoded file with the filename as the key to the S3 bucket
   6. Returned `statusCode`
      1. On success: `200`
      2. On exception: `500` 

[Base64](https://en.wikipedia.org/wiki/Base64) is a method used to send binary data like images over plain text channels like an HTTP POST body. This method is generally not preferred because:

1. It uses CPU to encode / decode
2. It has > 33% overhead
3. You cannot do partial uploads

The preferred method is using the [`multipart/form-data`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST) POST `formenctype`. I wanted to learn about Base64 and got it working, but I will probably switch to `multipart/form-data` next time I modify the Lambda

#### Putting it all together

We can take a photo and we can upload a file, so let's put it all together by chaining commands. We need to:

1. Take a photo
2. Base64 encode the photo
3. Generate a filename including the date and time
4. Build JSON containing the filename and Base64 image data
5. Upload the data to an HTTP POST API

Putting the above in terms of actual commands looks like:

1. `libcamera-still --immediate -o -`
   1. The same command we ended up with in the *Taking a photo* section 
2. `libcamera-still --immediate -o - 2>/dev/null | base64 -w 0`
   1. Pipes the binary image from `libcamera-still` into the base64 command for encoding
   2. `base64 -w 0` disables line wrapping in the base64 output
      1. It is set to 76 characters by default for usage in email and usenet clients 
3. `$(date -u "%Y%m%dT%H%M%S")Z.jpg`
   1. `date` outputs the current date and time in the format specified
   2. `-u` specifies [UTC](https://en.wikipedia.org/wiki/Coordinated_Universal_Time) time
   3. `"%Y%m%dT%H%M%S"` specifies a date time format like: `20240102T030405`
   4. `$(...)` captures the output of the `date` command
   5. `Z` specifies that the datetime string is UTC
   6. `.jpg` is the filename extension for the JPEG images
4. `(echo -n '{"image": "'; libcamera-still --immediate -o - 2>/dev/null | base64 -w 0; echo '", "filename": "'$(date -u +"%Y%m%dT%H%M%S")Z.jpg'"}')`
   1. [echo](https://en.wikipedia.org/wiki/Echo_(command)) is used to assemble the JSON string
   2. `-n` tells `echo` not to print the trailing `\n` new line
   3. `'...'` tells bash to [interpret text within the single quotes as literal](https://www.gnu.org/software/bash/manual/html_node/Single-Quotes.html), this helps us generate strings with special characters
   4. `{"image": "` defines the beginning of a JSON file and the key of the first object: `image` and has an opening quote for its value
   5. We covered the `libcamera-still` portion above
   6. `","filename":"` provides the closing double quote for the `image` value, the delimiter between the objects, and the key `filename`
   7. We covered the `date` portion above
   8. `(...)` [groups](https://www.gnu.org/software/bash/manual/html_node/Command-Grouping.html) the commands and concatenates `stdout` so that we can pipe the generated JSON into other commands 
5. `(echo -n '{"image": "'; libcamera-still --immediate -o - 2>/dev/null | base64 -w 0; echo '", "filename": "'$(date -u +"%Y%m%dT%H%M%S")Z.jpg'"}') | curl -X POST -H "Content-Type: application/json" -d @- <API URL>`
   1. 

## Script development



My first attempt was a [cron job](https://en.wikipedia.org/wiki/Cron), a periodic job scheduler on Unix-like systems

**Pros**
1. Well established mechanism to run periodic jobs
   1. Like a webcam taking a photo!
2. Baked into the OS, runs automatically at boot
   1. Nice for crashes
3. Actual job is short lived and independent
   1. If the job fails, the next invocation might be fine

**Cons**
1. Not very experiment oriented
   1. Not an interactive / real-time command
      1. For example changing the prefix key / filename
      2. Changing the period
      3. Starting and stopping "experiments"


