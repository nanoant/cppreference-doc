#!/usr/bin/env python3

#   Copyright (C) 2011, 2012  Povilas Kanapickas <povilas@radix.lt>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

import fnmatch
import re
import os

# copy the source tree
os.system('rm -rf output/reference')
os.system('mkdir -p output/reference')
os.system('cp -rt output/reference reference/*')

# rearrange the archive {root} here is output/reference

# before
# {root}/en.cppreference.com/w/ : html
# {root}/en.cppreference.com/mwiki/ : data
# {root}/en.cppreference.com/ : data
# ... (other languages)
# {root}/upload.cppreference.com/mwiki/ : data

# after
# {root}/common/ : all common data
# {root}/en/ : html for en
# ... (other languages)

data_path = "output/reference/common"
os.system('mkdir ' + data_path)
os.system('mv output/reference/upload.cppreference.com/mwiki/* ' + data_path)
os.system('rm -r output/reference/upload.cppreference.com/')

for lang in ["en"]:
    path = "output/reference/" + lang + ".cppreference.com/"
    src_html_path = path + "w/"
    src_data_path = path + "mwiki/"
    html_path = "output/reference/" + lang

    if (os.path.isdir(src_html_path)):
        os.system('mv ' + src_html_path + ' ' + html_path)

    if (os.path.isdir(src_data_path)):
        # the skin files should be the same for all languages thus we
        # can merge everything
        os.system('cp -rl ' + src_data_path + '/* ' + data_path)
        os.system('rm -r ' + src_data_path)

    # also copy the custom fonts
    os.system('cp ' + path + 'DejaVuSansMonoCondensed60.ttf ' +
                      path + 'DejaVuSansMonoCondensed75.ttf ' + data_path)
    # remove what's left
    os.system('rm -r '+ path)

# find all html and css files
html_files = []
css_files = []
for root, dirnames, filenames in os.walk('output/reference/'):
    for filename in fnmatch.filter(filenames, '*.html'):
        html_files.append(os.path.join(root, filename))
    for filename in fnmatch.filter(filenames, '*.css'):
        css_files.append(os.path.join(root, filename))

#
r1 = re.compile('<!-- Added by HTTrack -->.*?<!-- \/Added by HTTrack -->')
r2 = re.compile('<!-- Mirrored from .*?-->')

#temporary fix
r3 = re.compile('<style[^<]*?<[^<]*?MediaWiki:Geshi\.css[^<]*?<\/style>', re.MULTILINE)

# clean the html files
for fn in html_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    text = r1.sub('', text);
    text = r2.sub('', text);
    text = r3.sub('', text);

    f = open(fn, "w")
    f.write(text)
    f.close()

    tmpfile = fn + '.tmp';
    os.system('xsltproc --novalid --html --encoding UTF-8 preprocess.xsl "' + fn + '" > "' + tmpfile + '"')
    os.system('mv "' + tmpfile + '" "' + fn + '"')

# append css modifications to the css files

f = open("preprocess-css.css", "r")
css_app = f.read()
f.close()

for fn in css_files:
    f = open(fn, "r")
    text = f.read()
    f.close()

    text = text.replace('../DejaVuSansMonoCondensed60.ttf', 'DejaVuSansMonoCondensed60.ttf')
    text = text.replace('../DejaVuSansMonoCondensed75.ttf', 'DejaVuSansMonoCondensed75.ttf')

    if (re.search('DejaVuSansMonoCondensed60', text)):
        # assume this is minified MediaWiki:Common.css
        # append the modifications
        text += css_app

    # QT Help viewer doesn't understand nth-child
    text = text.replace('nth-child(1)', 'first-child')

    f = open(fn, "w")
    f.write(text)
    f.close()

