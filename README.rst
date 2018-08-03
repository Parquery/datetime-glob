datetime-glob
=============

Parses date/times from a path given a glob pattern intertwined with date/time format akin to strptime/strftime format.

datetime.datetime.strptime suffices for simple date/time parsing. However, as soon as you need to handle wildcards,
it becomes tricky and you need to resort to regular expressions.

We found the glob patterns and strptime format to be far easier to read and write than regular expressions, and
encapsulated the logic involving regular expressions in this module.

Installation
============

* Create a virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate it:

.. code-block:: bash

    source venv3/bin/activate

* Install datetime-glob with pip:

.. code-block:: bash

    pip3 install datetime-glob

Usage
=====
To match a path:

.. code-block:: python

    >>> import datetime_glob
    >>> matcher = datetime_glob.Matcher(pattern='/some/path/*%Y-%m-%dT%H-%M-%SZ.jpg')
    >>> matcher.match(path='/some/path/some-text2016-07-03T21-22-23Z.jpg')
    datetime_glob.Match(year = 2016, month = 7, day = 3, hour = 21, minute = 22, second = 23, microsecond = None)

    >>> match.as_datetime()
    datetime.datetime(2016, 7, 3, 21, 22, 23)
    >>> match.as_date()
    datetime.date(2016, 7, 3)
    >>> match.as_time()
    datetime.time(21, 22, 23)

If you specify a directive for the same field twice, the matcher will make sure that the field has the same semantical
value in order to match:

.. code-block:: python

    >>> import datetime_glob
    >>> matcher = datetime_glob.Matcher(pattern='/some/path/%y/%Y-%m-%d.txt')

    >>> match = matcher.match(path='/some/path/16/2016-07-03.txt')
    >>> match
    datetime_glob.Match(year = 2016, month = 7, day = 3, hour = None, minute = None, second = None, microsecond = None)

    >>> match = matcher.match(path='/some/path/19/2016-07-03.txt')
    >>> type(match)
    <class 'NoneType'>

You can walk the pattern on the file system:

.. code-block:: python

    >>> import datetime_glob
    >>> for match, path in datetime_glob.walk(pattern='/some/path/*%Y/%m/%d/%H-%M-%SZ.jpg'):
    ...     dtime = match.as_datetime()
    ...     print(dtime, path)
    2016-03-04 12:13:14 /some/path/saved-2016/03/04/12-13-14Z.jpg
    2017-11-23 22:23:24 /some/path/restored-2017/11/23/22-23-24Z.jpg

To iterate manually over a tree, and match incrementally each path segment by yourself:

.. code-block:: python

    >>> import datetime_glob
    >>> pattern_segments = datetime_glob.parse_pattern(pattern='/some/path/*%Y/%m/%d/%H-%M-%SZ.jpg')
    >>> match = datetime_glob.Match()

    >>> match=datetime_glob.match_segment(segment='some', pattern_segment=pattern_segments[0], match=match)
    >>> match
    datetime_glob.Match(year = None, month = None, day = None, hour = None, minute = None, second = None,
                        microsecond = None)

    >>> match=datetime_glob.match_segment(segment='path', pattern_segment=pattern_segments[1], match=match)
    >>> match
    datetime_glob.Match(year = None, month = None, day = None, hour = None, minute = None, second = None,
                        microsecond = None)

    >>> match=datetime_glob.match_segment(segment='some-text2016', pattern_segment=pattern_segments[2], match=match)
    >>> match
    datetime_glob.Match(year = 2016, month = None, day = None, hour = None, minute = None, second = None,
                        microsecond = None)

    >>> match=datetime_glob.match_segment(segment='07', pattern_segment=pattern_segments[3], match=match)
    >>> match
    datetime_glob.Match(year = 2016, month = 7, day = None, hour = None, minute = None, second = None,
                        microsecond = None)

    >>> match=datetime_glob.match_segment(segment='03', pattern_segment=pattern_segments[4], match=match)
    >>> match
    datetime_glob.Match(year = 2016, month = 7, day = 3, hour = None, minute = None, second = None, microsecond = None)

    >>> match=datetime_glob.match_segment(segment='21-22-23Z.jpg', pattern_segment=pattern_segments[5], match=match)
    >>> match
    datetime_glob.Match(year = 2016, month = 7, day = 3, hour = 21, minute = 22, second = 23, microsecond = None)


Supported strftime directives
=============================
(subset from https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior)

=========   =========================================================   ==========================
Directive   Meaning                                                     Example
=========   =========================================================   ==========================
%d          Day of the month as a zero-padded decimal number.           01, 02, …, 31
%-d         Day of the month as a decimal number.                       1, 2, …, 31
%m          Month as a zero-padded decimal number.                      01, 02, …, 12
%-m         Month as a  decimal number.                                 1, 2, …, 12
%y          Year without century as a zero-padded decimal number.       00, 01, …, 99
%Y          Year with century as a decimal number.                      1970, 1988, 2001, 2013
%H          Hour (24-hour clock) as a zero-padded decimal number.       00, 01, …, 23
%-H         Hour (24-hour clock) as a decimal number.                   0, 1, …, 23
%M          Minute as a zero-padded decimal number.                     00, 01, …, 59
%-M         Minute as a decimal number.                                 0, 1, …, 59
%S          Second as a zero-padded decimal number.                     00, 01, …, 59
%-S         Second as a decimal number.                                 0, 1, …, 59
%f          Microsecond as a decimal number, zero-padded on the left.   000000, 000001, …, 999999
%%          A literal '%' character.                                    %
=========   =========================================================   ==========================

Development
===========

* Check out the repository.

* In the repository root, create the virtual environment:

.. code-block:: bash

    python3 -m venv venv3

* Activate the virtual environment:

.. code-block:: bash

    source venv3/bin/activate

* Install the development dependencies:

.. code-block:: bash

    pip3 install -e .[dev]

* Run `precommit.py` to execute pre-commit checks locally.