# Copyright (c) Microsoft. All rights reserved.
# Licensed under the MIT license. See LICENSE file in the project root for
# full license information.

import time
import os
import sys
import zipfile
import asyncio
import hashlib, base64
from six.moves import input
import threading
import requests
from azure.iot.device.aio import IoTHubModuleClient

async def main():
    try:
        if not sys.version >= "3.5.3":
            raise Exception( "The sample requires python 3.5.3+. Current version of Python: %s" % sys.version )
        print ( "IoT Hub Client for Python" )

        # The client object is used to interact with your Azure IoT hub.
        module_client = IoTHubModuleClient.create_from_edge_environment()

        # connect the client.
        await module_client.connect()

        
        def get_filename_and_ext(filename):
            (filepath,tempfilename) = os.path.split(filename);
            (shotname,extension) = os.path.splitext(tempfilename);
            return shotname,extension

        def unzip_file(unZipSrc,targeDir):
            if not os.path.isfile(unZipSrc):
                raise Exception(u'unZipSrc not exists:{0}'.format(unZipSrc))
            if not os.path.isdir(targeDir):
                os.makedirs(targeDir)
            print(u'######## Start decompressing the file: {0}'.format(unZipSrc))
            unZf = zipfile.ZipFile(unZipSrc,'r')
            for name in unZf.namelist() :
                unZfTarge = os.path.join(targeDir,name)

                if unZfTarge.endswith("/"):
                    #empty dir
                    splitDir = unZfTarge[:-1]
                    if not os.path.exists(splitDir):
                        os.makedirs(splitDir)
                else:
                    splitDir,_ = os.path.split(targeDir)
                    if not os.path.exists(splitDir):
                        os.makedirs(splitDir)
                    hFile = open(unZfTarge,'wb')
                    hFile.write(unZf.read(name))
                    hFile.close()
            print(u'######## Unzipped. Target file directory: {0}'.format(targeDir))
            unZf.close()

        def content_encoding(path: str):
            with open(path, 'rb') as f:
                content = f.read()
            content_md5 = hashlib.md5()
            content_md5.update(content)
            content_base64 = base64.b64encode(content_md5.digest())
            return content_base64.decode("utf-8")

        # define behavior for receiving a twin patch
        async def twin_patch_handler(patch):
            try:
                print( "######## The data in the desired properties patch was: %s" % patch)
                if "FileName" in patch:
                    FileName = patch["FileName"]
                if "DownloadUrl" in patch:
                    DownloadUrl = patch["DownloadUrl"]
                if "ContentMD5" in patch:
                    ContentMD5 = patch["ContentMD5"]
                # print ( "FilePath is: %s\n" % FilePath )
                # print ( "DownloadUrl is: %s\n" % DownloadUrl )
                FilePath = "/iotedge/storage/" + FileName
                # download AI model
                r = requests.get(DownloadUrl)

                print ("######## response code: " + str(r.status_code))

                if r.status_code is not 200:
                    print ("######## download AI Model failed please check DownloadUrl response code: " + str(r.status_code))
                    return

                print ("######## download AI Model Succeeded.")
                ffw = open(FilePath, 'wb')
                ffw.write(r.content)
                ffw.close()
                print ("######## AI Model File: " + FilePath)

                # # message to iot hub
                # print ( "######## Send message to iot hub")
                # await module_client.send_message_to_output("message from AML module FilePath is: " + FilePath, "IoTHubMeg")

                # MD5 checksum
                md5str = content_encoding(FilePath)
                if md5str == ContentMD5:
                    print ( "######## New AI Model MD5 checksum succeeded")
                    # decompressing the ZIP file
                    unZipSrc = FilePath
                    targeDir = "/iotedge/storage/"
                    filenamenoext = get_filename_and_ext(unZipSrc)[0]
                    targeDir = targeDir + filenamenoext
                    unzip_file(unZipSrc,targeDir)

                    model_name = ""
                    labelmap_name =""
                    for files in os.listdir(targeDir):
                        if '.tflite' in files:
                            model_name = files
                        if '.txt' in files:
                            labelmap_name = files

                    # message to module
                    print ( "######## Send AI Model Info AS Routing Message")
                    data = "{\"local_model_path\": \"%s\",\"local_labelmap_path\": \"%s\"}" % (filenamenoext+"/"+model_name, filenamenoext+"/"+labelmap_name)
                    await module_client.send_message_to_output(data, "DLModelOutput")
                    # update the reported properties
                    reported_properties = {"LatestAIModelFileName": FileName }
                    print("######## Setting reported LatestAIModelName to {}".format(reported_properties["LatestAIModelFileName"]))
                    await module_client.patch_twin_reported_properties(reported_properties)
                else:
                    print ( "######## New AI Model MD5 checksum failed")

            except Exception as ex:
                print ( "Unexpected error in twin_patch_handler: %s" % ex )

        # set the twin patch handler on the client
        module_client.on_twin_desired_properties_patch_received = twin_patch_handler

        # define behavior for halting the application
        def stdin_listener():
            while True:
                try:
                    selection = input("Press Q to quit\n")
                    if selection == "Q" or selection == "q":
                        print("Quitting...")
                        break
                except:
                    time.sleep(60*30)

        # Run the stdin listener in the event loop
        loop = asyncio.get_event_loop()
        user_finished = loop.run_in_executor(None, stdin_listener)

        # Wait for user to indicate they are done listening for messages
        await user_finished

        # Finally, disconnect
        await module_client.disconnect()

    except Exception as e:
        print ( "Unexpected error %s " % e )
        raise

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()

    # If using Python 3.7 or above, you can use following code instead:
    # asyncio.run(main())