import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('project_path', type=str, default='../sample/Triangle_fast')
    parser.add_argument('--line', action='store_true', default=None)
    parser.add_argument('--ast', action='store_true', default=None)
    parser.add_argument('--xml', action='store_true', default=None)
    args = parser.parse_args()

    if args.ast:
        from pyggi.astor import Program
    elif args.xml:
        from pyggi.xml import Program
    else:
        from pyggi.line import Program

    program = Program(args.project_path)
    for target in program.target_files:
        program.print_modification_points(target)
