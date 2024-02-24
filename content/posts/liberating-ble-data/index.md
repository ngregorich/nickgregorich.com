---
title: “Liberating BLE data”
date: 2024-02-19T09:01:08-08:00
description: “A simple BLE reverse engineering walkthrough”
categories: []
tags: [“bluetooth”, “BLE”, “reverse engineering”, “data”, “swift”, “walkthrough”]
toc: true
math: false
draft: true
---
## Background

I recently had a need for a kitchen scale with some sort of data logging feature. Ideally the scale would have WiFi and push every measurement to a REST API, but I would have settled for the ability to export a .csv file with timestamps of my measurements

I couldn’t find the exact thing I was looking for, so I purchased an [Etekcity Luminary Kitchen Scale](https://etekcity.com/collections/kitchen-scales/products/eks-l221-sus-luminary-kitchen-scale). The Luminary has some pretty nice features including a 300 mAh battery charged via a USB-C port, [Bluetooth Low Energy (BLE)](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy)connectivity, and the [VeSync app](https://www.vesync.com/app) for iOS and Android

I unboxed the scale and downloaded the app, but I didn’t find a way to export the timestamped .csv file full of scale measurements that I was hoping for

The BLE communication between the scale and the app should be pretty simple, maybe I can reverse engineer it and liberate its data!

## LightBlue

[LightBlue](https://punchthrough.com/lightblue-features/) by a company called Punch through bills itself as “The Go-To BLE Development Tool”, and I think that’s a fair assessment

I’m going to use the macOS version of LightBlue for this walk through, but it is also available for iOS and Android

When you open LightBlue you’ll probably be prompted to give the app access to Bluetooth on your device, then you’ll see the scan screen where you can see all the BLE devices that have [advertised](https://en.wikipedia.org/wiki/Bluetooth_advertising) in the last few moments

![scanning for scale](scanning_for_scale.png)

LightBlue will show a surprising number of devices in the list! This will include your Apple devices including Mac, iPhone, AirTag, your other [Internet of things (IoT)](https://en.wikipedia.org/wiki/Internet_of_things) devices, maybe even your neighbor’s devices

You’ll need to find the device you are trying to liberate in the list. This may require some sleuthing using the whether the device is on (and advertising) or off (not advertising), [received signal strength indicator (RSSI)](https://en.wikipedia.org/wiki/Received_signal_strength_indicator) to locate the device in question, or if you’re really lucky the device will advertise an obvious name like ours did: `Etekcity Nutrition Scale` (with a relatively high RSSI, so I can infer that it’s probably not my neighbor’s)

Next, we tap the device name so LightBlue can *interrogate* it (sounds intense!)

![interrogating scale](interrogating_scale.png)

Interrogation will reveal the device’s [services and characteristics](https://en.wikipedia.org/wiki/Bluetooth_Low_Energy). For example, we’re expecting (hoping) to reveal a service containing a characteristic that holds the same reading on the kitchen scale’s display

![scale services](scale_services.png)

## Services and characteristics

LightBlue has revealed a single service: `0xFFF0` with 2 characteristics:

1. `0xFFF2` with property: write without response
2. `0xFFF1` with property: notify

Both properties are as they sound:

1. Write without response allows the central (Mac, iPhone) to write to the peripheral (scale), but the peripheral will not provide a response indicating that the transmission was successful or not
2. Notify is somewhat similar and allows the scale peripheral to notify whenever the characteristic becomes available without the central responding to acknowledge receipt of the notification

I’m not sure what the write characteristic does. The scale features selectable measurement units (grams, ounces, even fluid ounces) so maybe we can write those over BLE? It might be nice to force the scale into a given unit so we can always log the same units. Luckily I have a work around, I’ll cover it later

The notify characteristic is the one we’re interested in. There is an implicit *read* before the *notify*, meaning we can read the scale measurement via this characteristic

## The notify characteristic

If we tap the `0xfff1` *notify* characteristic in LightBlue, we’ll see a button called *Listen for notifications*

![listen for notifications](notify_switch.png)

Tap this button to have LightBlue *listen* to notifications for this characteristic. Each time this characteristic is updated, LightBlue will show the updated value and show a timestamped history of the recent values below

![updating the characteristic](characteristic_98g.png)

In our case, the characteristic seems to update each time the scale stabilizes after the measurement changes

In the history of this characteristic, we see 3 entries:

1. The current value with darker font
    1. `0xA522810B00A90187A10000D40300020001`
2. The previous value in the lighter font in the middle:
    1. `0xA522800B00AA0187A10000D40300020001`
3. Two values back in the lighter font at the bottom:
    1. `0xA5027F0500B90178A10001`

One of these things is not like the others, can you spot it?

The 2 most recent values are longer (17 bytes) while 2 values back is shorter (11 bytes)

I was able to decode the scale measurements from the 17-byte value, so I initially regarded the 11-byte transmissions as being truncated, lost in transmission. After further research on the Etekcity scale, I found [similar work by George Hertz](https://dev.to/hertzg/hacking-ble-kitchen-scale-55io) who noted that the shorter transmissions indicated things like “err on / err off”, “tare set / update / tare off”, and “item on scale / no item on scale”. Thanks George!

## Decoding the measurements

So we can receive a 17 (or 11) byte transmission from a scale over BLE, now what?

We’ll have to decode the transmission. Luckily we have a great point of reference: the actual display on the scale which shows the measurement including units

We don’t know if the scale sends the VeSync app raw [analog to digital converter (ADC)](https://en.wikipedia.org/wiki/Analog-to-digital_converter) samples, a standard unit like grams, or whatever the units on the display says (spoiler: it’s the last one)

Why don’t we see if we can tease out the measurement from the characteristic by putting different objects on the scale, noting the measurement in a fixed unit (grams) and then seeing what bytes change

The `0xA522810B00A90187A10000D40300020001` value above was transmitted when the scale display showed `98 g`:

![batteries](scale_98g.jpg)

We can put a different object on the scale:

![sharpie](scale_18g.jpg)

get a new measurement, and get a notification on our characteristic:

![sharpie characteristic](characteristic_18g.png)

Now we have two references and two values to decode:

1. `98 g = 0xA522810B00A90187A10000D40300020001`
2. `18 g = 0xA5228D0B00C00187A10000B40000020001`

We should be able to get away with ignoring the common bytes between the two transmissions and focus on the differences in order to extract the data:

1. `0x10B_A9_D403`
2. `0xD0B_C0_B400`

I am not sure why there are 3 discrete sections of the transmission with different values for different readings. Having 2 sections would be understandable: a measurement field and a CRC or checksum field, but I’m not sure what the 3rd might be

We don’t really know anything about the transmission including the [endianness](https://en.wikipedia.org/wiki/Endianness), so everything should be on the table when it comes to reverse engineering

The first section is only 12 bits (maybe 16 if the most significant nibbles are both 0) but only 2 bits are unique between them which doesn’t feel like enough information to distinguish 98 and 18, so let’s keep looking

The second section is only 8 bits for a range of 256, quite a bit short of the 10 kg range of the scale. More bits probably get set for larger measurements, but let’s keep looking

The third section looks like it could be 16 bits. If we convert hex to decimal, we get `0xd403 = 54275` which seems far off from 98 g. But if we do a byte swap we get `0x03d4 = 980` which sure looks like 98.0!

If we do the same byte swapped hex to decimal on the 18 g measurement, we get `0x00b4 = 180` which looks like 18.0, awesome!

Later, I ended up reading this data in an iOS app using [Swift](https://en.wikipedia.org/wiki/Swift_(programming_language)). When reading the value of the characteristic, the byte ordering is as follows:

```text
Byte number:         0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16
Example sequence: 0xA5_22_81_0B_00_A9_01_87_A1_00_00_D4_03_00_02_00_01
```

We now know the measurement is at bytes 11 and 12 (little endian). There’s actually one more byte associated with the measurement: byte 10 is the sign. If the byte is 0 the sign is positive. In my code I wrote `if sign_byte > 0 then is_negative`, but I can’t remember if just a single bit gets set 

If we push the *UNIT* button on the device, we can see bytes 14 and 15 change but with an interesting pattern

It turns out that byte 14 is the *units* and byte 15 is what I called the *media*. This is a kitchen nutrition scale, so it has a way to designate if the measurement is water, milk, or neither / nothing

There’s one more byte that’s interesting to us, byte 16 is what I called the stable byte. If this byte is set to `0x01`, the reading is stable or valid. When placing or removing items from the scale, the byte goes to 0x00, presumably indicating that the reading is not stable and shouldn’t be considered valid

What we know about the Etekcity Luminary scale:

1. BLE advertised name: `Etekcity Nutrition Scale`
2. BLE service: `0xfff0`
3. BLE characteristic: `0xfff1`
4. Measurement payload length: 17 bytes
5. Sign: `byte 10`
    1. `0x00`: positive
    2. Otherwise: negative
6. Value: `bytes 11 and 12`
7. Units: `byte 14`
    1. `0x00`: ounces
    2. `0x01`: ounces
        1. The scale displays the measurement as integer pounds and fixed / fractional ounces
        2. The BLE data is identical to the `0x00` case, fixed / fractional ounces
    3. `0x02`: grams
    4. `0x03`: milliliters
    5. `0x04`: fluid ounces 
8. Media: `byte 15`
    1. `0x00`: none
    2. `0x01`: water
    3. `0x02`: milk 
9. Stable: `byte 16`
    1. `0x01`: stable
    2. Otherwise: unstable

There is some more information that we aren’t using which may include:

1. CRC or other checksum
2. Error conditions
3. Tare state 

## Web Bluetooth

There’s a little known [Web Bluetooth](https://github.com/WebBluetoothCG/web-bluetooth) standard that allows web browsers to communicate via Bluetooth. Unfortunately [there isn’t support for Apple’s Safari nor Firefox](https://caniuse.com/web-bluetooth), so there doesn’t seem to be widespread usage of the library. We can still make a quick prototype using Google Chrome on macOS!

One thing to note is that connecting with Web Bluetooth requires a "user gesture" like a button click to initiate. Here is an example of the error message when trying to connect to Bluetooth calling from `window.onload`:

```text
Bluetooth error: DOMException: Failed to execute 'requestDevice' on 'Bluetooth':
Must be handling a user gesture to show a permission request.
```

This seems like a good move security wise in order to prevent a rogue webpage from connecting to BLE devices in your home, but it adds a little bit of friction. We can fix the above error by connecting after a button click:

```javascript
const scanButton = document.getElementById('scanButton');
scanButton.addEventListener('click', function () {
```

When building a native iOS app, the user needs to agree to give the app Bluetooth permissions once and then is free to connect to devices upon launch, delivering a much nicer user experience

### Web Bluetooth app step by step

We can build an app to connect to the Etekcity scale in a single HTML file

1. Create a new file called `etekcity_nutrition_scale.html`
2. Add boilerplate HTML
   1. `<html>`
   2. `<head>`
   3. `<title>`
   4. `<body>`
   5. I added a `<style>` tag in the `<head>` to use CSS for monospace font
      1. `<style>#output p { font-family: monospace; }</style>`
3. Add a `<div>` to the `<body>` to display the scale measurements
      1. `<div id="output"></div>`
4. Add a `<button>` to the `<body>` to connect to Bluetooth
   1. `<button id="scanButton">Scan for Etekcity Nutrition Scale</button>`
5. Add a `<script>` for the Web Bluetooth code
6. Add a listener for when the HTML has been loaded
   1. `document.addEventListener('DOMContentLoaded', function () {`
7. Retrieve the button from the DOM:
   1. `const scanButton = document.getElementById('scanButton');`
8. Add a callback function for when the DOM button is clicked:
   1. `scanButton.addEventListener('click', function ()`
9. Use [navigator.bluetooth.requestDevice](https://webbluetoothcg.github.io/web-bluetooth/#dom-requestdeviceoptions-filters) to prompt the user to connect to a Bluetooth device
   1. We can filter the devices shown in the user prompt by:
      1. GATT service UUID (`0xfff0` for our device)
      2. Name (`Etekcity Nutrition Scale` for our device)
      3. Manufacturer specific data
      4. Service data
   2. In our case, we can filter by name
      1. `navigator.bluetooth.requestDevice({ filters: [{name: 'Etekcity Nutrition Scale'}], })`
10. At this point in the flow, the user will need to select the device from a pop-up menu
11. The `requestDevice()` function returns a promise that resolves to a BluetoothDevice object
12. The callback for the promise is defined in the `.then()` method
13. We can make a sequence of these asynchronous operations to connect to the scale and listen for the characteristic value changing