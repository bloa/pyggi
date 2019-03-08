import argparse
import re
import sys
from xml.etree import ElementTree

def append_child(src, tree, child, tags):
    last = None
    if child.tag in tags:
        last = filter_tags(child, tags)
        tree.append(last)
    else:
        if child.tail:
            if len(child) > 0:
                *_, last = child
                if last.tail:
                    last.tail += child.tail
                else:
                    last.tail = child.tail
            elif child.text:
                child.text += child.tail
            else:
                child.text = child.tail
        if child.text:
            if len(tree) > 0:
                *_, last = tree
                if last.tail:
                    last.tail += child.text
                else:
                    last.tail = child.text
            else:
                if tree.text:
                    tree.text += child.text
                else:
                    tree.text = child.text
        if len(child) > 0:
            for subchild in child:
                append_child(src, tree, subchild, tags)
    return tree

def filter_tags(tree, tags):
    filtered = ElementTree.Element(tree.tag, tree.attrib)
    filtered.text = tree.text
    filtered.tail = tree.tail
    for child in tree:
        filtered = append_child(tree, filtered, child, tags)
    return filtered

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('tags', type=str)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    tags = args.tags.split(',')
    xml = re.sub(r'\s+xmlns="[^"]+"', '', args.infile.read(), count=1)
    tree = ElementTree.fromstring(xml)
    tree = filter_tags(tree, tags)
    print(ElementTree.tostring(tree, encoding='unicode', method='xml'), file=args.outfile)

