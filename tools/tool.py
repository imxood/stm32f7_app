#!/usr/bin/env python3

import os
import sys
import argparse
import json
import re

PROJECT = "stm32f7_app"
# PROJECT = "tests/kernel/mem_protect/mem_protect"
# PROJECT = "samples/hello_world"

ZEPHYR_BASE = "{}/develop/sources/zephyrproject/zephyr".format(
    os.environ.get("HOME"))

OUTPUT = "{}/w_output".format(ZEPHYR_BASE)

Env = {
    'ZEPHYR_TOOLCHAIN_VARIANT': 'zephyr',
    'ZEPHYR_BASE': ZEPHYR_BASE
}

VERBOSE = 0


C_CPP_PROPERTIES = '''
{
    "configurations": [
        {
            "name": "Linux",
            "includePath": [
                "${workspaceFolder}/**"
            ],
            "defines": [],
            "compilerPath": "/usr/bin/gcc",
            "cStandard": "c11",
            "cppStandard": "c++17",
            "intelliSenseMode": "clang-x64"
        }
	],
	"version": 4
}
'''

SETTINGS_TEMPLATE = '''
{
	"cortex-debug.openocdPath": "${env:ZEPHYR_SDK_INSTALL_DIR}/sysroots/x86_64-pokysdk-linux/usr/bin/openocd",
	"editor.fontSize": 16,
    "terminal.integrated.fontSize": 16,
    "editor.mouseWheelZoom": true,
    "editor.renderWhitespace": "all",
    "editor.fontFamily": "文泉驿等宽微米黑",
    "terminal.integrated.fontFamily": "文泉驿等宽微米黑"
}
'''

LAUNCH_TEMPLATE = '''
{
    "version": "0.2.0",
	"configurations": []
}
'''

LAUNCH_CORTEX_DEBUG = '''
{
    "type": "cortex-debug",
    "request": "launch",
    "servertype": "openocd",
    "cwd": "${workspaceRoot}",
    "executable": "./w_output/zephyr/zephyr.elf",
    "name": "Stm32f7 Debug",
    "device": "STM32F7",
    "configFiles": [
        "board/stm32f7discovery.cfg"
    ]
}
'''


# 创建一个xstr类，用于处理从文件中读出的字符串
class xstr:

    def __init__(self, instr):
        self.instr = instr

    # 删除“//”标志后的注释
    def rmCmt(self):
        qtCnt = cmtPos = slashPos = 0
        rearLine = self.instr
        # rearline: 前一个“//”之后的字符串，
        # 双引号里的“//”不是注释标志，所以遇到这种情况，仍需继续查找后续的“//”
        while rearLine.find('//') >= 0: # 查找“//”
            slashPos = rearLine.find('//')
            cmtPos += slashPos
            # print 'slashPos: ' + str(slashPos)
            headLine = rearLine[:slashPos]
            while headLine.find('"') >= 0: # 查找“//”前的双引号
                qtPos = headLine.find('"')
                if not self.isEscapeOpr(headLine[:qtPos]): # 如果双引号没有被转义
                    qtCnt += 1 # 双引号的数量加1
                headLine = headLine[qtPos+1:]
                # print qtCnt
            if qtCnt % 2 == 0: # 如果双引号的数量为偶数，则说明“//”是注释标志
                # print self.instr[:cmtPos]
                return self.instr[:cmtPos]
            rearLine = rearLine[slashPos+2:]
            # print rearLine
            cmtPos += 2
        # print self.instr
        return self.instr

    # 判断是否为转义字符
    def isEscapeOpr(self, instr):
        if len(instr) <= 0:
            return False
        cnt = 0
        while instr[-1] == '\\':
            cnt += 1
            instr = instr[:-1]
        if cnt % 2 == 1:
            return True
        else:
            return False

def loadJson(JsonPath):
    try:
        srcJson = open(JsonPath, 'r')
    except:
        print('cannot open ' + JsonPath)
        quit()

    dstJsonStr = ''
    for line in srcJson.readlines():
        if not re.match(r'\s*//', line) and not re.match(r'\s*\n', line):
            xline = xstr(line)
            dstJsonStr += xline.rmCmt()

    # print dstJsonStr
    dstJson = None
    try:
        dstJson = json.loads(dstJsonStr)
    except:
        print(JsonPath + ' is not a valid json file')
    return dstJson


def get_real_path(output, path):
    return path if os.path.isabs(path) else os.path.realpath(output + '/' + path)


def update_c_cpp_properties():

    compile_file = "{}/compile_commands.json".format(OUTPUT)

    defines = set()
    includePath = set()
    forcedInclude = set()

    if os.path.exists(compile_file):
        data = loadJson(compile_file)
        for compile_item in data:
            if os.path.splitext(compile_item['file'])[-1].lower() == ".s":
                continue
            command = compile_item['command']
            defines = defines | set(map(lambda x: x[2:], filter(
                lambda x: x.startswith('-D'), command.split())))
            includePath = includePath | set(map(lambda x: get_real_path(
                OUTPUT, x[2:]), filter(lambda x: x.startswith('-I'), command.split())))

    for path in ('zephyr/include/generated/autoconf.h', 'zephyr/include/generated/generated_dts_board_fixups.h', 'zephyr/include/generated/generated_dts_board_unfixed.h'):
        path = get_real_path(OUTPUT, path)
        forcedInclude.add(path)

    autoconf_file = "{}/zephyr/include/generated/autoconf.h".format(OUTPUT)

    if os.path.exists(autoconf_file):
        with open(autoconf_file, 'r') as f:
            for line in f.readlines():
                parts = line.split()
                if len(parts) == 3:
                    defines.add("{}={}".format(parts[1], parts[2]))

    if len(defines) == 0:
        return

    config_file = "{}/.vscode/c_cpp_properties.json".format(ZEPHYR_BASE)

    data = json.loads(C_CPP_PROPERTIES)

    json_defines = data['configurations'][0]['defines']
    json_defines.extend(defines)

    # json_includePath = data['configurations'][0]['includePath']
    # json_includePath.extend(includePath)

    # json_browsePath = data['configurations'][0]['browse']['path']
    # json_browsePath.extend(includePath)

    # json_forcedInclude = data['configurations'][0]['forcedInclude']
    # json_forcedInclude.extend(forcedInclude)

    # data['configurations'][0]['compileCommands'] = "{}/compile_commands.json".format(OUTPUT)

    with open(config_file, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def update_settings():

    settings_data = None
    settings_file = "{}/.vscode/settings.json".format(ZEPHYR_BASE)

    if os.path.exists(settings_file):
        try:
            settings_data = loadJson(settings_file)
        except json.decoder.JSONDecodeError as err:
            print("json load file '{}' Error: {}".format(settings_file, err))

    settings_configue = json.loads(SETTINGS_TEMPLATE)

    if settings_data == None:
        settings_data = settings_configue
    else:
        settings_data.update(settings_configue)

    with open(settings_file, 'w') as f:
        json.dump(settings_data, f, indent=4, ensure_ascii=False)


def update_launch():

    launch_data = None
    launch_file = "{}/.vscode/launch.json".format(ZEPHYR_BASE)

    if os.path.exists(launch_file):
        try:
            launch_data = loadJson(launch_file)
        except json.decoder.JSONDecodeError as err:
            print("json load file '{}' Error: {}".format(launch_file, err))

    if launch_data == None:
        launch_data = json.loads(LAUNCH_TEMPLATE)

    cortex_debug_configuration = json.loads(LAUNCH_CORTEX_DEBUG)

    if len(launch_data) == 0:
        launch_data['configurations'] = [cortex_debug_configuration]

    need_append = True

    for configuration in launch_data['configurations']:
        if configuration.get("name") == cortex_debug_configuration["name"]:
            configuration.clear()
            configuration.update(cortex_debug_configuration)
            need_append = False
            break

    if need_append:
        launch_data['configurations'].append(cortex_debug_configuration)

    with open(launch_file, 'w') as f:
        json.dump(launch_data, f, indent=4, ensure_ascii=False)


def update():

    vscode_dir = "{}/.vscode".format(ZEPHYR_BASE)

    if not os.path.exists(vscode_dir):
        os.makedirs(vscode_dir)

    update_launch()

    update_settings()

    update_c_cpp_properties()


def config():
    cmd = "cmake -H{}/{} -B{} -GNinja -DCMAKE_BUILD_TYPE=Debug -DBOARD=stm32f769i_disco -DCMAKE_EXPORT_COMPILE_COMMANDS=1"
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
    parser.add_argument(
        '-c', '--config', action='store_true', help="config project")
    parser.add_argument(
        '-b', '--build', action='store_true', help="build project")
    parser.add_argument(
        '-C', "--clean", action='store_true', help="clean project")
    parser.add_argument('-f', '--flash', action='store_true', help="flash")
    parser.add_argument('-v', '--verbose',
                        action='store_true', help="verbose log")
    return parser.parse_args()


if __name__ == "__main__":

    for key in Env:
        os.environ[key] = Env[key]

    args = parse_arguments()

    if args.verbose:
        VERBOSE = args.verbose

    if args.clean:
        clean()

    if args.config:
        if config():
            os._exit(-1)
        update()

    if args.build:
        if build():
            os._exit(-1)

    if args.flash:
        if flash():
            os._exit(-1)
