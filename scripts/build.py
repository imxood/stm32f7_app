#!/usr/bin/env python3

import os
import argparse

PROJECT = "hello_world"
# PROJECT = "tests/kernel/mem_protect/mem_protect"

ZEPHYR_BASE = "/home/mx/develop/zephyrproject/zephyr"
OUTPUT = "{}/output".format(ZEPHYR_BASE)

Env = {
    'ZEPHYR_TOOLCHAIN_VARIANT': 'zephyr',
    'ZEPHYR_BASE': ZEPHYR_BASE
}

VERBOSE=0

def config():
    cmd = "cmake -H{}/{} -B{} -GNinja -DCMAKE_BUILD_TYPE=Release -DBOARD=stm32f769i_disco -DCMAKE_EXPORT_COMPILE_COMMANDS=1"
    cmd = cmd.format(ZEPHYR_BASE, PROJECT, OUTPUT)
    print("cmd: " + cmd)
    return os.system(cmd)

def build():
    cmd = "ninja -v" if VERBOSE else "ninja"
    cmd = cmd + " -C {}".format(OUTPUT)
    print("cmd: " + cmd)
    return os.system(cmd)

def clean():
    cmd = "rm -rf {}".format(OUTPUT)
    print("cmd: " + cmd)
    return os.system(cmd)

def flash():
    cmd = "ninja -C {} flash".format(OUTPUT)
    print("cmd: " + cmd)
    return os.system(cmd)


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', action='store_true', help="config project")
    parser.add_argument('-b', '--build', action='store_true', help="build project")
    parser.add_argument('-C', "--clean", action='store_true', help="clean project")
    parser.add_argument('-f', '--flash', action='store_true', help="flash")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose log")
    return parser.parse_args()


if __name__ == "__main__":

    for key in Env:
        os.environ[key] = Env[key]

    args = parse_arguments()

    if args.clean:
        clean()

    if args.config:
        if config():
            os._exit(-1)

    if args.build:
        if build():
            os._exit(-1)

    if args.flash:
        if flash():
            os._exit(-1)


