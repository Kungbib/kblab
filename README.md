# KB data lab

**Note:** This repository is under active development and is provided as-is

## About

This repository aims to provide and demo tools for researchers in preparation of gaining access to digital archives at the National Library, or anyone else wanting to access collections without active copyright. There are two main ways to access digital objects in the data lab: either by using the HTTP API directly or using the provided client written in Python. You can also create a Docker image based on the one below which will have the client installed. The data available outside the National Library, currently on https://betalab.kb.se, does not have active copyright.

## TLDR;

Start environment using docker-compose. The local directory `./data` will be mounted on `/data` in the container. Any change from within the container will be reflected in the local directory and vice versa.

```
# connect to data lab
git clone https://github.com/kungbib/kblab
cd kblab
docker-compose exec repository.kb.se/lab/client /bin/bash
```

Then, see [examples](#examples) below.

## API

The API is a simple REST-based API on top of 

### URIs

Examples
- https://betalab.kb.se/dark-4001723/
- https://betalab.kb.se/dark-4001723/bib4345612_20140405_119570_95_0002.jp2

## Python client

## Docker images

## Examples

### Step 1 - Start Python
```
# python
```

### Step 2 - import relevant pacakages, for example
```
from kblab import Archive
from kblab.utils import fix_alto,get_alto_content
```

### Step 3 - connect
```
a = Archive('https://betalab.kb.se/')
```

### Step 4 - search for files and do something with the result
```

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

