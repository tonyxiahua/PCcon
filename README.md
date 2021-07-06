# 任天堂Switch自动手柄 V0.0.1_07052021_Alpha

一款任天堂Switch 第三方蓝牙控制器
使用电脑的蓝牙模拟Switch 的手柄来控制游戏。
我已经成功在动森部署了自动化购买器。
成功在树莓派4B部署。Razer Blade Pro 17 Intel 虚拟机蓝牙配置成功。

## 功能
* 模拟所有按键和摇杆
* 连发按键
* 模拟 NFC 读取功能

## 安装步骤
Linux 下面的Raspbian:
```bash
sudo apt install python3-dbus libhidapi-hidraw0 libbluetooth-dev bluez
```
```bash
sudo pip3 install aioconsole hid crc8
```
打开程序
```bash
sudo python3 run_controller_cli.py -r PRO_CONTROLLER
```
这个时候打开你的switch 进入需要你按下手柄LR 的时候的界面。
过一会应该会成功找到一个pro controller。

等连接成功了就输入 Enter 进入Command Line 大概是这样的一个界面
```bash
cmd >> 
```

## 蓝牙配置（适用于系统12.0.0 以上 最新系统）
- 关闭 SDP [只有在匹配的时候需要]
  改变 `ExecStart` 在 `/lib/systemd/system/bluetooth.service` 里面的数值为： `ExecStart=/usr/lib/bluetooth/bluetoothd -C -P sap,input,avrcp`
  这个会关闭现有的蓝牙连接使匹配过程更纯粹。如果发现对你现在的设备有任何问题。
  
- 关闭输入模块（可选，如果你只在虚拟机搞事情的话我就不理这一部分了）
改变 `ExecStart` 在 `/lib/systemd/system/bluetooth.service` 里面的数值为： `ExecStart=/usr/lib/bluetooth/bluetoothd -C -P input` 


- 重启服务们
  ```bash
    sudo systemctl daemon-reload
    sudo systemctl restart bluetooth.service
  ```
[更多问题请查询](https://github.com/Poohl/joycontrol/issues/4) 

## run_controller_cli.py 常用的命令
我就按照最普通的来，就是运行
```bash
sudo python3 run_controller_cli.py -r PRO_CONTROLLER
```

下面的更多内容你可以参考一下

```
usage: run_controller_cli.py [-h] [-l LOG] [-d DEVICE_ID]
                             [--spi_flash SPI_FLASH] [-r RECONNECT_BT_ADDR]
                             [--nfc NFC]
                             controller

positional arguments:
  controller            JOYCON_R, JOYCON_L or PRO_CONTROLLER

optional arguments:
  -h, --help            show this help message and exit
  -l LOG, --log LOG     BT-communication logfile output
  -d DEVICE_ID, --device_id DEVICE_ID
                        not fully working yet, the BT-adapter to use
  --spi_flash SPI_FLASH
                        controller SPI-memory dump to use
  -r RECONNECT_BT_ADDR, --reconnect_bt_addr RECONNECT_BT_ADDR
                        The Switch console Bluetooth address (or "auto" for
                        automatic detection), for reconnecting as an already
                        paired controller.
  --nfc NFC             amiibo dump placed on the controller. Equivalent to
                        the nfc command.
```

如果你之前已经连接过了自己的Switch的话，你需要做的事情是在启动脚本后面加上 `-r auto` 或者  `-r <Switch Bluetooth Mac address>`

## API 接口 （我个人不觉得是）
代码我放这里了，读得懂就改吧。
```python
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from joycontrol.controller import Controller

# the type of controller to create
controller = Controller.PRO_CONTROLLER # or JOYCON_L or JOYCON_R
# a callback to create the corresponding protocol once a connection is established
factory = controller_protocol_factory(controller)
# start the emulated controller
transport, protocol = await create_hid_server(factory)
# get a reference to the state beeing emulated.
controller_state = protocol.get_controller_state()
# wait for input to be accepted
await controller_state.connect()
# some sample input
controller_state.button_state.set_button('a', True)
# wait for it to be sent at least once
await controller_state.send()
```

## 已知问题
- 有一些蓝牙接收器并不是接受很好，尝试使用USB 接收器或者使用树莓派系统。[Issue #8](https://github.com/mart1nro/joycontrol/issues/8)
- 一堆疑难杂症……
- Plan，Code，Build，Test，Release，Deploy，Operate···

## 感谢
- 特别感谢： https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering 的控制器逆向工程文件
- 感谢各位看到这里的人以及各位贡献者。

## 可能对你二次开发有用的资源（GNU协议请遵守）

[Nintendo_Switch_Reverse_Engineering](https://github.com/dekuNukem/Nintendo_Switch_Reverse_Engineering)

[console_pairing_session](https://github.com/timmeh87/switchnotes/blob/master/console_pairing_session)

[Hardware Issues thread](https://github.com/Poohl/joycontrol/issues/4)
