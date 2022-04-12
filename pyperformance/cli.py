import argparse
import logging
import os.path
import sys

from pyperformance import _utils, is_installed, is_dev
from pyperformance.commands import COMMANDS


def comma_separated(values):
    values = [value.strip() for value in values.split(',')]
    return list(filter(None, values))


#######################################
# benchmarks

def filter_opts(cmd, *, allow_no_benchmarks=False):
    cmd.add_argument("--manifest", help="benchmark manifest file to use")

    cmd.add_argument("-b", "--benchmarks", metavar="BM_LIST", default='<default>',
                     help=("Comma-separated list of benchmarks to run.  Can"
                           " contain both positive and negative arguments:"
                           "  --benchmarks=run_this,also_this,-not_this.  If"
                           " there are no positive arguments, we'll run all"
                           " benchmarks except the negative arguments. "
                           " Otherwise we run only the positive arguments."))
    cmd.set_defaults(allow_no_benchmarks=allow_no_benchmarks)


def _legacy_benchmarks_check(selections, manifest):
    for sel in selections or ():
        if not sel:
            raise NotImplementedError(sel)
        if callable(sel.parsed):
            raise NotImplementedError(sel)
        # Disallow negative groups.
        name = sel.parsed.name if sel.kind == 'benchmark' else sel.parsed
        if name in manifest.groups and sel.op == '-':
            raise ValueError(f'negative groups not supported: -{sel.parsed.name}')


def _benchmarks_from_options(options):
    from pyperformance._benchmark_selections import RequestedBenchmarks

    class SelectedBenchmarks(RequestedBenchmarks):

        def _parse_selections(self, manifest):
            selections = super()._parse_selections(manifest)
            selections = list(selections)
            _legacy_benchmarks_check(selections, manifest)
            return selections

        def _on_selection_has_no_matches(self, selstr):
            logging.warning(f"no benchmark named {selstr!r}")

    return SelectedBenchmarks(options.manifest, options.benchmarks)


#######################################
# the script

def parse_args():
    parser = argparse.ArgumentParser(
        description=("Compares the performance of baseline_python with"
                     " changed_python and prints a report."))

    subparsers = parser.add_subparsers(dest='action')
    cmds = []

    # run
    cmd = subparsers.add_parser(
        'run', help='Run benchmarks on the running python')
    cmds.append(cmd)
    cmd.add_argument("-r", "--rigorous", action="store_true",
                     help=("Spend longer running tests to get more"
                           " accurate results"))
    cmd.add_argument("-f", "--fast", action="store_true",
                     help="Get rough answers quickly")
    cmd.add_argument("--debug-single-value", action="store_true",
                     help="Debug: fastest mode, only compute a single value")
    cmd.add_argument("-v", "--verbose", action="store_true",
                     help="Print more output")
    cmd.add_argument("-m", "--track-memory", action="store_true",
                     help="Track memory usage. This only works on Linux.")
    cmd.add_argument("--affinity", metavar="CPU_LIST", default=None,
                     help=("Specify CPU affinity for benchmark runs. This "
                           "way, benchmarks can be forced to run on a given "
                           "CPU to minimize run to run variation."))
    cmd.add_argument("-o", "--output", metavar="FILENAME",
                     help="Run the benchmarks on only one interpreter and "
                           "write benchmark into FILENAME. "
                           "Provide only baseline_python, not changed_python.")
    cmd.add_argument("--append", metavar="FILENAME",
                     help="Add runs to an existing file, or create it "
                     "if it doesn't exist")
    filter_opts(cmd)

    # show
    cmd = subparsers.add_parser('show', help='Display a benchmark file')
    cmd.add_argument("filename", metavar="FILENAME")

    # compare
    cmd = subparsers.add_parser('compare', help='Compare two benchmark files')
    cmds.append(cmd)
    cmd.add_argument("-v", "--verbose", action="store_true",
                     help="Print more output")
    cmd.add_argument("-O", "--output_style", metavar="STYLE",
                     choices=("normal", "table"),
                     default="normal",
                     help=("What style the benchmark output should take."
                           " Valid options are 'normal' and 'table'."
                           " Default is normal."))
    cmd.add_argument("--csv", metavar="CSV_FILE",
                     action="store", default=None,
                     help=("Name of a file the results will be written to,"
                           " as a three-column CSV file containing minimum"
                           " runtimes for each benchmark."))
    cmd.add_argument("baseline_filename", metavar="baseline_file.json")
    cmd.add_argument("changed_filename", metavar="changed_file.json")

    # list
    cmd = subparsers.add_parser(
        'list', help='List benchmarks of the running Python')
    cmds.append(cmd)
    filter_opts(cmd)

    # list-groups
    cmd = subparsers.add_parser(
        'list-groups', aliases=['list_groups'],
        help='List benchmark groups of the running Python')
    cmds.append(cmd)
    cmd.add_argument("--manifest", help="benchmark manifest file to use")

    # compile
    cmd = subparsers.add_parser(
        'compile', help='Compile and install CPython and run benchmarks '
                        'on installed Python')
    cmd.add_argument('config_file',
                     help='Configuration filename')
    cmd.add_argument('revision',
                     help='Python benchmarked revision')
    cmd.add_argument('branch', nargs='?',
                     help='Git branch')
    cmd.add_argument('--patch',
                     help='Patch file')
    cmd.add_argument('-U', '--no-update', action="store_true",
                     help="Don't update the Git repository")
    cmd.add_argument('-T', '--no-tune', action="store_true",
                     help="Don't run 'pyperf system tune' "
                          "to tune the system for benchmarks")
    cmds.append(cmd)

    # compile-all
    cmd = subparsers.add_parser(
        'compile-all', aliases=['compile_all'],
        help='Compile and install CPython and run benchmarks '
             'on installed Python on all branches and revisions '
             'of CONFIG_FILE')
    cmd.add_argument('config_file',
                     help='Configuration filename')
    cmds.append(cmd)

    # upload
    cmd = subparsers.add_parser(
        'upload', help='Upload JSON results to a Codespeed website')
    cmd.add_argument('config_file',
                     help='Configuration filename')
    cmd.add_argument('json_file',
                     help='JSON filename')
    cmds.append(cmd)

    # venv
    venv_common = argparse.ArgumentParser(add_help=False)
    venv_common.add_argument("--venv", dest="_venv_ignored",
                             action="store_true",
                             help="(legacy; not used)")
    venv_common.add_argument("venv", nargs="?", help="Path to the virtual environment")
    cmd = subparsers.add_parser('venv', parents=[venv_common],
                                help='Actions on the virtual environment')
    cmd.set_defaults(venv_action='show')
    venvsubs = cmd.add_subparsers(dest="venv_action")
    cmd = venvsubs.add_parser('show', parents=[venv_common])
    cmds.append(cmd)
    cmd = venvsubs.add_parser('create', parents=[venv_common])
    filter_opts(cmd, allow_no_benchmarks=True)
    cmds.append(cmd)
    cmd = venvsubs.add_parser('recreate', parents=[venv_common])
    filter_opts(cmd, allow_no_benchmarks=True)
    cmds.append(cmd)
    cmd = venvsubs.add_parser('remove', parents=[venv_common])
    cmds.append(cmd)

    for cmd in cmds:
        cmd.add_argument("--inherit-environ", metavar="VAR_LIST",
                         type=comma_separated,
                         help=("Comma-separated list of environment variable "
                               "names that are inherited from the parent "
                               "environment when running benchmarking "
                               "subprocesses."))
        cmd.add_argument("-p", "--python",
                         help="Python executable (default: use running Python)",
                         default=sys.executable)

    #########################
    # Now run the parser.

    options = parser.parse_args()
    ns = vars(options)

    cmd = ns.pop('action')
    if not cmd:
        parser.error('missing cmd')
    elif cmd == 'venv':
        ns.pop('_venv_ignored')
        venv_action = ns.pop('venv_action')
        cmd = f'venv-{venv_action}'
    elif cmd == 'run':
        if options.debug_single_value:
            options.fast = True

    if hasattr(options, 'python'):
        # Replace "~" with the user home directory
        options.python = os.path.expanduser(options.python)
        # Try to get the absolute path to the binary
        abs_python = os.path.abspath(options.python)
        if not abs_python:
            print("ERROR: Unable to locate the Python executable: %r" %
                  options.python, flush=True)
            sys.exit(1)
        options.python = abs_python

    if hasattr(options, 'benchmarks'):
        allow_empty = ns.pop('allow_no_benchmarks')
        if options.benchmarks == '<NONE>':
            if not allow_empty:
                parser.error('--benchmarks cannot be empty')
            options.benchmarks = None
        else:
            parsed = _utils.ParsedSelection.iter_from_raw(
                options.benchmarks.lower(),
            )
            options.benchmarks = [str(s) for s in parsed]

    return cmd, ns, options, parser


def _main(cmd, cmd_kwargs, options, parser):
    try:
        run_cmd = COMMANDS[cmd]
    except KeyError:
        print(f'ERROR: unsupported command {cmd!r}')
        parser.print_help()
        sys.exit(1)

    if 'benchmarks' in cmd_kwargs:
        benchmarks = _benchmarks_from_options(options)
        run_cmd(options, benchmarks)
    else:
        run_cmd(options)


def main():
    try:
        if not is_installed():
            # Always require a local checkout to be installed.
            print('ERROR: pyperformance should not be run without installing first')
            if is_dev():
                print('(consider using the dev.py script)')
            sys.exit(1)

        cmd, cmd_kwargs, options, parser = parse_args()
        _main(cmd, cmd_kwargs, options, parser)
    except KeyboardInterrupt:
        print("Benchmark suite interrupted: exit!", flush=True)
        sys.exit(1)
