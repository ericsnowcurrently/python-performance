Changelog
=========

Version 0.5.4
-------------

* Add ``pyperformance compile`` command to compile, install and benchmark
  Python
* Add ``pyperformance upload`` command to upload a JSON file to a Codespeed
  instance
* Add ``pyperformance compile_all`` command to benchmark multiple branches and
  revisions of Python

Version 0.5.3 (2017-03-27)
--------------------------

* Upgrade Dulwich to 0.17.3 to support PyPy older than 5.6:
  see https://github.com/jelmer/dulwich/issues/509
* Fix ResourceWarning warnings: close explicitly files and sockets.
* scripts: replace Mercurial commands with Git commands.
* Upgrade requirements:

  - dulwich: 0.17.1 => 0.17.3
  - perf: 1.0 => 1.1
  - psutil: 5.2.0 => 5.2.1

Version 0.5.2 (2017-03-17)
--------------------------

* Upgrade requirements:

  - certifi: 2016.9.26 => 2017.1.23
  - Chameleon: 3.0 => 3.1
  - Django: 1.10.5 => 1.10.6
  - MarkupSafe: 0.23 => 1.0
  - dulwich: 0.16.3 => 0.17.1
  - mercurial: 4.0.2 => 4.1.1
  - pathlib2: 2.2.0 => 2.2.1
  - perf: 0.9.3 => 1.0
  - psutil: 5.0.1 => 5.2.0
  - SQLAlchemy: 1.1.4 => 1.1.6

Version 0.5.1 (2017-01-16)
--------------------------

* Fix Windows support (upgrade perf from 0.9.0 to 0.9.3)
* Upgrade requirements:

  - Chameleon: 2.25 => 3.0
  - Django: 1.10.3 => 1.10.5
  - docutils: 0.12 => 0.13.1
  - dulwich: 0.15.0 => 0.16.3
  - mercurial: 4.0.0 => 4.0.2
  - perf: 0.9.0 => 0.9.3
  - psutil: 5.0.0 => 5.0.1

Version 0.5.0 (2016-11-16)
--------------------------

* Add ``mdp`` benchmark: battle with damages and topological sorting of nodes
  in a graph
* The ``default`` benchmark group now include all benchmarks but ``pybench``
* If a benchmark fails, log an error, continue to execute following
  benchmarks, but exit with error code 1.
* Remove deprecated benchmarks: ``threading_threaded_count`` and
  ``threading_iterative_count``. It wasn't possible to run them anyway.
* ``dulwich`` requirement is now optional since its installation fails
  on Windows.
* Upgrade requirements:

  - Mako: 1.0.5 => 1.0.6
  - Mercurial: 3.9.2 => 4.0.0
  - SQLAlchemy: 1.1.3 => 1.1.4
  - backports-abc: 0.4 => 0.5

Version 0.4.0 (2016-11-07)
--------------------------

* Add ``sqlalchemy_imperative`` benchmark: it wasn't registered properly
* The ``list`` command now only lists the benchmark that the ``run`` command
  will run. The ``list`` command gets a new ``-b/--benchmarks`` option.
* Rewrite the code creating the virtual environment to test correctly pip.
  Download and run ``get-pip.py`` if pip installation failed.
* Upgrade requirements:

  * perf: 0.8.2 => 0.9.0
  * Django: 1.10.2 => 1.10.3
  * Mako: 1.0.4 => 1.0.5
  * psutil: 4.3.1 => 5.0.0
  * SQLAlchemy: 1.1.2 => 1.1.3

* Remove ``virtualenv`` dependency

Version 0.3.2 (2016-10-19)
--------------------------

* Fix setup.py: include also ``performance/benchmarks/data/asyncio.git/``

Version 0.3.1 (2016-10-19)
--------------------------

* Add ``regex_dna`` benchmark
* The ``run`` command now fails with an error if no benchmark was run.
* genshi, logging, scimark, sympy and xml_etree scripts now run all
  sub-benchmarks by default
* Rewrite pybench using perf: remove the old legacy code to calibrate and run
  benchmarks, reuse perf.Runner API.
* Change heuristic to create the virtual environment, tried commands:

  * ``python -m venv``
  * ``python -m virtualenv``
  * ``virtualenv -p python``

* The creation of the virtual environment now ensures that pip works
  to detect "python3 -m venv" which doesn't install pip.
* Upgrade perf dependency from 0.7.12 to 0.8.2: update all benchmarks to
  the new perf 0.8 API (which introduces incompatible changes)
* Update SQLAlchemy from 1.1.1 to 1.1.2

Version 0.3.0 (2016-10-11)
--------------------------

New benchmarks:

* Add ``crypto_pyaes``: Benchmark a pure-Python implementation of the AES
  block-cipher in CTR mode using the pyaes module (version 1.6.0). Add
  ``pyaes`` dependency.
* Add ``sympy``: Benchmark on SymPy. Add ``scipy`` dependency.
* Add ``scimark`` benchmark
* Add ``deltablue``: DeltaBlue benchmark
* Add ``dulwich_log``: Iterate on commits of the asyncio Git repository using
  the Dulwich module. Add ``dulwich`` (and ``mpmath``) dependencies.
* Add ``pyflate``: Pyflate benchmark, tar/bzip2 decompressor in pure
  Python
* Add ``sqlite_synth`` benchmark: Benchmark Python aggregate for SQLite
* Add ``genshi`` benchmark: Render template to XML or plain text using the
  Genshi module. Add ``Genshi`` dependency.
* Add ``sqlalchemy_declarative`` and ``sqlalchemy_imperative`` benchmarks:
  SQLAlchemy Declarative and Imperative benchmarks using SQLite. Add
  ``SQLAlchemy`` dependency.

Enhancements:

* ``compare`` command now fails if the performance versions are different
* ``nbody``: add ``--reference`` and ``--iterations`` command line options.
* ``chaos``: add ``--width``, ``--height``, ``--thickness``, ``--filename``
  and ``--rng-seed`` command line options
* ``django_template``: add ``--table-size`` command line option
* ``json_dumps``: add ``--cases`` command line option
* ``pidigits``: add ``--digits`` command line option
* ``raytrace``: add ``--width``, ``--height`` and ``--filename`` command line
  options
* Port ``html5lib`` benchmark to Python 3
* Enable ``pickle_pure_python`` and ``unpickle_pure_python`` on Python 3
  (code was already compatible with Python 3)
* Creating the virtual environment doesn't inherit environment variables
  (especially ``PYTHONPATH``) by default anymore: ``--inherit-environ``
  command line option must now be used explicitly.

Bugfixes:

* ``chaos`` benchmark now also reset the ``random`` module at each sample
  to get more reproductible benchmark results
* Logging benchmarks now truncate the in-memory stream before each benchmark
  run

Rename benchmarks:

* Rename benchmarks to get a consistent name between the command line and
  benchmark name in the JSON file.
* Rename pickle benchmarks:

   - ``slowpickle`` becomes ``pickle_pure_python``
   - ``slowunpickle`` becomes ``unpickle_pure_python``
   - ``fastpickle`` becomes ``pickle``
   - ``fastunpickle`` becomes ``unpickle``

 * Rename ElementTree benchmarks: replace ``etree_`` prefix with
   ``xml_etree_``.
 * Rename ``hexiom2`` to ``hexiom_level25`` and explicitly pass ``--level=25``
   parameter
 * Rename ``json_load`` to ``json_loads``
 * Rename ``json_dump_v2`` to ``json_dumps`` (and remove the deprecated
   ``json_dump`` benchmark)
 * Rename ``normal_startup`` to ``python_startup``, and ``startup_nosite``
   to ``python_startup_no_site``
 * Rename ``threaded_count`` to ``threading_threaded_count``,
   rename ``iterative_count`` to ``threading_iterative_count``
 * Rename logging benchmarks:

   - ``silent_logging`` to ``logging_silent``
   - ``simple_logging`` to ``logging_simple``
   - ``formatted_logging`` to ``logging_format``

Minor changes:

* Update dependencies
* Remove broken ``--args`` command line option.


Version 0.2.2 (2016-09-19)
--------------------------

* Add a new ``show`` command to display a benchmark file
* Issue #11: Display Python version in compare. Display also the performance
  version.
* CPython issue #26383; csv output: don't truncate digits for timings shorter
  than 1 us
* compare: Use sample unit of benchmarks, format values in the table
  output using the unit
* compare: Fix the table output if benchmarks only contain a single sample
* Remove unused -C/--control_label and -E/--experiment_label options
* Update perf dependency to 0.7.11 to get Benchmark.get_unit() and
  BenchmarkSuite.get_metadata()

Version 0.2.1 (2016-09-10)
--------------------------

* Add ``--csv`` option to the ``compare`` command
* Fix ``compare -O table`` output format
* Freeze indirect dependencies in requirements.txt
* ``run``: add ``--track-memory`` option to track the memory peak usage
* Update perf dependency to 0.7.8 to support memory tracking and the new
  ``--inherit-environ`` command line option
* If ``virtualenv`` command fail, try another command to create the virtual
  environment: catch ``virtualenv`` error
* The first command to upgrade pip to version ``>= 6.0`` now uses the ``pip``
  binary rather than ``python -m pip`` to support pip 1.0 which doesn't support
  ``python -m pip`` CLI.
* Update Django (1.10.1), Mercurial (3.9.1) and psutil (4.3.1)
* Rename ``--inherit_env`` command line option to ``--inherit-environ`` and fix
  it

Version 0.2 (2016-09-01)
------------------------

* Update Django dependency to 1.10
* Update Chameleon dependency to 2.24
* Add the ``--venv`` command line option
* Convert Python startup, Mercurial startup and 2to3 benchmarks to perf scripts
  (bm_startup.py, bm_hg_startup.py and bm_2to3.py)
* Pass the ``--affinity`` option to perf scripts rather than using the
  ``taskset`` command
* Put more installer and optional requirements into
  ``performance/requirements.txt``
* Cached ``.pyc`` files are no more removed before running a benchmark.
  Use ``venv recreate`` command to update a virtual environment if required.
* The broken ``--track_memory`` option has been removed. It will be added back
  when it will be fixed.
* Add performance version to metadata
* Upgrade perf dependency to 0.7.5 to get ``Benchmark.update_metadata()``

Version 0.1.2 (2016-08-27)
--------------------------

* Windows is now supported
* Add a new ``venv`` command to show, create, recrete or remove the virtual
  environment.
* Fix pybench benchmark (update to perf 0.7.4 API)
* performance now tries to install the ``psutil`` module on CPython for better
  system metrics in metadata and CPU pinning on Python 2.
* The creation of the virtual environment now also tries ``virtualenv`` and
  ``venv`` Python modules, not only the virtualenv command.
* The development version of performance now installs performance
  with "pip install -e <path_to_performance>"
* The GitHub project was renamed from ``python/benchmarks``
  to ``python/performance``.

Version 0.1.1 (2016-08-24)
--------------------------

* Fix the creation of the virtual environment
* Rename pybenchmarks script to pyperformance
* Add -p/--python command line option
* Add __main__ module to be able to run: python3 -m performance

Version 0.1 (2016-08-24)
------------------------

* First release after the conversion to the perf module and move to GitHub
* Removed benchmarks

  - django_v2, django_v3
  - rietveld
  - spitfire (and psyco): Spitfire is not available on PyPI
  - pystone
  - gcbench
  - tuple_gc_hell


History
-------

Projected moved to https://github.com/python/performance in August 2016. Files
reorganized, benchmarks patched to use the perf module to run benchmark in
multiple processes.

Project started in December 2008 by Collin Winter and Jeffrey Yasskin for the
Unladen Swallow project. The project was hosted at
https://hg.python.org/benchmarks until Feb 2016