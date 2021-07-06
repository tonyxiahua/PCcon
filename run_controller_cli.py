#!/usr/bin/env python3
"""
This code have three parts 

1. Fucntions 
2. Register to main CLI
3. Main CLI

"""
import argparse
import asyncio
import logging
import os

from aioconsole import ainput

import joycontrol.debug as debug
from joycontrol import logging_default as log, utils
from joycontrol.command_line_interface import ControllerCLI
from joycontrol.controller import Controller
from joycontrol.controller_state import ControllerState, button_push, button_press, button_release
from joycontrol.memory import FlashMemory
from joycontrol.protocol import controller_protocol_factory
from joycontrol.server import create_hid_server
from joycontrol.nfc_tag import NFCTag

logger = logging.getLogger(__name__)

"""
Testing Button 
1. you can start from here to learn how to build a proper command 
"""


async def test_controller_buttons(controller_state: ControllerState):
    """
    Example controller script.
    Navigates to the "Test Controller Buttons" menu and presses all buttons.
    """
    if controller_state.get_controller() != Controller.PRO_CONTROLLER:
        raise ValueError('This script only works with the Pro Controller!')

    # waits until controller is fully connected
    await controller_state.connect()

    await ainput(prompt='Make sure the Switch is in the Home menu and press <enter> to continue.')

    """
    # We assume we are in the "Change Grip/Order" menu of the switch
    await button_push(controller_state, 'home')

    # wait for the animation
    await asyncio.sleep(1)
    """

    # Goto settings
    await button_push(controller_state, 'down', sec=1)
    await button_push(controller_state, 'right', sec=2)
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'left')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # go all the way down
    await button_push(controller_state, 'down', sec=4)
    await asyncio.sleep(0.3)

    # goto "Controllers and Sensors" menu
    for _ in range(2):
        await button_push(controller_state, 'up')
        await asyncio.sleep(0.3)
    await button_push(controller_state, 'right')
    await asyncio.sleep(0.3)

    # go all the way down
    await button_push(controller_state, 'down', sec=3)
    await asyncio.sleep(0.3)

    # goto "Test Input Devices" menu
    await button_push(controller_state, 'up')
    await asyncio.sleep(0.3)
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # goto "Test Controller Buttons" menu
    await button_push(controller_state, 'a')
    await asyncio.sleep(0.3)

    # push all buttons except home and capture
    button_list = controller_state.button_state.get_available_buttons()
    if 'capture' in button_list:
        button_list.remove('capture')
    if 'home' in button_list:
        button_list.remove('home')

    user_input = asyncio.ensure_future(
        ainput(prompt='Pressing all buttons... Press <enter> to stop.')
    )

    # push all buttons consecutively until user input
    while not user_input.done():
        for button in button_list:
            await button_push(controller_state, button)
            await asyncio.sleep(0.1)

            if user_input.done():
                break

    # await future to trigger exceptions in case something went wrong
    await user_input

    # go back to home
    await button_push(controller_state, 'home')

"""
Ensure Valid Butoon 

"""

def ensure_valid_button(controller_state, *buttons):
    """
    Raise ValueError if any of the given buttons os not part of the controller state.
    :param controller_state:
    :param buttons: Any number of buttons to check (see ButtonState.get_available_buttons)
    """
    for button in buttons:
        if button not in controller_state.button_state.get_available_buttons():
            raise ValueError(f'Button {button} does not exist on {controller_state.get_controller()}')

"""
Mash Button
Keep pressing button for a time 

"""


async def mash_button(controller_state, button, interval):
    # wait until controller is fully connected
    await controller_state.connect()
    ensure_valid_button(controller_state, button)

    user_input = asyncio.ensure_future(
        ainput(prompt=f'Pressing the {button} button every {interval} seconds... Press <enter> to stop.')
    )
    # push a button repeatedly until user input
    while not user_input.done():
        await button_push(controller_state, button)
        await asyncio.sleep(float(interval))

    # await future to trigger exceptions in case something went wrong
    await user_input

"""
This is one sample code for the Animal Crossing Buying Custom Kit Demo


"""


async def buyCustomKit(controller_state: ControllerState):
    if controller_state.get_controller() != Controller.PRO_CONTROLLER:
        raise ValueError('This script only works with the Pro Controller!')
    await controller_state.connect()
    await ainput(prompt='动森购买器 Make sure the Animal crossing in shop item and press <enter> to continue.')
    user_input = asyncio.ensure_future(
        ainput(prompt='Buying gifts... Press <enter> to stop.')
    )
    while not user_input.done():
        await button_push(controller_state, 'a')
        await button_push(controller_state, 'b')
        await asyncio.sleep(0.4)
        await button_push(controller_state, 'a')
        await button_push(controller_state, 'b')
        await asyncio.sleep(0.4)
        await button_push(controller_state, 'down')
        await button_push(controller_state, 'a')
        await button_push(controller_state, 'b')
        await asyncio.sleep(1.5)
        await button_push(controller_state, 'a')
        await button_push(controller_state, 'b')
        await asyncio.sleep(0.4)
        await button_push(controller_state, 'a')
        await button_push(controller_state, 'b')
        await asyncio.sleep(0.4)
    await user_input

"""
Drop 9 items on the empty ground.
-- TO DO
1. auto clear full backpack at 3*3n ground 
"""

async def dropBackpackItems(controller_state: ControllerState):
    if controller_state.get_controller() != Controller.PRO_CONTROLLER:
        raise ValueError('This script only works with the Pro Controller!')
    await controller_state.connect()
    await ainput(prompt='集合啦动物森友会！ You choose clear 9 items function! press <enter> to continue.')
    user_input = asyncio.ensure_future(
        ainput(prompt='Dropping items... Press <enter> to stop.')
    )
    while not user_input.done():
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.3)
        await button_push(controller_state, 'down')
        await button_push(controller_state, 'a')
        await asyncio.sleep(0.8)
        await button_push(controller_state, 'right')
        await asyncio.sleep(0.3)
    await user_input

#-------------------------------------------------------------------------------------------------------------


"""
This is important!
Remember register your edited command here!

"""
def _register_commands_with_controller_state(controller_state, cli):
    """
    Commands registered here can use the given controller state.
    The doc string of commands will be printed by the CLI when calling "help"
    :param cli:
    :param controller_state:
    """

    async def _run_ACNH_buyCustomKit(): 
        await buyCustomKit(controller_state)
    cli.add_command('buyCustomKit',_run_ACNH_buyCustomKit)
    
    
    async def _run_ACNH_dropBackpackItems(): 
        await dropBackpackItems(controller_state)
    cli.add_command('dropBackpackItems',_run_buy)

    
    async def test_buttons():
        """
        test_buttons - Navigates to the "Test Controller Buttons" menu and presses all buttons.
        """
        await test_controller_buttons(controller_state)

    cli.add_command(test_buttons.__name__, test_buttons)

    # Mash a button command
    async def mash(*args):
        """
        mash - Mash a specified button at a set interval

        Usage:
            mash <button> <interval>
        """
        if not len(args) == 2:
            raise ValueError('"mash_button" command requires a button and interval as arguments!')

        button, interval = args
        await mash_button(controller_state, button, interval)

    cli.add_command(mash.__name__, mash)

    async def click(*args):

        if not args:
            raise ValueError('"click" command requires a button!')

        await controller_state.connect()
        ensure_valid_button(controller_state, *args)

        await button_push(controller_state, *args)

    cli.add_command(click.__name__, click)

    # Hold a button command
    async def hold(*args):
        """
        hold - Press and hold specified buttons

        Usage:
            hold <button>

        Example:
            hold a b
        """
        if not args:
            raise ValueError('"hold" command requires a button!')

        ensure_valid_button(controller_state, *args)

        # wait until controller is fully connected
        await controller_state.connect()
        await button_press(controller_state, *args)

    cli.add_command(hold.__name__, hold)

    # Release a button command
    async def release(*args):
        """
        release - Release specified buttons

        Usage:
            release <button>

        Example:
            release a b
        """
        if not args:
            raise ValueError('"release" command requires a button!')

        ensure_valid_button(controller_state, *args)

        # wait until controller is fully connected
        await controller_state.connect()
        await button_release(controller_state, *args)

    cli.add_command(release.__name__, release)

    # Create nfc command
    async def nfc(*args):
        """
        nfc - Sets nfc content

        Usage:
            nfc <file_name>          Set controller state NFC content to file
            nfc remove               Remove NFC content from controller state
        """
        #logger.error('NFC Support was removed from joycontrol - see https://github.com/mart1nro/joycontrol/issues/80')
        if controller_state.get_controller() == Controller.JOYCON_L:
            raise ValueError('NFC content cannot be set for JOYCON_L')
        elif not args:
            raise ValueError('"nfc" command requires file path to an nfc dump or "remove" as argument!')
        elif args[0] == 'remove':
            controller_state.set_nfc(None)
            print('Removed nfc content.')
        else:
            controller_state.set_nfc(NFCTag.load_amiibo(args[0]))
            print("added nfc content")

    cli.add_command(nfc.__name__, nfc)

    async def pause(*args):
        """
        Pause regular input
        """
        controller_state._protocol.pause()

    cli.add_command(pause.__name__, pause)

    async def unpause(*args):
        """
        unpause regular input
        """
        controller_state._protocol.unpause()

    cli.add_command(unpause.__name__, unpause)




async def _main(args):
    # Get controller name to emulate from arguments
    controller = Controller.from_arg(args.controller)

    # parse the spi flash
    if args.spi_flash:
        with open(args.spi_flash, 'rb') as spi_flash_file:
            spi_flash = FlashMemory(spi_flash_file.read())
    else:
        # Create memory containing default controller stick calibration
        spi_flash = FlashMemory()


    with utils.get_output(path=args.log, default=None) as capture_file:
        # prepare the the emulated controller
        factory = controller_protocol_factory(controller, spi_flash=spi_flash, reconnect = args.reconnect_bt_addr)
        ctl_psm, itr_psm = 17, 19
        transport, protocol = await create_hid_server(factory, reconnect_bt_addr=args.reconnect_bt_addr,
                                                      ctl_psm=ctl_psm,
                                                      itr_psm=itr_psm, capture_file=capture_file,
                                                      device_id=args.device_id,
                                                      interactive=True)

        controller_state = protocol.get_controller_state()

        # Create command line interface and add some extra commands
        cli = ControllerCLI(controller_state)
        _register_commands_with_controller_state(controller_state, cli)
        cli.add_command('amiibo', ControllerCLI.deprecated('Command was removed - use "nfc" instead!'))
        cli.add_command(debug.debug.__name__, debug.debug)

        # set default nfc content supplied by argument
        if args.nfc is not None:
            await cli.commands['nfc'](args.nfc)

        # run the cli
        try:
            await cli.run()
        finally:
            logger.info('Stopping communication...')
            await transport.close()

"""
Main function configure
"""


if __name__ == '__main__':
    # check if root
    if not os.geteuid() == 0:
        raise PermissionError('Script must be run as root!')

    # setup logging
    #log.configure(console_level=logging.ERROR)
    log.configure()

    parser = argparse.ArgumentParser()
    parser.add_argument('controller', help='JOYCON_R, JOYCON_L or PRO_CONTROLLER')
    parser.add_argument('-l', '--log', help="BT-communication logfile output")
    parser.add_argument('-d', '--device_id', help='not fully working yet, the BT-adapter to use')
    parser.add_argument('--spi_flash', help="controller SPI-memory dump to use")
    parser.add_argument('-r', '--reconnect_bt_addr', type=str, default=None,
                        help='The Switch console Bluetooth address (or "auto" for automatic detection), for reconnecting as an already paired controller.')
    parser.add_argument('--nfc', type=str, default=None, help="amiibo dump placed on the controller. Äquivalent to the nfc command.")
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        _main(args)
    )
