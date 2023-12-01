# RIO 201 project

## Introduction

The objective of this project is to implement an IoT application. The IoT should uses several sensors and requests.
We should use the [IoT Lab](https://www.iot-lab.info/).

To simplify the task for the IoT lab deployment, we used the enoslib library.

\newpage

## Architecture

![Architecture](./img/archi.png)

This architecture is composed of 3 parts:

- Data collection
- Threshold for the autonomous actuator
- Alarm

### Data collection

The first part of this diagram is the data collection. It is composed of 2 captors. The server make a request to the captors to get the data every minutes.
Then we retreive the data and display it on a graph.
As we want to compare both HTTP and COAP, each captor is using a different protocol.

### Threshold for the autonomous actuator

The autonomous captor is a captor that can move. We can set a threshold from the server. If the captor is above the threshold, it will stop.

In a real application this captor would be an actuator.

Randomly, the server set a threshold using by making a request from the server to an the autonomous actuator. The autonomous actuator will then stop the motor if the threshold is above the threshold.

### Alarm

The final part is an alarm, this alarm is made by an alarm sensor. To be realistic, this alarm can be trigerred from the SSH connection using a COAP request. Another solution would be to use a button to trigger the alarm or randomly trigger it.
When the alarm is triggered, the alarm is sent to the which can display an alert.

\newpage

## Demonstration

All the code is available on this github repository: [https://github.com/Its-Just-Nans/rio201](https://github.com/Its-Just-Nans/rio201)

As explained previously, we used the enoslib library. It's a python library (made by the INRIA research center) that allows to deploy IoT lab experiments.

The repo is available on the INRIA gitlab [https://gitlab.inria.fr/discovery/enoslib](https://gitlab.inria.fr/discovery/enoslib).

During the project, I had to fix some bug in the library.

The pull request is available on online: [https://gitlab.inria.fr/discovery/enoslib/-/merge_requests/214](https://gitlab.inria.fr/discovery/enoslib/-/merge_requests/214).

To deploy our experiment, we just need to provide a correct configuration schema and the correct images to flash.

First we need to install the enoslib and to setup the authentification file.

```sh
# download dependencies
python -m pip install enoslib[iotlab]

# create the auth file
ENC_PASS=$(printf '%s' pass | base64)
echo -n user:$ENC_PASS > ~/.iotlabrc
```

In the configuration object of enoslib, if we want to reserve a node, we have two solutions.

The first solution is to use a random device, to do that, we can specify a node like this:

```python
machines = [
    {
        "roles": ["sensor", "mysensor"],
        "archi": "m3:at86rf231",
        "site": "lille",
        "number": 1,
        "image": path_to_image,
    },
]
```

To reserve a specific node that we know, we can reserve it using his name :

```python
machines = [
    {
        "roles": ["sensor", "mysensor"],
        "hostname": ["m3-66.lille.iot-lab.info"],
        "image": path_to_image,
    },
]
```

After creating the configuration, we can deploy our experiment:

```python
conf = en.IotlabConf.from_dictionary(provider_conf)
p = en.Iotlab(conf)
roles, networks = p.init()
```

Then we can use the roles from the configuration to get the node we want and use them. For example, we can access to the serial connection

```python
sender = roles["mysensor"][0]
with en.IotlabSerial(sender, interactive=True) as sender:
    data = sender.read()
    print(data)
```

Finally we can automatically clear the experiment:

```python
try:
    roles, networks = p.init()
    # do something
except Exception as e:
    print(e)
finally:
    p.shutdown()
```

\newpage

## Conclusion

This project was very interesting. We learned a lot about the IoT lab and the enoslib library. We also learned how to use the IoT lab and how to deploy an IoT application on it.
