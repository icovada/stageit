# StageIT!

![StageIT logo](gitlab-media/logo.png?raw=true "StageIT logo")

## What
StageIT is a web-based tool to stage Cisco network devices.


It does not leverage vendor tools such as ZTP or PXE booting, instead using the pure console port, albeit exposed through telnet or SSH by a terminal server (in our case, an old Cisco 2600 with an OOB "octopus" cable)

It currently supports a [wide range of devices](Supported-devices)

## Why

The Italian team often needs to prepare devices in a staging area in the warehouse before shipping them out to multiple locations.
Multiple locations always mean different addressing, and Cisco's zero touch configuration systems require the device to be connected to its final network (or at least to clone the addressing and vlan settings in the lab)

This simply moves the effort from the device itself to the lab switch.

Staging the device completely from the console port requires no advanced configuration, no planning, no knowledge of serial numbers and vlan IDs, just plug in the console and an ethernet cable to download the firmware image should the switch need it, and you are good to go

## When

Development started in march 2019, while the project is reasonably mature there is still more to do and suggestions are welcome

## Who

Federico Tabbò (Europe) is the main developer and owner of the project. Discussion, merge requests, issue reporting and more are of course very welcome

## Where
StageIT is made out of multiple pieces. The default way to install and run it is inside a few docker containers built via docker-compose.

It is built to be able to run on a single machine, to interact with a central db or to have a central management point distributing jobs to remote workers

For more info check out the [Architecture](https://scm.dimensiondata.com/federico.tabbo/stageit/wikis/Architecture) page


## Contacts:

* **Federico Tabbò** - Main Contributor - Collaboration Engineer

## Documentation

* **[Wiki](https://scm.dimensiondata.com/federico.tabbo/stageit/wikis/home)**

## How to run

* Clone repo
* `docker-compose up`
* [http://localhost](http://localhost)

## Issues & Errors

Open an issue on scm or message me on Microsoft Teams!
