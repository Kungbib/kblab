#!/usr/bin/env python

from lxml import etree
from argparse import ArgumentParser
from os.path import abspath,dirname,isfile
from sys import stdin,stdout,stderr,argv
from os import getpid,makedirs,remove
from inspect import getfile,currentframe
from json import loads

def fixalto(i):
    parser = etree.XMLParser()
    basedir = dirname(abspath(getfile(currentframe())))

    # find, correct and archive all OCR files
    fixalto = etree.XSLT(etree.parse('%s/fixalto.xsl' % basedir, parser))
    fixed = fixalto(etree.parse(i, parser))
    root = fixed.getroot()

    for cb in root.xpath("//*[ local-name() = 'ComposedBlock' ]"):
        # HPOS, etc already exists?
        if cb.xpath('@HPOS'):
            continue

        c = [ 100000000, 100000000, 0, 0 ]

        for tb in cb.xpath("*[ local-name() = 'TextBlock' ]"):
            t = [ int(tb.attrib['HPOS']), int(tb.attrib['VPOS']), int(tb.attrib['WIDTH']), int(tb.attrib['HEIGHT']) ]

            if t[0] < c[0]: c[0] = t[0]
            if t[1] < c[1]: c[1] = t[1]
            if t[0]+t[2] > c[2]: c[2] = t[0]+t[2]
            if t[1]+t[3] > c[3]: c[3] = t[1]+t[3]

            cb.attrib['HPOS'] = str(c[0])
            cb.attrib['VPOS'] = str(c[1])
            cb.attrib['WIDTH'] = str(c[2] - c[0])
            cb.attrib['HEIGHT'] = str(c[3] - c[1])

    return fixed


def get_alto_content(i, level='paragraph'):
    # fix alto
    fixed = fixalto(i)

    # get stylesheet
    parser = etree.XMLParser()
    basedir = dirname(abspath(getfile(currentframe())))

    # find, correct and archive all OCR files
    alto_to_json = etree.XSLT(etree.parse('%s/alto_to_json.xsl' % basedir, parser))
    js = alto_to_json(fixed)
    j = loads(str(js))

    if level == 'paragraph':
        j['composedblocks'] = [ {
            'i':x['i'],
            'c':x['c'],
            'textblocks': [ { 'content':" ".join([ z['w'] for z in w['words']]) } for w in x['textblocks'] ]
        } for x in j['composedblocks'] ]
    elif level == '':
        ...
    
    return j


