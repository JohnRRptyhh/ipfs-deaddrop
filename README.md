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

![Welcome screen](https://ipfs.io/ipfs/QmTv7K8z3JkcL3rfsYdtwm2bWdMBCHZCQNNggjY9xuniqM) ![Results screen](https://ipfs.io/ipfs/QmbKYuuaUDqLCSoH1srcSwLaiVqwtZm2DA1ihGsgkpqGQR)

## How to use?

  * Bring a USB memory stick (FAT-formatted) with the file(s) you want to share and smartphone with a QR code scanner app.
  * Plug a USB memory stick into the dead drop host.
  * Wait ca. 5 seconds until the dead drop starts copying your files.
  * Wait until the whole process is complete. The QR code will be shown once it is completed.
  * Scan the QR code with your mobile and share the URL with your friends.
     * The QR code contains the content hash that you need to access your files using IPFS.

## Prerequisites

  * You need a Linux-device with udev
  * IPFS should be installed and your local system should be a IPFS node (e.g. you should be able to add files using `ipfs add ...`).

## How to install?

  * Copy the udev-rule-script to `/etc/udev/rules.d/mount.rules`
  * Reload your udev rules afterwards: `udevadm control --reload-rules`
  * Copy the dumper script to `/usr/local/bin/dumpusb` and edit it to configure to your needs.
  * Make sure the a copy of the QR code page is available by pinning it to your local IPFS node. Currently with `ipfs pin add QmUzER8RFyFMKfcE5WKcCWdK1pFXJMVKoCzeHEw2XWpibA`.

## Mirroring

It is easy to set up a mirror of the dead drops using [ipfs-ringpin](https://github.com/c-base/ipfs-ringpin). The IPNS address for c-base's Siri is:

```
/ipns/QmdCYibjHMinqnh7eWw8WEMsopi5CWz5yD2R86nYegL2Sr/pinlist/deaddrop
```
