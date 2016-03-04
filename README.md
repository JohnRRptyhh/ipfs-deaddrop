# IPFS Dead Drop

This is the source code for an IPFS dead drop.

The IPFS dead drop is a variant of the 
USB dead drop (see https://deaddrops.com/ for more information on USB dead drops).

When you plug a USB memory into the device it will automatically access the memory 
stick and publish all the files on the web. It does so using the 
InterPlanetary File System (IPFS). Thanks to IPFS the files are instantly available
to the whole world (see http://ipfs.io/ to find out more about IPFS).

When the IPFS dead drop is finished uploading it opens a web page that displays a 
QR code that contains the IPFS address of your files. Just scan that and share the
address with anyone.

## Prerequisites

  * You need a Linux-device with udev

## How to install?

  * Copy the udev-rule-script to ``


