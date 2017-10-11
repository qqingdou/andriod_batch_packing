# /usr/bin/python
# -*- coding:utf-8 -*-

# 在所有的配置参数中，不能使用中文(包括配置路径)

import os
import time
import argparse

curr_dir = os.path.join(os.getcwd(), time.strftime('%Y%m%d_%H%M%S', time.localtime(time.time())))

jar_signer_file_def = "D:\\jdk\\setuppath\\bin\\jarsigner.exe"
key_store_file_def = "E:\\you\\path\\gamecenter.jks"
key_store_pass_def = "xxx"
key_pass_def = "xxx"
key_alias_def = "xxx"
apk_tool_def = 'E:\\you\\path\\apktool_2.3.0.jar'


def build():
    parser = argparse.ArgumentParser()
    parser.add_argument('--channels', default='')
    parser.add_argument('--package', default='')
    parser.add_argument('--apk_tool', default=apk_tool_def)
    parser.add_argument('--output_dir', default=curr_dir)
    parser.add_argument('--jarsigner', default=jar_signer_file_def)
    parser.add_argument('--key_store_file', default=key_store_file_def)
    parser.add_argument('--key_store_pass', default=key_store_pass_def)
    parser.add_argument('--key_pass', default=key_pass_def)
    parser.add_argument('--key_alias', default=key_alias_def)
    parser.add_argument('--tsacert', default='0')

    args = parser.parse_args()
    channels = args.channels.strip()
    apk_file = args.package.strip()
    apk_tool = args.apk_tool.strip()
    output_dir = args.output_dir.strip()
    jar_signer_file = args.jarsigner.strip()
    key_store_file = args.key_store_file.strip()
    key_store_pass = args.key_store_pass.strip()
    key_pass = args.key_pass.strip()
    key_alias = args.key_alias.strip()
    decode_dir = os.path.join(output_dir, 'decode')
    re_build_dir = os.path.join(output_dir, 're_package')
    signed_apk_dir = os.path.join(output_dir, 'sign_package')
    tsacert = args.tsacert.strip()

    if output_dir == '':
        raise Exception('output_dir is empty,please use --output_dir %s' % curr_dir)

    if os.path.exists(output_dir):
        raise Exception('output_dir is exists, please choose another.')

    if channels == '':
        raise Exception('channels is empty,please use --channels 1,2,3')

    if apk_file == '':
        raise Exception('package path is empty,please use --package E:\\app-debug.apk')

    if apk_tool == '':
        raise Exception('apk_tool path is empty,please use --apk_tool %s' % apk_tool_def)

    if jar_signer_file == '':
        raise Exception('jarsigner is empty,please use --jarsigner %s' % jar_signer_file_def)

    if key_store_file == '':
        raise Exception('key_store_file is empty,please use --key_store_file %s' % key_store_file_def)

    if key_store_pass == '':
        raise Exception('key_store_pass is empty,please use --key_store_pass %s' % key_store_pass_def)

    if key_pass == '':
        raise Exception('key_pass is empty,please use --key_pass %s' % key_pass_def)

    if key_alias == '':
        raise Exception('key_alias is empty,please use --key_alias %s' % key_alias_def)

    try:
        # 创建输出目录
        os.mkdir(output_dir)
        # 创建最后签名的目录
        os.mkdir(signed_apk_dir)

        array_channels = channels.split(",")

        if len(array_channels) <= 0:
            raise Exception('channels format is not valid,please use --channels 1,2,3')

        print 'begin decode apk,please waiting...'
        # 解压压缩包
        os.system("java -jar %s d %s -o %s -f" % (apk_tool, apk_file, decode_dir))

        # 安装包文件名
        package_name = os.path.splitext(os.path.basename(apk_file))[0]

        print 'completed decode apk.'

        for channel in array_channels:

            channel = channel.strip()

            print 'channel: %s is running to replace AndroidManifest.xml, please waiting...' % channel

            manifest_file = os.path.join(decode_dir, 'AndroidManifest.xml')

            temp_manifest = []
            with open(manifest_file, 'r') as handle:
                for line in handle.readlines():
                    if line.find('HW_CHANNEL') > 0:
                        temp_manifest.append('<meta-data android:name="HW_CHANNEL" android:value="%s"/>\r\n' % channel)
                    else:
                        temp_manifest.append(line)

            with open(manifest_file, 'w') as handle:
                handle.write("".join(temp_manifest))

            print 'channel: %s replaced AndroidManifest.xml completed' % channel

            print 'channel: %s is building...' % channel
            # 重新打包
            re_apk_file = os.path.join(re_build_dir, '%s_%s.apk' % (package_name, channel))
            os.system("java -jar %s b %s -o %s" % (apk_tool, decode_dir, re_apk_file))
            print 'channel: %s build completed' % channel

            print 'channel: %s is signing...' % channel
            # 签名
            signed_apk_file = os.path.join(signed_apk_dir, '%s_%s.apk' % (package_name, channel))

            # 时间戳签发机构，由于国内，翻墙经常会断，看情况而定，不会影响使用
            tsacert = ('' if tsacert == '0' else '-tsa https://timestamp.geotrust.com/tsa')

            os.system("%s -keystore %s -storepass %s -keypass %s -sigfile CERT -digestalg SHA1 -sigalg MD5withRSA -signedjar %s %s %s %s" % (jar_signer_file, key_store_file, key_store_pass, key_pass, signed_apk_file, re_apk_file, key_alias, tsacert))
            print 'channel: %s sign completed' % channel

        print 'all completed'

    except Exception as e:
        print e


if __name__ == '__main__':
    build()
