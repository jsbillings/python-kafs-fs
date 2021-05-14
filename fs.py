#!/usr/bin/env python3

import os
import sys
import argparse
import xattr
from pprint import pprint

## https://github.com/openafs/openafs/blob/openafs-stable-1_8_x/src/libacl/prs_fs.h
#define PRSFS_READ            1 /*Read files*/
#define PRSFS_WRITE           2 /*Write and write-lock existing files*/
#define PRSFS_INSERT          4 /*Insert and write-lock new files*/
#define PRSFS_LOOKUP          8 /*Enumerate files and examine access list */
#define PRSFS_DELETE          16 /*Remove files*/
#define PRSFS_LOCK            32 /*Read-lock files*/
#define PRSFS_ADMINISTER      64 /*Set access list of directory*/

def print_err(errstr):
    print("%s: %s" % (sys.argv[0], errstr))
    sys.exit(1)

def acllookup(acl):
    aclstr = ''
    acln = int(acl)
    if acln & 1: #PRFS_READ
        aclstr += 'r'
    if acln & 8: #PRFS_LOOKUP
        aclstr += 'l'
    if acln & 4: #PRFS_INSERT
        aclstr += 'i'
    if acln & 16: #PRFS_DELETE
        aclstr += 'd'
    if acln & 2: #PRFS_WRITE
        aclstr += 'w'
    if acln & 32: #PRFS_LOCK
        aclstr += 'k'
    if acln & 64: #PRFS_ADMINISTER
        aclstr += 'a'
    if aclstr == '':
        return 'none'
    else:
        return aclstr

def dolistacl(args):
    path = os.path.abspath(args.path[0])
    try:
        attrobj = xattr.getxattr(path, "afs.acl")
    except FileNotFoundError:
        print_err("No such file or directory: %s" % path)
    except OSError as e:
        if e.errno == 95:
            print_err("Invalid argument; it is possible that %s is not in AFS"
                  % path)
        else:
            print_err("cannot open directory %s: %s" %
                      ( path, e.strerror) )
    attrs = attrobj.decode(encoding='UTF-8').split('\n')
    print("Access list for %s" % path)
    positiveacls = int(attrs[0])
    negativeacls = int(attrs[1])
    if (positiveacls > 0):
        print("Normal rights:")
        for attr in attrs[2:positiveacls+2]:
            if not '\t' in attr:
                continue
            (name,acl) = attr.split('\t')
            print("  %s %s" % (name, acllookup(acl)))
    if (negativeacls > 0):
        print("Negative rights:")
        for attr in attrs[2+positiveacls:2+positiveacls+negativeacls]:
            if not '\t' in attr:
                continue
            (name,acl) = attr.split('\t')
            print("  %s %s" % (name, acllookup(acl)))

if __name__ == '__main__':
    usage = "Usage: fs subcommand"
    parser = argparse.ArgumentParser("AFS filesystem command",
                            usage=usage)
    subparsers = parser.add_subparsers()
    listacl = subparsers.add_parser(
        'listacl', aliases=['la'],help='list access control list'
    )
    listacl.set_defaults(func=dolistacl)

    listacl.add_argument(
        'path',  nargs='+'
    )
    args = parser.parse_args()
    args.func(args)
    
    
