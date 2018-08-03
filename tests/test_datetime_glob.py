#!/usr/bin/env python3

# pylint: disable=missing-docstring
# pylint: disable=invalid-name
import datetime
import pathlib
import tempfile
import unittest

import datetime_glob


def match_equal(match: datetime_glob.Match, other: datetime_glob.Match) -> bool:
    if match is None and other is None:
        return True

    if (match is None and other is not None) or (match is not None and other is None):
        return False

    return match.year == other.year and \
           match.month == other.month and \
           match.day == other.day and \
           match.hour == other.hour and \
           match.minute == other.minute and \
           match.second == other.second and \
           match.microsecond == other.microsecond


class TestDatetimeGlob(unittest.TestCase):
    def test_parse_pattern_segment_invalid(self):
        with self.assertRaises(ValueError):
            _ = datetime_glob.parse_pattern_segment(pattern_segment='some text %1')

    def test_parse_pattern_segment_as_text(self):
        # yapf: disable
        table = [
            ('some -text_[x]', 'some -text_[x]'),
            ('?', None),
            ('*a?b*', None),
            ('%d', None),
            ('%-d', None),
            ('%m', None),
            ('%-m', None),
            ('%y', None),
            ('%Y', None),
            ('%H', None),
            ('%-H', None),
            ('%M', None),
            ('%-M', None),
            ('%S', None),
            ('%-S', None),
            ('%f', None),
            ('%%', '%'),
            ('%y%y', None),
            ('some text *%%*x%Y-%m-%dT%H-%M-%SZ.jpg', None)
        ]
        # yapf: enable

        for pattern_segment, expected_text in table:
            patseg = datetime_glob.parse_pattern_segment(pattern_segment=pattern_segment)

            if expected_text is not None:
                self.assertEqual(patseg.text, expected_text)
                self.assertIsNone(patseg.regex)
            else:
                self.assertIsNone(patseg.text)
                self.assertIsNotNone(patseg.regex)

    def test_parse_pattern_segment(self):
        # yapf: disable
        table = [
            ('some -text_[x]', None, {}),
            ('*', '^.*$', {}),
            ('?', '^.$', {}),
            ('*a?b*', '^.*a.b.*$', {}),
            ('%d', '^(0[1-9]|1[0-9]|2[0-9]|3[0-1])$', {1: '%d'}),
            ('%-d', '^(1[0-9]|2[0-9]|3[0-1]|[1-9])$', {1: '%-d'}),
            ('%m', '^(0[1-9]|1[0-2])$', {1: '%m'}),
            ('%-m', '^(1[0-2]|[1-9])$', {1: '%-m'}),
            ('%y', '^([0-9]{2})$', {1: '%y'}),
            ('%Y', '^([0-9]{4})$', {1: '%Y'}),
            ('%H', '^(0[0-9]|1[0-9]|2[0-3])$', {1: '%H'}),
            ('%-H', '^(1[0-9]|2[0-3]|[0-9])$', {1: '%-H'}),
            ('%M', '^([0-5][0-9])$', {1: '%M'}),
            ('%-M', '^([1-5][0-9]|[0-9])$', {1: '%-M'}),
            ('%S', '^([0-5][0-9])$', {1: '%S'}),
            ('%-S', '^([1-5][0-9]|[0-9])$', {1: '%-S'}),
            ('%f', '^([0-9]{6})$', {1: '%f'}),
            ('%%', None, {}),
            ('%y%y', '^([0-9]{2})([0-9]{2})$', {1: '%y', 2: '%y'}),
            ('some text *%%*x%Y-%m-%dT%H-%M-%SZ.jpg',
             '^some\\ text\\ .*%.*x'
             '([0-9]{4})\\-'
             '(0[1-9]|1[0-2])\\-'
             '(0[1-9]|1[0-9]|2[0-9]|3[0-1])'
             'T'
             '(0[0-9]|1[0-9]|2[0-3])\\-'
             '([0-5][0-9])\\-'
             '([0-5][0-9])Z\\.jpg$',
             {1: '%Y', 2: '%m', 3: '%d', 4: '%H', 5: '%M', 6: '%S'})
        ]
        # yapf: enable

        for pattern_segment, expected_regex, expected_group_map in table:
            patseg = datetime_glob.parse_pattern_segment(pattern_segment=pattern_segment)

            if expected_regex is None:
                self.assertIsNotNone(patseg.text)
            else:
                self.assertIsNotNone(patseg.regex, pattern_segment)
                self.assertEqual(patseg.regex.pattern, expected_regex, pattern_segment)
                self.assertDictEqual(patseg.group_map, expected_group_map, pattern_segment)

    def test_parse_pattern_as_prefix_segments(self):
        # yapf: disable
        table = [
            ('/*', '/', 1),
            ('/some-text/*', '/some-text', 1),
            ('/some-text/%Y', '/some-text', 1),
            ('/some-text/%%', '/some-text/%', 0),
            ('/some-text/%Y/other-text', '/some-text', 2),
            ('some-text/*', 'some-text', 1),
        ]
        # yapf: enable

        for pattern, expected_prefix, expected_count in table:
            prefix, patsegs = datetime_glob.parse_pattern_as_prefix_segments(pattern=pattern)
            self.assertEqual(prefix, expected_prefix, pattern)
            self.assertEqual(len(patsegs), expected_count, pattern)

    def test_match_segment(self):
        # yapf: disable
        table = [
            ('some text *%%*x%Y-%m-%dT%H-%M-%S.%fZ.jpg', 'some text aa%bbx2016-12-02T03-04-05.123456Z.jpg',
             datetime_glob.Match(2016, 12, 2, 3, 4, 5, 123456)),
            ('decimal %Y-%-m-%-dT%-H-%-M-%-SZ.jpg', 'decimal 2016-1-2T3-4-5Z.jpg',
             datetime_glob.Match(2016, 1, 2, 3, 4, 5)),
            ('double year %y %Y', 'double year 18 2018', datetime_glob.Match(year=2018)),
            ('double year %y %Y', 'double year 17 2018', None),
            ('invalid day %Y-%m-%d', 'invalid day 2018-02-31', None)
        ]
        # yapf: enable

        for pattern_segment_str, segment, expected in table:
            patseg = datetime_glob.parse_pattern_segment(pattern_segment=pattern_segment_str)
            mtch = datetime_glob.match_segment(segment=segment, pattern_segment=patseg)

            self.assertTrue(
                match_equal(match=mtch, other=expected), "for input: {!r}, got: {}, expected: {}".format(
                    segment, mtch, expected))

    def test_match_segment_for_arbitrary_patterns(self):
        patseg = datetime_glob.parse_pattern_segment(pattern_segment='%-d/%-m/%Y,%H:%M:%S*')
        match = datetime_glob.match_segment(segment='9/4/2013,00:00:00,7.8,7.4,9.53', pattern_segment=patseg)
        self.assertEqual(match.as_datetime(), datetime.datetime(2013, 4, 9))

    def test_match_multiple_definition(self):
        mtcher = datetime_glob.Matcher(pattern='/some/path/%Y-%m-%d/%Y-%m-%dT%H-%M-%S.%fZ.jpg')
        mtch = mtcher.match(path='/some/path/2016-12-02/2016-12-02T03-04-05.123456Z.jpg')
        self.assertEqual(mtch.as_datetime(), datetime.datetime(2016, 12, 2, 3, 4, 5, 123456))

        mtch = mtcher.match(path='/some/path/2017-04-12/2016-12-02T03-04-05.123456Z.jpg')
        self.assertIsNone(mtch)

    def test_match_conversion(self):
        mtcher = datetime_glob.Matcher(pattern='/some/path/%Y-%m-%dT%H-%M-%S.%fZ.jpg')
        mtch = mtcher.match(path='/some/path/2016-12-02T03-04-05.123456Z.jpg')
        self.assertEqual(mtch.as_datetime(), datetime.datetime(2016, 12, 2, 3, 4, 5, 123456))
        self.assertEqual(mtch.as_maybe_datetime(), datetime.datetime(2016, 12, 2, 3, 4, 5, 123456))
        self.assertEqual(mtch.as_date(), datetime.date(2016, 12, 2))
        self.assertEqual(mtch.as_maybe_date(), datetime.date(2016, 12, 2))
        self.assertEqual(mtch.as_time(), datetime.time(3, 4, 5, 123456))

        # match time without date
        mtcher = datetime_glob.Matcher(pattern='/some/path/%H-%M-%S.jpg')
        mtch = mtcher.match(path='/some/path/03-04-05.jpg')

        with self.assertRaises(ValueError):
            _ = mtch.as_datetime()
            _ = mtch.as_date()

        self.assertIsNone(mtch.as_maybe_datetime())
        self.assertIsNone(mtch.as_maybe_date())

        self.assertEqual(mtch.as_time(), datetime.time(3, 4, 5, 0))

    def test_matcher_preconditions(self):
        # yapf: disable
        table = [
            ('/', ValueError),
            ('', ValueError),
            ('/some/../path', ValueError),
            ('/some//path/*', None),
            ('/some/./path/*', None)
        ]
        # yapf: enable

        for pattern, expected_exception in table:
            if expected_exception is not None:
                with self.assertRaises(expected_exception):
                    _ = datetime_glob.Matcher(pattern=pattern)
            else:
                _ = datetime_glob.Matcher(pattern=pattern)

    def test_matcher_match_preconditions(self):
        mtcher = datetime_glob.Matcher('/some/./path/*%Y-%m-%dT%H-%M-%SZ.jpg')

        # yapf: disable
        table = [
            ('/', ValueError),
            ('', ValueError),
            ('/some/../path', ValueError),
            ('some/relative/path', ValueError),
            ('/some//path', None),
            ('/some/./path', None)
        ]
        # yapf: enable

        for path, expected_exception in table:
            if expected_exception is not None:
                with self.assertRaises(expected_exception):
                    _ = mtcher.match(path=path)

                with self.assertRaises(expected_exception):
                    _ = mtcher.match(path=pathlib.Path(path))

            else:
                _ = mtcher.match(path=path)
                _ = mtcher.match(path=pathlib.Path(path))

        relative_mtcher = datetime_glob.Matcher('some/./path/*%Y-%m-%dT%H-%M-%SZ.jpg')
        with self.assertRaises(ValueError):
            relative_mtcher.match('/some/absolute/path')

    def test_matcher(self):
        relative_pattern = 'some/./path/*%Y-%m-%dT%H-%M-%SZ.jpg'

        # yapf: disable
        table = [
            ('some/path/ooo2016-07-03T21-22-23Z.jpg', datetime_glob.Match(2016, 7, 3, 21, 22, 23)),
            ('some/path/2016-07-03T21-22-23Z.jpg', datetime_glob.Match(2016, 7, 3, 21, 22, 23)),
            ('some/./path/2016-07-03T21-22-23Z.jpg', datetime_glob.Match(2016, 7, 3, 21, 22, 23)),
            ('some//path/2016-07-03T21-22-23Z.jpg', datetime_glob.Match(2016, 7, 3, 21, 22, 23)),
            ('some//path/2016-07-03T21-22-23Z.jpg', datetime_glob.Match(2016, 7, 3, 21, 22, 23)),
            ('some/other/path/2016-07-03T21-22-23Z.jpg', None),
            ('some//path/2016-07-03', None)
        ]
        # yapf: enable

        for relative_path, expected_match in table:
            # test both absolute and relative paths
            abs_matcher = datetime_glob.Matcher(pattern='/{}'.format(relative_pattern))
            abs_pth = '/{}'.format(relative_path)

            self.assertTrue(match_equal(match=abs_matcher.match(path=abs_pth), other=expected_match))

            rel_matcher = datetime_glob.Matcher(pattern=relative_pattern)
            self.assertTrue(match_equal(match=rel_matcher.match(path=relative_path), other=expected_match))

    def test_sort_listdir(self):
        with tempfile.TemporaryDirectory() as tempdir:
            pth = pathlib.Path(tempdir)
            (pth / 'some-description-20.3.2016.txt').write_text('tested')
            (pth / 'other-description-7.4.2016.txt').write_text('tested')
            (pth / 'yet-another-description-1.1.2016.txt').write_text('tested')

            matcher = datetime_glob.Matcher(pattern='*%-d.%-m.%Y.txt')
            subpths_matches = [(subpth, matcher.match(subpth.name)) for subpth in pth.iterdir()]
            dtimes_subpths = [(mtch.as_datetime(), subpth) for subpth, mtch in subpths_matches]

            subpths = [subpth for _, subpth in sorted(dtimes_subpths)]

            # yapf: disable
            expected = [
                pth / 'yet-another-description-1.1.2016.txt',
                pth / 'some-description-20.3.2016.txt',
                pth / 'other-description-7.4.2016.txt'
            ]
            # yapf: enable

            self.assertListEqual(subpths, expected)

    def test_walk(self):
        with tempfile.TemporaryDirectory() as tempdir:
            tmppth = pathlib.Path(tempdir)

            dtimes = [
                datetime.datetime(2016, 10, 3, 21, 22, 23),
                datetime.datetime(2016, 10, 4, 11, 12, 13),
                datetime.datetime(2016, 10, 5, 1, 2, 3)
            ]

            for dtime in dtimes:
                pth = tmppth / dtime.strftime('%Y-%m-%d') / dtime.strftime('%H-%M-%S.txt')
                pth.parent.mkdir(exist_ok=True, parents=True)
                pth.write_text('tested')

                unmatched_pth = tmppth / dtime.strftime('%Y-%m-%d') / 'unmatched.txt'
                unmatched_pth.write_text('tested')

            (tmppth / 'some-dummy-directory').mkdir(exist_ok=True)

            # empty matched directory
            (tmppth / '2016-10-06').mkdir(exist_ok=True)

            mtches_pths = list(datetime_glob.walk(pattern=tempdir + "/%Y-%m-%d/%H-%M-%S.txt"))

            dtimes_pths = sorted([(mtch.as_datetime(), str(pth.relative_to(tmppth))) for mtch, pth in mtches_pths])
            self.assertListEqual(dtimes_pths, [(datetime.datetime(2016, 10, 3, 21, 22, 23), '2016-10-03/21-22-23.txt'),
                                               (datetime.datetime(2016, 10, 4, 11, 12, 13), '2016-10-04/11-12-13.txt'),
                                               (datetime.datetime(2016, 10, 5, 1, 2, 3), '2016-10-05/01-02-03.txt')])


if __name__ == '__main__':
    unittest.main()
