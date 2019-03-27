# KB data lab

**Note:** This repository is under active development and is provided as-is

## About

This repository aims to provide and demo tools for researchers in preparation of gaining access to digital archives at the National Library, or anyone else wanting to access collections without active copyright. There are two main ways to access digital objects in the data lab: either by using the HTTP API directly or using the provided client written in Python. You can also create a Docker image based on the one below which will have the client installed. The data available outside the National Library, currently on https://betalab.kb.se, does not have active copyright.

## TLDR;

Start environment using docker-compose. The local directory `./data` will be mounted on `/data` in the container. Any change from within the container will be reflected in the local directory and vice versa.

```
git clone https://github.com/kungbib/kblab
cd kblab
docker-compose exec repository.kb.se/lab/client /bin/bash
d8fg7sjf4i # python
```

Then, see [examples](#examples) below.

## API

The API is a simple REST-based API that delivers JSON(-LD) describing packages and/or files with the addition of a search endpoint.

### URIs

Examples
- https://betalab.kb.se/dark-4001723/
- https://betalab.kb.se/dark-4001723/bib4345612_20140405_119570_95_0002.jp2

### Finding packages

### Data model

## Python client

## Docker images

## Examples

### Do word frequency analysis on first ten pages of Aftonbladet, issue 1899-12-22
```
from kblab import Archive
from kblab.utils import fix_alto,get_alto_content
a = Archive('https://betalab.kb.se/')

# find a specific issue of Aftonbladet
for package_id in a.search({ 'label': 'AFTONBLADET 1899-12-22' }):
    p = a.get(package_id)

    # iterate over files in package
    for fname in a.get(package_id):
        if fname.endswith('_alto.xml'):
            # apply fix for potentially borken ALTO files
            text = get_alto_content(fix_alto(a.get(fname)))
            
            # do something with the text
```

## IIIF support

Images in the archive can either be downloaded and dealt with directly in full resolution or they can be cropped and scaled using the IIIF protocol.

### Manifests

For same packages IIIF-manifests can be accessed by adding `/_manifest` to a URI. See example below.


