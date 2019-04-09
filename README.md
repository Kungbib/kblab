# KB data lab

**Note:** This repository is under active development, is not fully (or at all) functional, and is provided as-is

## About

This repository aims to provide and demo tools for researchers in preparation of gaining access to digital archives on-premise at the National Library, or anyone else wanting to access collections without active copyright. There are two main ways to access digital objects: either by using the HTTP API directly or using the provided client written in Python. You can also create a Docker image based on the one below which will have the client installed, or use the install the client using `pip` or `conda` in your own container. The data available outside the National Library, currently on https://betalab.kb.se, does not have active copyright.

## Installation

## TLDR; - [pip](https://pypi.org/) or [conda](https://www.anaconda.com/distribution/)

To install the client module using `pip` simply run
```
pip install kblab-client
```

To install using `conda` instead use the following
```
conda install kblab-client
```

Or add it to your dependencies in `environment.yml`
```
dependencies:
    - pip:
        kblab-client
```

Then, see [examples](#examples) below.

## TLDR; - Docker version

Start environment using docker. The local directory `./data` will be mounted on `/data` in the container. Any change from within the container will be reflected in the local directory and vice versa.
```
docker container run -it repository.kb.se/lab/client /bin/bash
d8fg7sjf4i # python
```

Then, see [examples](#examples) below.

## From source

First check out the source code
```
git clone https://github.com/kungbib/kblab
cd kblab
```

Then either build and run the Docker image 
```
docker build .
docker run -it <image id> /bin/bash
```

Or install the required package and python client, optionally creating a virtual environment so as to not mess up you existing one.
```
python -m venv venv
source venv/bin/activate
pip install -r requirement.txt
./setup.py install
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

The National Library uses a package structure modeled on OAIS. A simplified representation in JSON-LD is provided as part of the response in addition to information about the logical structure of the material (e.g pages, covers), some metadata, links to physical object, etc.

## Python client

## Docker images

## Examples

### Word count of Aftonbladet, issue 1899-12-22
```
from collections import Counter
from kblab import Archive
from kblab.utils import fix_alto
from kblab.helpers get_alto_content

a = Archive('https://betalab.kb.se/')
c = Counter()

# find a specific issue of Aftonbladet
for package_id in a.search({ 'label': 'AFTONBLADET 1899-12-22' }):
    p = a.get(package_id)

    # iterate over files in package
    for fname in a.get(package_id):
        if fname.endswith('_alto.xml'):
            # apply fix for potentially borken ALTO files and get text
            text = get_alto_content(a.get_stream(fname))
            
            # research goes here ...
            c.update(text.split())
    for word,count in c:
        print(word, count, sep='\t')
else:
    print('not found')

```

## IIIF support

Images in the archive can either be downloaded and dealt with directly in full resolution or they can be cropped and scaled using the [IIIF](https://iiif.io/) protocol.

### Manifests

For same packages IIIF-[manifests](https://iiif.io/api/presentation/2.0/#manifest) can be accessed by adding `/_manifest` to a URI. See example below.


