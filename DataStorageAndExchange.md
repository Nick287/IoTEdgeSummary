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

In real engagement scenarios, customers often deploy multiple custom modules on the Edge side. So sometimes we need to consider sharing data/messages between modules. One thing come out from mind is sharing folders. ( Or you want to use the container Intranet transmission, yes this traditional way is possible, I want to introduce the use of Edge function to do this, which simpler, less code to implement.)

![image](/img/edgestorage-share.png)

We only need two steps to do this, and fortunately we did this in the previous section on sharing files.

1. As a first step we need to share the same directory with both containers so that whatever we do to this directory in one container can be easily seen in the other.
2. The second step, which is sometimes optional, is to notify another module (container) when I have done something. For example, if I create a new file and need to pass the full file path and file name to another module, or you created encrypted file requires a transfer key. So you need transform message to another one. Finally the message best for you. This message runs inside edge and is secure from the external network environment.

- [Learn how to deploy modules and establish routes in IoT Edge](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11)
- [Declare routes](https://docs.microsoft.com/en-us/azure/iot-edge/module-composition?view=iotedge-2020-11#declare-routes)
- [Building Azure IoT Edge Module with Message Routing](https://tsmatz.wordpress.com/2019/10/19/azure-iot-hub-iot-edge-module-container-tutorial-with-message-route/)

## 2.3 Local database SQL server

In some cases, your customers may need to store their data locally and their system is based on SQL so have to access some legacy database, such as MS SQL, MYSQL, or PostgreSQL. However, there are now containerized SQL databases, so Azure IoT Edge can also deploy SQL and support Module access.
You can use code to connect to a database connect. You'll then run a Transact-SQL statement to query data.

For example, if you are familiar with C# you mast know the library [System.Data.SqlClient](https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-dotnet-core?view=azuresql), You can use it to access the database

```csharp
using System;
using System.Data.SqlClient;
using System.Text;

namespace sqltest
{
    class Program
    {
        static void Main(string[] args)
        {
            try 
            { 
                SqlConnectionStringBuilder builder = new SqlConnectionStringBuilder();

                builder.DataSource = "<your_server.database.windows.net>"; 
                builder.UserID = "<your_username>";            
                builder.Password = "<your_password>";     
                builder.InitialCatalog = "<your_database>";
         
                using (SqlConnection connection = new SqlConnection(builder.ConnectionString))
                {
                    Console.WriteLine("\nQuery data example:");
                    Console.WriteLine("=========================================\n");
                    
                    connection.Open();       

                    String sql = "SELECT name, collation_name FROM sys.databases";

                    using (SqlCommand command = new SqlCommand(sql, connection))
                    {
                        using (SqlDataReader reader = command.ExecuteReader())
                        {
                            while (reader.Read())
                            {
                                Console.WriteLine("{0} {1}", reader.GetString(0), reader.GetString(1));
                            }
                        }
                    }                    
                }
            }
            catch (SqlException e)
            {
                Console.WriteLine(e.ToString());
            }
            Console.WriteLine("\nDone. Press enter.");
            Console.ReadLine(); 
        }
    }
}
```

Or maybe you're a Python developer you mast know [pyodbc](https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-python?view=azuresql)

```python
import pyodbc
server = '<server>.database.windows.net'
database = '<database>'
username = '<username>'
password = '{<password>}'   
driver= '{ODBC Driver 17 for SQL Server}'

with pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password) as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT TOP 3 name, collation_name FROM sys.databases")
        row = cursor.fetchone()
        while row:
            print (str(row[0]) + " " + str(row[1]))
            row = cursor.fetchone()
```

Of course, other develop languages also have library to access SQL databases that you can use freely.

Next you can deploy a containerized SQL database to Edge

[Tutorial: Store data at the edge with SQL Server databases](https://docs.microsoft.com/en-us/azure/iot-edge/tutorial-store-data-sql-server?view=iotedge-2020-11#deploy-the-solution-to-a-device)

Or SQL container is part of an on-premise solution, and I used a similar scenario in a project.

[Azure IoT Edge On-Premise Solution](https://github.com/Nick287/AzureIoTEdgeOnPremiseSolution)

## 2.4 Sync data between cloud and Edge device

Sometimes we need to sync messages between the device and IoThub. There are two main message transmission modes: C2D(Cloud-to-device) D2C(Device-to-cloud) and Module Twin.

[__C2D (Cloud-to-device)__](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-c2d-guidance)

[Direct methods](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-direct-methods) for communications that require immediate confirmation of the result. Direct methods are often used for interactive control of devices such as turning on a fan.

[Twin's desired](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-device-twins) properties for long-running commands intended to put the device into a certain desired state. For example, set the telemetry send interval to 30 minutes.

[Cloud-to-device](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-c2d) messages for one-way notifications to the device app.

[__D2C (Device-to-cloud)__](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-d2c-guidance)

[Device-to-cloud](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-d2c) messages for time series telemetry and alerts.

[Device twin's reported properties](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-device-twins) for reporting device state information such as available capabilities, conditions, or the state of long-running workflows. For example, configuration and software updates.

[File uploads](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-file-upload) for media files and large telemetry batches uploaded by intermittently connected devices or compressed to save bandwidth.

In practical projects we are often most concerned about 2 key factor of message.

1. First is the size of the message of capacity.
   1. Direct methods payload size is 128 KB for the request and 128 KB for the response.
   2. Twin's desired properties Maximum desired properties size is 32 KB. And Maximum reported properties size is 32 KB.
   3. Cloud-to-device messages size Up to 64 KB messages. Device-to-cloud messages size Up to 256-KB messages.
2. Second stability.
   1. All messages are delivered immediately when the device is online.
   2. The Device Twin caches messages on the cloud (IoTHub) or Edge and synchronizes messages automatically when the device comeback online.
   3. Other ways you need to consider routing or how to handle offline scenarios.

Therefore, if you only need data synchronization, Twin may be the best choice. If you want to query the real-time status of the Device please consider [Direct methods](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-direct-methods) . If you want to route messages, please use [Device-to-cloud](https://docs.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-messages-d2c) messages.

![image](/img/edgestorage-twin.png)

As I mentioned above, messages are limited in size, so consider using blob or type services to host content when transferring large files between Edge devices and the cloud.

Two options

Option 1 you can access cloud resources directly in the Edge Module using the [blob SDK](https://docs.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=environment-variable-windows), whether upload or download data. but make sure your Edge device is online.

Option 2 [deviceToCloudUpload](https://docs.microsoft.com/en-us/azure/iot-edge/how-to-store-data-blob?view=iotedge-2020-11) is a configurable functionality. This function automatically uploads the data from your local blob storage to Azure with intermittent internet connectivity support.
