"""
src_line_to_xml ::

    python src_line_to_xml.py src_line_to_xml.py
"""
import argparse
import sys
import xml.sax.saxutils as saxutils

def split_raw(newline, infile, outfile):
    print('<unit>', end='', file=outfile)
    if newline:
        for i, line in enumerate(infile.readlines()):
            if i > 0:
                print('</line>', end='')
            print('<line>{}'.format(saxutils.escape(line.rstrip())), file=outfile)
        print('</line>')
    else:
        for line in infile.readlines():
            print('<line>{}</line>'.format(saxutils.escape(line.rstrip())), file=outfile)
    print('</unit>', file=outfile)

def split_better(newline, infile, outfile):
    print('<unit>', end='', file=outfile)
    if newline:
        end = False
        for line in infile.readlines():
            if end:
                print('</line>', end='')
                end = False
            if line.strip() != '':
                print('<line>{}'.format(saxutils.escape(line.rstrip())), file=outfile)
                end = True
            else:
                print(line.rstrip(), file=outfile)
        if end:
            print('</line>', end='')
    else:
        for line in infile.readlines():
            if line.strip() != '':
                print('<line>{}</line>'.format(saxutils.escape(line.rstrip())), file=outfile)
            else:
                print(line.rstrip(), file=outfile)
    print('</unit>', file=outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--mode', default='better')
    parser.add_argument('--newline', action='store_true', default=False)
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'), default=sys.stdin)
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'), default=sys.stdout)
    args = parser.parse_args()

    if args.mode == 'raw':
        split_raw(args.newline, args.infile, args.outfile)
    elif args.mode == 'better':
        split_better(args.newline, args.infile, args.outfile)
    else:
        print('ERROR: --mode should be either "raw" or "better"', file=sys.stderr)
        exit(1)
