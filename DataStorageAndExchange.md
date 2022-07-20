#

## 2.1 Local storage - IO

As you know IoTEdge is based on container technology so we can access local storage in containers for IO operations. This is no different from normal container development, so you can use the storage space in the container, which is safely isolated.

![image](/img/edgestorage.png)

In addition, you may want to use physical machine local storage or load data from local disk/storage. This requires mounting local storage, so the containers can do this, of course IoT Edge can also mount external storage as well. So for mount external storage in IoT edge module its there are some different. This is done by configuring it in the deployment manifest file.

- [Give modules access to a device's local storage](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-access-host-storage-from-module?view=iotedge-2020-11)
- [IoT Edge Deployment Manifest](https://azure.github.io/Industrial-IoT/deploy/deployment-manifest.html)
- [Deployment manifest example](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11#deployment-manifest-example)

![image](/img/edgestorage-mount.png)

When you configure the mounted storage you can access it like read files from local folder on external or local storage disks. And please don't forget to configure access permissions, especially during the pre-configuration process. Sometimes we only pre-configure deployment manifest files but forget to set permissions, which will cause file path access failure.

Bash

```Bash
sudo chown 1000 <HostStoragePath>
sudo chmod 700 <HostStoragePath>
```

PowerShell

```PowerShell
$acl = get-acl <HostStoragePath>
$ace = new-object system.security.AccessControl.FileSystemAccessRule('Authenticated Users','FullControl','Allow')
$acl.AddAccessRule($ace)
$acl | Set-Acl
```

## 2.2 Share file/data between Edge module

In real engagement scenarios , customers often deploy multiple custom modules on the Edge side. So sometimes we need to consider sharing data/messages between modules. One thing come out from mind is sharing folders. ( Or you want to use the container Intranet transmission, yes this traditional way is possible, I want to introduce the use of Edge function to do this, which simpler, less code to implement.)

![image](/img/edgestorage-share.png)

We only need two steps to do this, and fortunately we did this in the previous section on sharing files.

1. As a first step we need to share the same directory with both containers so that whatever we do to this directory in one container can be easily seen in the other.
2. The second step, which is sometimes optional, is to notify another module (container) when I have done something. For example, if I create a new file and need to pass the full file path and file name to another module, or you created encrypted file requires a transfer key. So you need transform message to another one. Finally the message best for you. This message runs inside edge and is secure from the external network environment.
- [Learn how to deploy modules and establish routes in IoT Edge](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11)
- [Declare routes](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11#declare-routes)
- [Building Azure IoT Edge Module with Message Routing](https://tsmatz.wordpress.com/2019/10/19/azure-iot-hub-iot-edge-module-container-tutorial-with-message-route/)
