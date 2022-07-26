#

## Devops

### Package images and upload to container registry

During development we often need setup CICD pipeline compile and deploy the Edge Module image to the test stage and dev environment. So I would like to share here, how to this in [ADO](https://azure.microsoft.com/en-us/services/devops/#overview). If you not familiar with ADO please read [this](https://azure.microsoft.com/en-us/services/devops/pipelines/)， understand the concept of pipeline.

In the IoT Edge official IoT Edge documentation introduced built-in [Azure IoT Edge tasks](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/build/azure-iot-edge?view=azure-devops) It compiles and uploads images and deploys images to Edge devices.

You can follow this document and try it out in your ADO subsection first [Continuous integration and continuous deployment to Azure IoT Edge devices](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-continuous-integration-continuous-deployment?view=iotedge-2020-11)

Action | Description
:---| :---
Build module images | Takes your IoT Edge solution code and builds the container images.
Push module images| Pushes module images to the container registry you specified.
Generate deployment manifest |  Takes a deployment.template.json file and the variables, then generates the final IoT Edge deployment manifest file.
Deploy to IoT Edge devices | Creates IoT Edge deployments to one or more IoT Edge devices.

### Package of multiple images

However, I am used to using standard [Docker Task](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/build/docker?view=azure-devops&tabs=yaml) when compiling Docker image. Because he has more parameters to work with.

For example, This is really easy when you want to Tag your docker image. It is also easier if you add parameters or specify code levels when compiling the image.

If you only want to compile and upload images in the CI pipeline, there is no need to run the Edge CLI task. This saves time on your pipeline

Parameter|Required or optional|Description
:---| :---| :---
tags Tags|Optional|Multiline input where each line contains a tag to be used in build, push, or buildAndPush commands.Default value: $(Build.BuildId)
Dockerfile Dockerfile|Optional|Path to the Dockerfile. The task will use the first Dockerfile that it finds to build the image.Default value: **/Dockerfile
buildContext Build context|Optional|Path to the build context.Default value: **
arguments Arguments|Optional|Additional arguments to be passed onto the Docker client.Be aware that if you use the value buildAndPush for the command parameter, the arguments property will be ignored.

simple code [Build_and_Push_Docker_Image.yml](https://dev.azure.com/CSECodeHub/435025%20-%20Telstra%20-%20MLOps%20for%20Smart%20Video%20Platform%20LVA/_git/smart-video-mlops?path=/devops/IoTEdge/templates/Build_and_Push_Docker_Image.yml)

```yaml
parameters:
  - name: buildContext
    type: string
  - name: Dockerfile
    type: string
  - name: AppName
    type: string
  - name: ACR
    type: string
  - name: ImageTag
    type: string

steps:
  - task: Docker@2
    displayName: Docker login
    inputs:
      containerRegistry: ${{ parameters.ACR }}
      command: 'login'

  - task: Docker@2
    displayName: Build and Push Docker Image
    inputs:
      command: buildAndPush
      buildContext: ${{ parameters.buildContext }}
      Dockerfile: ${{ parameters.Dockerfile }}
      repository: ${{ parameters.AppName }}
      containerRegistry: ${{ parameters.ACR }}
      tags: ${{ parameters.ImageTag }}
```

If you have multiple Docker images you can use multiple __jobs__ to call this Docker task which can compile multiple images in parallel

![image](/img/pipelinebuildimage.png)

Template points to the Build_and_Push_Docker_Image.yml

```yaml
jobs:
  - job: BuildDockerImagegrpcExtension
    pool:
      vmImage: "ubuntu-latest"
    displayName: "Build Image 001"
    steps:
      - template: templates/Build_and_Push_Docker_Image.yml
        parameters:
          AppName: modules/grpcExtension
          ACR: $(IMG_CONTAINER_REGISTRY_SVC_CONNECTION)
          buildContext: edgesmartvideo/modules/grpcExtension
          Dockerfile: edgesmartvideo/modules/grpcExtension/docker/Dockerfile
          ImageTag: $(Build.BuildId)

  - job: BuildDockerImageDownloaderModule
    pool:
      vmImage: "ubuntu-latest"
    displayName: "Build Image 002"
    steps:
      - template: templates/Build_and_Push_Docker_Image.yml
        parameters:
          AppName: modules/DownloaderModule
          ACR: $(IMG_CONTAINER_REGISTRY_SVC_CONNECTION)
          buildContext: edgesmartvideo/modules/DownloaderModule
          Dockerfile: edgesmartvideo/modules/DownloaderModule/Dockerfile.amd64
          ImageTag: $(Build.BuildId)
```

### ImageTag Used for version control

You can set it as a parameter to the pipeline __$(Build.BuildId)__.

```yaml
jobs:
  - job: BuildDockerImage
    pool:
      vmImage: "ubuntu-latest"
    displayName: "Build Image 001"
    steps:
      - template: templates/Build_and_Push_Docker_Image.yml
        parameters:
          AppName: modules/grpcExtension
          ACR: $(IMG_CONTAINER_REGISTRY_SVC_CONNECTION)
          buildContext: /modules/grpcExtension
          Dockerfile: /docker/Dockerfile
          ImageTag: $(Build.BuildId)
```

### Edge module image Deployment

The redeployment of the Edge Module is based on the Build Edge Deployment Manifest file, so we need to use the [task Generate Deployment Manifest](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/build/azure-iot-edge?view=azure-devops#generate-deployment-manifest)

```yaml
steps:    
- task: AzureIoTEdge@2
  displayName: AzureIoTEdge - Generate deployment manifest
  inputs:
    action: Generate deployment manifest
    templateFilePath: deployment.template.json
    defaultPlatform: amd64
    deploymentManifestOutputPath: $(System.DefaultWorkingDirectory)/config/deployment.json
    validateGeneratedDeploymentManifest: false
```

[Task Deploy to IoT Edge Devices](https://docs.microsoft.com/en-us/azure/devops/pipelines/tasks/build/azure-iot-edge?view=azure-devops#deploy-to-iot-edge-devices) is required to Deploy to Edge Device.

```yaml
steps:
- task: AzureIoTEdge@2
  displayName: 'Azure IoT Edge - Deploy to IoT Edge devices'
  inputs:
    action: 'Deploy to IoT Edge devices'
    deploymentFilePath: $(System.DefaultWorkingDirectory)/config/deployment.json
    azureSubscription: $(azureSubscriptionEndpoint)
    iothubname: iothubname
    deploymentid: '$(System.TeamProject)-devops-deployment'
    priority: '0'
    deviceOption: 'Single Device'
    deviceId: deviceId
```

According to these two tasks, we can build a E2E CICD pipeline to generate the [deployment manifest file](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11#create-a-deployment-manifest) and send it to IoTHub for Edge device deployment.

ADO Pipeline running looks like this below

![image](/img/pipeline.png)

The complete YAML code for the pipeline is shared [here](https://dev.azure.com/CSECodeHub/435025%20-%20Telstra%20-%20MLOps%20for%20Smart%20Video%20Platform%20LVA/_git/smart-video-mlops?path=/devops/IoTEdge/02-ava-edge-deploy.yml)
