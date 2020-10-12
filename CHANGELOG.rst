1.0.8
=====
* Made code comply to latest mypy 0.790 and pylint 2.6.0
* Made docstrings comply with pydocstyle
* Explicitly target Posix (and develop on a Windows machine so that bugs related
  to *e.g.*, path separators become obvious)
* Introduce continuous integration based on GitHub workflows
* Update package information (author email and URL)

1.0.7
=====
* Moved to github.com
* Moved datetime_glob.py to a module directory
* Added py.typed to comply with mypy

1.0.6
=====
* Added walk

1.0.5
=====
* Added as_maybe_datetime and as_maybe_date

1.0.4
=====
* Added fixed text to pattern segment

1.0.3
=====
* Added empty match as default value to match_segment

1.0.2
=====
* Added awalkdir test case
* Removed precondition in match_segment to allow for arbitrary patterns

1.0.1
=====
* Added multiple definition in docs
* Added as_time and as_date

1.0.0
=====
* Initial version
