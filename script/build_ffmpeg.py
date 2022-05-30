# encoding=utf-8
import os
import sys
import common
import argparse
import commands
import shutil


def exe_cmd(cmdstr):
    common.logger.debug('cmdstr %s ' % cmdstr)
    build_result = os.system(cmdstr)
    if build_result != 0:
        return False
    return build_result


def chmod_openssl():
    buid_path = os.path.join(common.ROOT_PATH, 'ios')
    x86_path = os.path.join(buid_path, 'openssl-x86_64/include/openssl/')
    armv7_path = os.path.join(buid_path, 'openssl-armv7/include/openssl/')
    armv7s_path = os.path.join(buid_path, 'openssl-armv7s/include/openssl/')
    i386_path = os.path.join(buid_path, 'openssl-i386/include/openssl/')
    os.system('chmod 777 %s/opensslv.h' % x86_path)
    os.system('chmod 777 %s/opensslv.h' % armv7_path)
    os.system('chmod 777 %s/opensslv.h' % armv7s_path)
    os.system('chmod 777 %s/opensslv.h' % i386_path)


def build_library(branch, mode, openssl, clean_ssl, ssl_version):
    cd_cmd = 'cd %s' % common.ROOT_PATH
    git_cmd = cd_cmd + ' && ' + 'git log --pretty=format:%h -n 1'
    commit = commands.getstatusoutput(git_cmd)[1]

    buid_path = os.path.join(common.ROOT_PATH, 'ios')

    build_script_ssl = os.path.join(buid_path, 'compile-openssl.sh')
    build_script = os.path.join(buid_path, 'compile-ffmpeg.sh')
    os.system('chmod +x %s' % build_script)
    os.system('chmod +x %s' % build_script_ssl)

    clean_cmd = 'cd %s && sh %s %s clean' % (buid_path, build_script, mode)
    if clean_ssl:
        clean_cmd = 'cd %s && sh %s clean && sh %s %s clean' % (buid_path, build_script_ssl, build_script, mode)

    buid_cmd = 'cd %s && sh %s %s all' % (buid_path, build_script, mode)
    zip_name = 'ffmpeg_3.1_nossl-cc-%s-%s-%s.zip' % (branch, mode, commit)
    if openssl:
        buid_cmd = 'cd %s && sh %s all && sh %s %s all' % (buid_path, build_script_ssl, build_script, mode)
        zip_name = 'ffmpeg_3.1_openssl-%s-%s-%s-%s.zip' % (ssl_version, branch, mode, commit)

    exe_cmd(clean_cmd)
    common.logger.debug('------clean success------')
    exe_cmd(buid_cmd)
    common.logger.debug('------build success------')

    common.logger.debug('------begin zip------')
    save_path = os.path.join(buid_path, 'build', 'universal')
    zip_cmd = 'cd %s && zip -r -q %s %s %s' % (save_path, zip_name, 'include/', 'lib/')
    move_cmd = 'cd %s && mv %s %s' % (save_path, zip_name, os.path.join(buid_path, 'release_%s' % mode, zip_name))
    exe_cmd(zip_cmd)
    exe_cmd(move_cmd)
    common.logger.debug('------end zip------')

    return True


def pull_openssl(version):
    openssl_file = os.path.join(common.ROOT_PATH, 'init-ios-openssl.sh')
    f = open(openssl_file, 'r+')
    flist = f.readlines()
    flist[19] = 'IJK_OPENSSL_COMMIT=OpenSSL_%s\n' % version
    f.close()
    f = open(openssl_file, 'w+')
    f.writelines(flist)
    f.close()
    common.logger.debug('------%s------' % flist[19])
    exe_cmd('cd %s && sh init-ios-openssl.sh' % common.ROOT_PATH)


def str_to_bool(strBool):
    return True if strBool.lower() == 'true' else False


if __name__ == '__main__':
    parser = argparse.ArgumentParser("cli")
    parser.add_argument('-branch', '--branch', type=str, help='branch info')
    parser.add_argument('-openssl', '--openssl', type=str, help='with openssl or not')
    parser.add_argument('-rebuild_ssl', '--rebuid_ssl', type=str, help='rebuild openssl or not')
    parser.add_argument('-version_ssl', '--version_ssl', type=str, help='openssl version')
    parser.add_argument('-mode', '--mode', type=str, help='sdk or player')

    args = parser.parse_args(sys.argv[1:])
    common.logger.debug('args %s' % args)
    branch = args.branch
    openssl = str_to_bool(args.openssl)
    mode = args.mode
    rebuid_openssl = str_to_bool(args.rebuid_ssl)
    version_openssl = args.version_ssl

    common.logger.debug('current branch is %s openssl is %d mode is %s \
                         rebuid ssl is %d ssl version is %s' % (branch, openssl, mode, rebuid_openssl, version_openssl))

    if mode != 'sdk' and mode != 'player':
        common.logger.debug('mode shouble be sdk or player')
        exit(0)

    frameworksOutputDir = os.path.join(common.ROOT_PATH, 'ios', 'release_%s' % mode)
    common.logger.debug('----- clean outputDir %s ----' % frameworksOutputDir)
    if os.path.exists(frameworksOutputDir):
        shutil.rmtree(frameworksOutputDir)
    os.makedirs(frameworksOutputDir)

    if rebuid_openssl and openssl:
        pull_openssl(version_openssl)
    build_library(branch, mode, openssl, rebuid_openssl, version_openssl)
