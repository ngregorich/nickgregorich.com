---
title: "Internet of dog toys"
date: 2025-04-30T17:00:26-07:00
description: ""
categories: []
tags: ["iot", "esp32", "esphome", "homeassistant", "homekit"]
toc: true
math: false
draft: true
---
I'm going to start with some introspection

First, it's been a while since I've written a post and I have to admit I miss it. I have had some (happy) things going on in my life, but I should have more time for bloggin' now :)

I have actually been working on some projects: a bigger system integration project with some 3D design in [FreeCAD](https://www.freecad.org) and a couple smaller microcontroller projects

I've found the small microcontroller projects to be super inspiring. In a single evening with a couple dozen lines of code I can build something that might not exist anywhere in the world that solves an actual problem in my life

That's pretty exciting, and highlights that a project doesn't have to be big and expensive to be high value. The return on investment in those twenty lines of code is incredible!

# The problem

A couple years ago, we adopted a Great Pyrenees mix named Roo. We love her deeply and I think the feeling is mutual, especially when you consider her separation anxiety induced howling when we leave the house

We have a couple [HomeKit](https://www.apple.com/home-app/) compatible cameras that we can watch Roo when we are away from home. Reassuring her through the camera's intercom has varying results, she will often continue howling despite hearing our voices

Maybe we could distract Roo with something a little more tangible than a voice from a camera on a nightstand. She loves this toy we call *squirrel ball* that is actually called [Hyper Pet Doggie Tail](https://www.amazon.com/stores/page/4E7BAF2F-5667-4AC6-A597-D1AAB7D17087)

Squirrel ball has a motor, speaker, some sort of shock sensor, power switch, and holder for 3 AAA batteries. When you (or maybe your dog) throw the ball against a hard surface like the floor, the shock sensor triggers a 2 - 3 second sequence of motorized vibration and speaker chirping. The ball is unbalanced by design, so the motor actuation causes the ball to hop around on the floor. It's completely obnoxious and she loves it :)

What if we could trigger the ball remotely when we see that Roo is having a hard time on the Roo-cam? Maybe that could help address her separation anxiety

# Cracking open squirrel ball

Squirrel ball has a fabric cover that is easily removed so you can replace the batteries. There's a tiny Phillips head screw that you need to loosen to replace the batteries. You know that squirrel ball means business if the batteries are held in with a screw!

The inside of the device can be accessed after removing 3 more Phillips screws from the other side. Careful, when you do this some motor gears and springs might fall out and it might take minute to learn how to put it all back together (spoiler: this was the hardest part of the whole project)

Inside you'll find the expected motor, speaker, an axle, and a PCBA with a single resistor and capacitor on the exposed side. The speaker, axle, and PCBA are each attached with 2 Phillips screws

If you unscrew and flip the PCBA over you'll find a decent sized electrolytic capacitor, a TO-92 package, and what looks like the shock sensor / switch

I didn't take note of the value of the electrolytic capacitor

The TO-92 is labeled "882C" which seems to be a fairly generic NPN BJT. Here's a [reference part from ST Micro](https://www.st.com/resource/en/datasheet/2sd882.pdf), but the actual part used looks to be from a lower cost manufacturer

The shock sensor is an interesting design: it's a metallic cylinder surrounding a metal spring, both soldered directly to the PCBA. You can imagine when the ball is thrown at the floor, the spring deflects and makes electrical contact with the enclosing cylinder. I don't know if there is a name for this kind of sensor / switch, but it's an elegant design

I probed with a voltmeter and the outer cylinder is connected directly to the battery voltage. This suggests that toggling the *spring* high with would be a good strategy for triggering the ball with a microcontroller

# Microcontroller selection

I'm an avid user of both [Apple HomeKit](https://www.apple.com/home-app/) and [Home Assistant](https://www.home-assistant.io) where HomeKit is the primary interface and Home Assistant provides features beyond what are available in HomeKit

But wait, this section is titled *Microcontroller selection* not *Home automation software*. Home Assistant has a sister project called [ESPHome](https://esphome.io) that:

> Turn your ESP32, ESP8266, or RP2040 boards into powerful smart home devices with simple YAML configuration

These ESPHome microcontrollers integrate with Home Assistant, which bridges to HomeKit. You can also create HomeKit accessories directly through the [HomeKit ADK](https://github.com/apple/HomeKitADK) or [Matter](https://en.wikipedia.org/wiki/Matter_%28standard%29) but my requirements are fairly simple and I already have dozens of ESPHome devices so it's the path of least resistance

The microcontroller requirements are pretty simple, making pretty much anything supported by ESPHome a viable option:

1. the ability to be powered from 3x AAA batteriesireless
2. wireless connectivitysingle
3. single output pin

The [ESPHome FAQ](https://esphome.io/guides/faq.html#recommended) recommends ESP32C3 as a low power platform and the [PlatformIO supported boards](https://registry.platformio.org/platforms/platformio/espressif32/boards?version=5.3.0) lists the [Seeed Studio XIAO ESP32C3](https://docs.platformio.org/en/latest/boards/espressif32/seeed_xiao_esp32c3.html) which is small, cheap, and easy to purchase on [Amazon](https://www.amazon.com/ESP32C3-Charging-Ultra-Low-Interfaces-Engineered/dp/B0B94JZ2YF/)

# ESPHome code 

I wanted IoT squirrel ball to look like a switch in Home Assistant / HomeKit, where I would set the switch on, which would trigger the motor and speaker sequence

I described my requirements to an LLM and we ultimately came up with this YAML:

```yaml
esphome:
  name: squirrelball
  friendly_name: Squirrel Ball

esp32:
  board: seeed_xiao_esp32c3
  variant: esp32c3

logger:

api:
  encryption:
    key: <omitted>

ota:

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

# D0 = GPIO2
output:
  - platform: gpio
    pin: GPIO2
    id: output_pin

switch:
  - platform: template
    name: "Trigger"
    id: pulse_switch
    turn_on_action:
      - output.turn_on: output_pin
      - delay: 1s
      - output.turn_off: output_pin
      - switch.turn_off: pulse_switch  # Auto-reset switch
```
