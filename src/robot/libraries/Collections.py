#  Copyright 2008-2015 Nokia Networks
#  Copyright 2016-     Robot Framework Foundation
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import copy
from ast import literal_eval

from robot.api import logger
from robot.utils import (get_error_message, is_dict_like, is_list_like, is_string, is_truthy,
                         Matcher, NOT_SET, plural_or_not as s, seq2str, seq2str2,
                         type_name)
from robot.utils.asserts import assert_equal
from robot.version import get_version


class _List:

    def convert_to_list(self, item):
        """Converts the given ``item`` to a Python ``list`` type.

        Mainly useful for converting tuples and other iterable to lists.
        Use `Create List` from the BuiltIn library for constructing new lists.
        """
        return list(item)

    def append_to_list(self, list_, *values):
        """Adds ``values`` to the end of ``list``.

        Example:
        | Append To List | ${L1} | xxx |   |   |
        | Append To List | ${L2} | x   | y | z |
        =>
        | ${L1} = ['a', 'xxx']
        | ${L2} = ['a', 'b', 'x', 'y', 'z']
        """
        self._validate_list(list_)
        for value in values:
            list_.append(value)

    def insert_into_list(self, list_, index, value):
        """Inserts ``value`` into ``list`` to the position specified with ``index``.

        Index ``0`` adds the value into the first position, ``1`` to the second,
        and so on. Inserting from right works with negative indices so that
        ``-1`` is the second last position, ``-2`` third last, and so on. Use
        `Append To List` to add items to the end of the list.

        If the absolute value of the index is greater than
        the length of the list, the value is added at the end
        (positive index) or the beginning (negative index). An index
        can be given either as an integer or a string that can be
        converted to an integer.

        Example:
        | Insert Into List | ${L1} | 0     | xxx |
        | Insert Into List | ${L2} | ${-1} | xxx |
        =>
        | ${L1} = ['xxx', 'a']
        | ${L2} = ['a', 'xxx', 'b']
        """
        self._validate_list(list_)
        list_.insert(self._index_to_int(index), value)

    def combine_lists(self, *lists):
        """Combines the given ``lists`` together and returns the result.

        The given lists are not altered by this keyword.

        Example:
        | ${x} = | Combine Lists | ${L1} | ${L2} |       |
        | ${y} = | Combine Lists | ${L1} | ${L2} | ${L1} |
        =>
        | ${x} = ['a', 'a', 'b']
        | ${y} = ['a', 'a', 'b', 'a']
        | ${L1} and ${L2} are not changed.
        """
        self._validate_lists(*lists)
        ret = []
        for item in lists:
            ret.extend(item)
        return ret

    def set_list_value(self, list_, index, value):
        """Sets the value of ``list`` specified by ``index`` to the given ``value``.

        Index ``0`` means the first position, ``1`` the second and so on.
        Similarly, ``-1`` is the last position, ``-2`` second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted to
        an integer.

        Example:
        | Set List Value | ${L3} | 1  | xxx |
        | Set List Value | ${L3} | -1 | yyy |
        =>
        | ${L3} = ['a', 'xxx', 'yyy']

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax. This is equivalent to the above:
        | ${L3}[1] =  | Set Variable | xxx |
        | ${L3}[-1] = | Set Variable | yyy |
        """
        self._validate_list(list_)
        try:
            list_[self._index_to_int(index)] = value
        except IndexError:
            self._index_error(list_, index)

    def remove_values_from_list(self, list_, *values):
        """Removes all occurrences of given ``values`` from ``list``.

        It is not an error if a value does not exist in the list at all.

        Example:
        | Remove Values From List | ${L4} | a | c | e | f |
        =>
        | ${L4} = ['b', 'd']
        """
        self._validate_list(list_)
        for value in values:
            while value in list_:
                list_.remove(value)

    def remove_from_list(self, list_, index):
        """Removes and returns the value specified with an ``index`` from ``list``.

        Index ``0`` means the first position, ``1`` the second and so on.
        Similarly, ``-1`` is the last position, ``-2`` the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Example:
        | ${x} = | Remove From List | ${L2} | 0 |
        =>
        | ${x} = 'a'
        | ${L2} = ['b']
        """
        self._validate_list(list_)
        try:
            return list_.pop(self._index_to_int(index))
        except IndexError:
            self._index_error(list_, index)

    def remove_duplicates(self, list_):
        """Returns a list without duplicates based on the given ``list``.

        Creates and returns a new list that contains all items in the given
        list so that one item can appear only once. Order of the items in
        the new list is the same as in the original except for missing
        duplicates. Number of the removed duplicates is logged.
        """
        self._validate_list(list_)
        ret = []
        for item in list_:
            if item not in ret:
                ret.append(item)
        removed = len(list_) - len(ret)
        logger.info(f'{removed} duplicate{s(removed)} removed.')
        return ret

    def get_from_list(self, list_, index):
        """Returns the value specified with an ``index`` from ``list``.

        The given list is never altered by this keyword.

        Index ``0`` means the first position, ``1`` the second, and so on.
        Similarly, ``-1`` is the last position, ``-2`` the second last, and so on.
        Using an index that does not exist on the list causes an error.
        The index can be either an integer or a string that can be converted
        to an integer.

        Examples (including Python equivalents in comments):
        | ${x} = | Get From List | ${L5} | 0  | # L5[0]  |
        | ${y} = | Get From List | ${L5} | -2 | # L5[-2] |
        =>
        | ${x} = 'a'
        | ${y} = 'd'
        | ${L5} is not changed
        """
        self._validate_list(list_)
        try:
            return list_[self._index_to_int(index)]
        except IndexError:
            self._index_error(list_, index)

    def get_slice_from_list(self, list_, start=0, end=None):
        """Returns a slice of the given list between ``start`` and ``end`` indexes.

        The given list is never altered by this keyword.

        If both ``start`` and ``end`` are given, a sublist containing values
        from ``start`` to ``end`` is returned. This is the same as
        ``list[start:end]`` in Python. To get all items from the beginning,
        use 0 as the start value, and to get all items until and including
        the end, use ``None`` (default) as the end value.

        Using ``start`` or ``end`` not found on the list is the same as using
        the largest (or smallest) available index.

        Examples (incl. Python equivalents in comments):
        | ${x} = | Get Slice From List | ${L5} | 2      | 4 | # L5[2:4]    |
        | ${y} = | Get Slice From List | ${L5} | 1      |   | # L5[1:None] |
        | ${z} = | Get Slice From List | ${L5} | end=-2 |   | # L5[0:-2]   |
        =>
        | ${x} = ['c', 'd']
        | ${y} = ['b', 'c', 'd', 'e']
        | ${z} = ['a', 'b', 'c']
        | ${L5} is not changed
        """
        self._validate_list(list_)
        start = self._index_to_int(start, True)
        if end is not None:
            end = self._index_to_int(end)
        return list_[start:end]

    def count_values_in_list(self, list_, value, start=0, end=None):
        """Returns the number of occurrences of the given ``value`` in ``list``.

        The search can be narrowed to the selected sublist by the ``start`` and
        ``end`` indexes having the same semantics as with `Get Slice From List`
        keyword. The given list is never altered by this keyword.

        Example:
        | ${x} = | Count Values In List | ${L3} | b |
        =>
        | ${x} = 1
        | ${L3} is not changed
        """
        self._validate_list(list_)
        return self.get_slice_from_list(list_, start, end).count(value)

    def get_index_from_list(self, list_, value, start=0, end=None):
        """Returns the index of the first occurrence of the ``value`` on the list.

        The search can be narrowed to the selected sublist by the ``start`` and
        ``end`` indexes having the same semantics as with `Get Slice From List`
        keyword. In case the value is not found, -1 is returned. The given list
        is never altered by this keyword.

        Example:
        | ${x} = | Get Index From List | ${L5} | d |
        =>
        | ${x} = 3
        | ${L5} is not changed
        """
        self._validate_list(list_)
        if start == '':
            start = 0
        list_ = self.get_slice_from_list(list_, start, end)
        try:
            return int(start) + list_.index(value)
        except ValueError:
            return -1

    def copy_list(self, list_, deepcopy=False):
        """Returns a copy of the given list.

        If the optional ``deepcopy`` is given a true value, the returned
        list is a deep copy. New option in Robot Framework 3.1.2.

        The given list is never altered by this keyword.
        """
        self._validate_list(list_)
        if deepcopy:
            return copy.deepcopy(list_)
        return list_[:]

    def reverse_list(self, list_):
        """Reverses the given list in place.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to keep also the original order.

        | Reverse List | ${L3} |
        =>
        | ${L3} = ['c', 'b', 'a']
        """
        self._validate_list(list_)
        list_.reverse()

    def sort_list(self, list_):
        """Sorts the given list in place.

        Sorting fails if items in the list are not comparable with each others.
        On Python 2 most objects are comparable, but on Python 3 comparing,
        for example, strings with numbers is not possible.

        Note that the given list is changed and nothing is returned. Use
        `Copy List` first, if you need to keep also the original order.
        """
        self._validate_list(list_)
        list_.sort()

    def list_should_contain_value(self, list_, value, msg=None, ignore_case=False):
        """Fails if the ``value`` is not found from ``list``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_list(list_)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(value) in normalize(list_),
                          f"{seq2str2(list_)} does not contain value '{value}'.", msg)

    def list_should_not_contain_value(self, list_, value, msg=None, ignore_case=False):
        """Fails if the ``value`` is found from ``list``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_list(list_)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(value) not in normalize(list_),
                          f"{seq2str2(list_)} contains value '{value}'.",
                          msg)

    def list_should_not_contain_duplicates(self, list_, msg=None, ignore_case=False):
        """Fails if any element in the ``list`` is found from it more than once.

        The default error message lists all the elements that were found
        from the ``list`` multiple times, but it can be overridden by giving
        a custom ``msg``. All multiple times found items and their counts are
        also logged.

        This keyword works with all iterables that can be converted to a list.
        The original iterable is never altered.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_list(list_)
        if not isinstance(list_, list):
            list_ = list(list_)
        dupes = []
        normalize = Normalizer(ignore_case).normalize
        for item in normalize(list_):
            if item not in dupes:
                count = normalize(list_).count(item)
                if count > 1:
                    logger.info(f"'{item}' found {count} times.")
                    dupes.append(item)
        if dupes:
            raise AssertionError(msg or f'{seq2str(dupes)} found multiple times.')

    def lists_should_be_equal(self, list1, list2, msg=None, values=True,
                              names=None, ignore_order=False, ignore_case=False):
        """Fails if given lists are unequal.

        The keyword first verifies that the lists have equal lengths, and then
        it checks are all their values equal. Possible differences between the
        values are listed in the default error message like ``Index 4: ABC !=
        Abc``. The types of the lists do not need to be the same. For example,
        Python tuple and list with same content are considered equal.

        The error message can be configured using ``msg`` and ``values``
        arguments:
        - If ``msg`` is not given, the default error message is used.
        - If ``msg`` is given and ``values`` gets a value considered true
          (see `Boolean arguments`), the error message starts with the given
          ``msg`` followed by a newline and the default message.
        - If ``msg`` is given and ``values``  is not given a true value,
          the error message is just the given ``msg``.

        The optional ``names`` argument can be used for naming the indices
        shown in the default error message. It can either be a list of names
        matching the indices in the lists or a dictionary where keys are
        indices that need to be named. It is not necessary to name all indices.
        When using a dictionary, keys can be either integers
        or strings that can be converted to integers.

        Examples:
        | ${names} = | Create List | First Name | Family Name | Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |
        | ${names} = | Create Dictionary | 0=First Name | 2=Email |
        | Lists Should Be Equal | ${people1} | ${people2} | names=${names} |

        If the items in index 2 would differ in the above examples, the error
        message would contain a row like ``Index 2 (email): name@foo.com !=
        name@bar.com``.

        The optional ``ignore_order`` argument can be used to ignore the order
        of the elements in the lists. Using it requires items to be sortable.
        This is new in Robot Framework 3.2.

        Example:
        | ${list1} = | Create List | apple | cherry | banana |
        | ${list2} = | Create List | cherry | banana | apple |
        | Lists Should Be Equal | ${list1} | ${list2} | ignore_order=True |

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_lists(list1, list2)
        len1 = len(list1)
        len2 = len(list2)
        _verify_condition(len1 == len2,
                          f'Lengths are different: {len1} != {len2}',
                          msg, values)
        names = self._get_list_index_name_mapping(names, len1)
        if ignore_order:
            list1 = sorted(list1)
            list2 = sorted(list2)
        normalize = Normalizer(ignore_case).normalize
        diffs = '\n'.join(self._yield_list_diffs(normalize(list1), normalize(list2),
                                                 names))
        _verify_condition(not diffs,
                          f'Lists are different:\n{diffs}',
                          msg, values)

    def _get_list_index_name_mapping(self, names, list_length):
        if not names:
            return {}
        if is_dict_like(names):
            return dict((int(index), names[index]) for index in names)
        return dict(zip(range(list_length), names))

    def _yield_list_diffs(self, list1, list2, names):
        for index, (item1, item2) in enumerate(zip(list1, list2)):
            name = f' ({names[index]})' if index in names else ''
            try:
                assert_equal(item1, item2, msg=f'Index {index}{name}')
            except AssertionError as err:
                yield str(err)

    def list_should_contain_sub_list(self, list1, list2, msg=None,
                                     values=True, ignore_case=False):
        """Fails if not all elements in ``list2`` are found in ``list1``.

        The order of values and the number of values are not taken into
        account.

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_lists(list1, list2)
        normalize = Normalizer(ignore_case).normalize
        diffs = ', '.join(str(item) for item in normalize(list2) if
                          item not in normalize(list1))
        _verify_condition(not diffs,
                          f'Following values were not found from first list: {diffs}',
                          msg, values)

    def log_list(self, list_, level='INFO'):
        """Logs the length and contents of the ``list`` using given ``level``.

        Valid levels are TRACE, DEBUG, INFO (default), and WARN.

        If you only want to the length, use keyword `Get Length` from
        the BuiltIn library.
        """
        self._validate_list(list_)
        logger.write('\n'.join(self._log_list(list_)), level)

    def _log_list(self, list_):
        if not list_:
            yield 'List is empty.'
        elif len(list_) == 1:
            yield f'List has one item:\n{list_[0]}'
        else:
            yield f'List length is {len(list_)} and it contains following items:'
            for index, item in enumerate(list_):
                yield f'{index}: {item}'

    def _index_to_int(self, index, empty_to_zero=False):
        if empty_to_zero and not index:
            return 0
        try:
            return int(index)
        except ValueError:
            raise ValueError(f"Cannot convert index '{index}' to an integer.")

    def _index_error(self, list_, index):
        raise IndexError(f'Given index {index} is out of the range 0-{len(list_)-1}.')

    def _validate_list(self, list_, position=1):
        if not is_list_like(list_):
            raise TypeError(f"Expected argument {position} to be a list or list-like, "
                            f"got {type_name(list_)} instead.")

    def _validate_lists(self, *lists):
        for index, item in enumerate(lists, start=1):
            self._validate_list(item, index)

class _Dictionary:

    def convert_to_dictionary(self, item):
        """Converts the given ``item`` to a Python ``dict`` type.

        Mainly useful for converting other mappings to normal dictionaries.
        This includes converting Robot Framework's own ``DotDict`` instances
        that it uses if variables are created using the ``&{var}`` syntax.

        Use `Create Dictionary` from the BuiltIn library for constructing new
        dictionaries.
        """
        return dict(item)

    def set_to_dictionary(self, dictionary, *key_value_pairs, **items):
        """Adds the given ``key_value_pairs`` and/or ``items`` to the ``dictionary``.

        If given items already exist in the dictionary, their values are updated.

        It is easiest to specify items using the ``name=value`` syntax:
        | Set To Dictionary | ${D1} | key=value | second=${2} |
        =>
        | ${D1} = {'a': 1, 'key': 'value', 'second': 2}

        A limitation of the above syntax is that keys must be strings.
        That can be avoided by passing keys and values as separate arguments:
        | Set To Dictionary | ${D1} | key | value | ${2} | value 2 |
        =>
        | ${D1} = {'a': 1, 'key': 'value', 2: 'value 2'}

        Starting from Robot Framework 6.1, it is also possible to use the native
        item assignment syntax. This is equivalent to the above:
        | ${D1}[key] =  | Set Variable | value |
        | ${D1}[${2}] = | Set Variable | value 2 |
        """
        self._validate_dictionary(dictionary)
        if len(key_value_pairs) % 2 != 0:
            raise ValueError("Adding data to a dictionary failed. There "
                             "should be even number of key-value-pairs.")
        for i in range(0, len(key_value_pairs), 2):
            dictionary[key_value_pairs[i]] = key_value_pairs[i+1]
        dictionary.update(items)
        return dictionary

    def remove_from_dictionary(self, dictionary, *keys):
        """Removes the given ``keys`` from the ``dictionary``.

        If the given ``key`` cannot be found from the ``dictionary``, it
        is ignored.

        Example:
        | Remove From Dictionary | ${D3} | b | x | y |
        =>
        | ${D3} = {'a': 1, 'c': 3}
        """
        self._validate_dictionary(dictionary)
        for key in keys:
            if key in dictionary:
                value = dictionary.pop(key)
                logger.info(f"Removed item with key '{key}' and value '{value}'.")
            else:
                logger.info(f"Key '{key}' not found.")

    def pop_from_dictionary(self, dictionary, key, default=NOT_SET):
        """Pops the given ``key`` from the ``dictionary`` and returns its value.

        By default the keyword fails if the given ``key`` cannot be found from
        the ``dictionary``. If optional ``default`` value is given, it will be
        returned instead of failing.

        Example:
        | ${val}= | Pop From Dictionary | ${D3} | b |
        =>
        | ${val} = 2
        | ${D3} = {'a': 1, 'c': 3}
        """
        self._validate_dictionary(dictionary)
        if default is NOT_SET:
            self.dictionary_should_contain_key(dictionary, key)
            return dictionary.pop(key)
        return dictionary.pop(key, default)

    def keep_in_dictionary(self, dictionary, *keys):
        """Keeps the given ``keys`` in the ``dictionary`` and removes all other.

        If the given ``key`` cannot be found from the ``dictionary``, it
        is ignored.

        Example:
        | Keep In Dictionary | ${D5} | b | x | d |
        =>
        | ${D5} = {'b': 2, 'd': 4}
        """
        self._validate_dictionary(dictionary)
        remove_keys = [k for k in dictionary if k not in keys]
        self.remove_from_dictionary(dictionary, *remove_keys)

    def copy_dictionary(self, dictionary, deepcopy=False):
        """Returns a copy of the given dictionary.

        The ``deepcopy`` argument controls should the returned dictionary be
        a [https://docs.python.org/library/copy.html|shallow or deep copy].
        By default returns a shallow copy, but that can be changed by giving
        ``deepcopy`` a true value (see `Boolean arguments`). This is a new
        option in Robot Framework 3.1.2. Earlier versions always returned
        shallow copies.

        The given dictionary is never altered by this keyword.
        """
        self._validate_dictionary(dictionary)
        if deepcopy:
            return copy.deepcopy(dictionary)
        return dictionary.copy()

    def get_dictionary_keys(self, dictionary, sort_keys=True):
        """Returns keys of the given ``dictionary`` as a list.

        By default keys are returned in sorted order (assuming they are
        sortable), but they can be returned in the original order by giving
        ``sort_keys``  a false value (see `Boolean arguments`). Notice that
        with Python 3.5 and earlier dictionary order is undefined unless using
        ordered dictionaries.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Keys | ${D3} |
        | ${unsorted} = | Get Dictionary Keys | ${D3} | sort_keys=False |
        =>
        | ${sorted} = ['a', 'b', 'c']
        | ${unsorted} = ['b', 'a', 'c']   # Order depends on Python version.

        ``sort_keys`` is a new option in Robot Framework 3.1.2. Earlier keys
        were always sorted.
        """
        self._validate_dictionary(dictionary)
        keys = dictionary.keys()
        if sort_keys:
            try:
                return sorted(keys)
            except TypeError:
                pass
        return list(keys)

    def get_dictionary_values(self, dictionary, sort_keys=True):
        """Returns values of the given ``dictionary`` as a list.

        Uses `Get Dictionary Keys` to get keys and then returns corresponding
        values. By default keys are sorted and values returned in that order,
        but this can be changed by giving ``sort_keys`` a false value (see
        `Boolean arguments`). Notice that with Python 3.5 and earlier
        dictionary order is undefined unless using ordered dictionaries.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Values | ${D3} |
        | ${unsorted} = | Get Dictionary Values | ${D3} | sort_keys=False |
        =>
        | ${sorted} = [1, 2, 3]
        | ${unsorted} = [2, 1, 3]    # Order depends on Python version.

        ``sort_keys`` is a new option in Robot Framework 3.1.2. Earlier values
        were always sorted based on keys.
        """
        self._validate_dictionary(dictionary)
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [dictionary[k] for k in keys]

    def get_dictionary_items(self, dictionary, sort_keys=True):
        """Returns items of the given ``dictionary`` as a list.

        Uses `Get Dictionary Keys` to get keys and then returns corresponding
        items. By default keys are sorted and items returned in that order,
        but this can be changed by giving ``sort_keys`` a false value (see
        `Boolean arguments`). Notice that with Python 3.5 and earlier
        dictionary order is undefined unless using ordered dictionaries.

        Items are returned as a flat list so that first item is a key,
        second item is a corresponding value, third item is the second key,
        and so on.

        The given ``dictionary`` is never altered by this keyword.

        Example:
        | ${sorted} =   | Get Dictionary Items | ${D3} |
        | ${unsorted} = | Get Dictionary Items | ${D3} | sort_keys=False |
        =>
        | ${sorted} = ['a', 1, 'b', 2, 'c', 3]
        | ${unsorted} = ['b', 2, 'a', 1, 'c', 3]    # Order depends on Python version.

        ``sort_keys`` is a new option in Robot Framework 3.1.2. Earlier items
        were always sorted based on keys.
        """
        self._validate_dictionary(dictionary)
        keys = self.get_dictionary_keys(dictionary, sort_keys=sort_keys)
        return [i for key in keys for i in (key, dictionary[key])]

    def get_from_dictionary(self, dictionary, key, default=NOT_SET):
        """Returns a value from the given ``dictionary`` based on the given ``key``.

        If the given ``key`` cannot be found from the ``dictionary``, this
        keyword fails. If optional ``default`` value is given, it will be
        returned instead of failing.

        The given dictionary is never altered by this keyword.

        Example:
        | ${value} = | Get From Dictionary | ${D3} | b |
        =>
        | ${value} = 2

        Support for ``default`` is new in Robot Framework 6.0.
        """
        self._validate_dictionary(dictionary)
        try:
            return dictionary[key]
        except KeyError:
            if default is not NOT_SET:
                return default
            raise RuntimeError(f"Dictionary does not contain key '{key}'.")

    def dictionary_should_contain_key(self, dictionary, key, msg=None,
                                      ignore_case=False):
        """Fails if ``key`` is not found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dictionary)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(key) in normalize(dictionary),
                          f"Dictionary does not contain key '{key}'.",
                          msg)

    def dictionary_should_not_contain_key(self, dictionary, key, msg=None,
                                          ignore_case=False):
        """Fails if ``key`` is found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dictionary)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(key) not in normalize(dictionary),
                          f"Dictionary contains key '{key}'.",
                          msg)

    def dictionary_should_contain_item(self, dictionary, key, value, msg=None,
                                       ignore_case=False):
        """An item of ``key`` / ``value`` must be found in a ``dictionary``.

        Value is converted to unicode for comparison.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dictionary)
        normalize = Normalizer(ignore_case).normalize
        self.dictionary_should_contain_key(dictionary, key, msg, ignore_case)
        assert_equal(normalize(dictionary[normalize(key)]), normalize(value),
                     msg or f"Value of dictionary key '{key}' does not match",
                     values=not msg)

    def dictionary_should_contain_value(self, dictionary, value, msg=None,
                                        ignore_case=False):
        """Fails if ``value`` is not found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dictionary)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(value) in normalize(dictionary).values(),
                          f"Dictionary does not contain value '{value}'.",
                          msg)

    def dictionary_should_not_contain_value(self, dictionary, value, msg=None,
                                            ignore_case=False):
        """Fails if ``value`` is found from ``dictionary``.

        Use the ``msg`` argument to override the default error message.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dictionary)
        normalize = Normalizer(ignore_case).normalize
        _verify_condition(normalize(value) not in normalize(dictionary).values(),
                          f"Dictionary contains value '{value}'.",
                          msg)

    def dictionaries_should_be_equal(self, dict1, dict2, msg=None, values=True,
                                     ignore_keys=None, ignore_case=False):
        """Fails if the given dictionaries are not equal.

        First the equality of dictionaries' keys is checked and after that all
        the key value pairs. If there are differences between the values, those
        are listed in the error message. The types of the dictionaries do not
        need to be same.

        ``ignore_keys`` can be used to provide a list of keys to ignore in the
        comparison. It can be an actual list or a Python list literal. This
        option is new in Robot Framework 6.1.

        Examples:
        | Dictionaries Should Be Equal | ${dict} | ${expected} |
        | Dictionaries Should Be Equal | ${dict} | ${expected} | ignore_keys=${ignored} |
        | Dictionaries Should Be Equal | ${dict} | ${expected} | ignore_keys=['key1', 'key2'] |

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dict1)
        self._validate_dictionary(dict2, 2)
        if ignore_keys:
            if isinstance(ignore_keys, str):
                try:
                    ignore_keys = literal_eval(ignore_keys)
                except Exception:
                    raise ValueError("Converting 'ignore_keys' to a list failed: "
                                     + get_error_message())
            if not is_list_like(ignore_keys):
                raise ValueError(f"'ignore_keys' must be list-like, "
                                 f"got {type_name(ignore_keys)}.")
            dict1 = {k: v for k, v in dict1.items() if k not in ignore_keys}
            dict2 = {k: v for k, v in dict2.items() if k not in ignore_keys}
        keys = self._keys_should_be_equal(dict1, dict2, msg, values, ignore_case)
        self._key_values_should_be_equal(keys, dict1, dict2, msg, values, ignore_case)

    def dictionary_should_contain_sub_dictionary(self, dict1, dict2, msg=None,
                                                 values=True, ignore_case=False):
        """Fails unless all items in ``dict2`` are found from ``dict1``.

        See `Lists Should Be Equal` for more information about configuring
        the error message with ``msg`` and ``values`` arguments.

        The ignore_case argument can be used to make comparison case-insensitive.
        See the Ignore case section for more details. It is new in Robot Framework 7.0.
        """
        self._validate_dictionary(dict1)
        self._validate_dictionary(dict2, 2)
        normalize = Normalizer(ignore_case).normalize
        keys2 = self.get_dictionary_keys(dict2)
        diffs = ', '.join(str(k) for k in normalize(keys2) if k
                          not in normalize(dict1))
        _verify_condition(not diffs,
                          f"Following keys missing from first dictionary: {diffs}",
                          msg, values)
        keys = [(key1, key2) for key1, key2 in
                zip(dict1.keys(), dict2.keys()) if normalize(key1) == normalize(key2)]
        self._key_values_should_be_equal(keys, dict1, dict2, msg,
                                         values, ignore_case)

    def log_dictionary(self, dictionary, level='INFO'):
        """Logs the size and contents of the ``dictionary`` using given ``level``.

        Valid levels are TRACE, DEBUG, INFO (default), and WARN.

        If you only want to log the size, use keyword `Get Length` from
        the BuiltIn library.
        """
        self._validate_dictionary(dictionary)
        logger.write('\n'.join(self._log_dictionary(dictionary)), level)

    def _log_dictionary(self, dictionary):
        if not dictionary:
            yield 'Dictionary is empty.'
        elif len(dictionary) == 1:
            yield 'Dictionary has one item:'
        else:
            yield f'Dictionary size is {len(dictionary)} and it contains following items:'
        for key in self.get_dictionary_keys(dictionary):
            yield f'{key}: {dictionary[key]}'

    def _keys_should_be_equal(self, dict1, dict2, msg, values, ignore_case):
        normalize = Normalizer(ignore_case).normalize
        keys1 = self.get_dictionary_keys(normalize(dict1))
        keys2 = self.get_dictionary_keys(normalize(dict2))
        miss1 = ', '.join(str(k) for k in keys2 if k
                          not in normalize(dict1))
        miss2 = ', '.join(str(k) for k in keys1 if k
                          not in normalize(dict2))
        error = []
        if miss1:
            error += [f'Following keys missing from first dictionary: {miss1}']
        if miss2:
            error += [f'Following keys missing from second dictionary: {miss2}']
        if len(set(normalize(dict1).keys()))!=len(dict1.keys()):
            error += ["First dictionary contains duplicate keys after normalizing."]
        if len(set(normalize(dict2).keys()))!=len(dict2.keys()):
            error += ["Second dictionary contains duplicate keys after normalizing."]
        _verify_condition(not error, '\n'.join(error), msg, values)
        keys = [(key1, key2) for key1, key2 in
                zip(dict1.keys(), dict2.keys()) if normalize(key1) == normalize(key2)]
        return keys

    def _key_values_should_be_equal(self, keys, dict1, dict2, msg, values, ignore_case):
        diffs = '\n'.join(self._yield_dict_diffs(keys, dict1,
                                dict2, ignore_case))
        _verify_condition(not diffs,
                          f'Following keys have different values:\n{diffs}',
                          msg, values)

    def _yield_dict_diffs(self, keys, dict1, dict2, ignore_case):
        normalize = Normalizer(ignore_case).normalize
        for k1, k2 in keys:
            try:
                assert_equal(normalize(dict1[k1]),
                             normalize(dict2[k2]), msg=f'Key {k1}')
            except AssertionError as err:
                yield str(err)

    def _validate_dictionary(self, dictionary, position=1):
        if not is_dict_like(dictionary):
            raise TypeError(f"Expected argument {position} to be a dictionary or "
                            f"dictionary-like, got {type_name(dictionary)} instead.")

class Collections(_List, _Dictionary):
    """A library providing keywords for handling lists and dictionaries.

    ``Collections`` is Robot Framework's standard library that provides a
    set of keywords for handling Python lists and dictionaries. This
    library has keywords, for example, for modifying and getting
    values from lists and dictionaries (e.g. `Append To List`, `Get
    From Dictionary`) and for verifying their contents (e.g. `Lists
    Should Be Equal`, `Dictionary Should Contain Value`).

    == Table of contents ==

    %TOC%

    = Related keywords in BuiltIn =

    Following keywords in the BuiltIn library can also be used with
    lists and dictionaries:

    | = Keyword Name =             | = Applicable With = |
    | `Create List`                | lists |
    | `Create Dictionary`          | dicts |
    | `Get Length`                 | both  |
    | `Length Should Be`           | both  |
    | `Should Be Empty`            | both  |
    | `Should Not Be Empty`        | both  |
    | `Should Contain`             | both  |
    | `Should Not Contain`         | both  |
    | `Should Contain X Times`     | lists |
    | `Should Not Contain X Times` | lists |
    | `Get Count`                  | lists |

    = Using with list-like and dictionary-like objects =

    List keywords that do not alter the given list can also be used
    with tuples, and to some extend also with other iterables.
    `Convert To List` can be used to convert tuples and other iterables
    to Python ``list`` objects.

    Similarly dictionary keywords can, for most parts, be used with other
    mappings. `Convert To Dictionary` can be used if real Python ``dict``
    objects are needed.

    = Boolean arguments =

    Some keywords accept arguments that are handled as Boolean values true or
    false. If such an argument is given as a string, it is considered false if
    it is an empty string or equal to ``FALSE``, ``NONE``, ``NO``, ``OFF`` or
    ``0``, case-insensitively. Keywords verifying something that allow dropping
    actual and expected values from the possible error message also consider
    string ``no values`` to be false. Other strings are considered true
    regardless their value, and other argument types are tested using the same
    [http://docs.python.org/library/stdtypes.html#truth|rules as in Python].

    True examples:
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=True    | # Strings are generally true.    |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=yes     | # Same as the above.             |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=${TRUE} | # Python ``True`` is true.       |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=${42}   | # Numbers other than 0 are true. |

    False examples:
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=False    | # String ``false`` is false.   |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=no       | # Also string ``no`` is false. |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=${EMPTY} | # Empty string is false.       |
    | `Should Contain Match` | ${list} | ${pattern} | case_insensitive=${FALSE} | # Python ``False`` is false.   |
    | `Lists Should Be Equal` | ${x}   | ${y} | Custom error | values=no values | # ``no values`` works with ``values`` argument |

    Considering ``OFF`` and ``0`` false is new in Robot Framework 3.1.

    = Data in examples =

    List related keywords use variables in format ``${Lx}`` in their examples.
    They mean lists with as many alphabetic characters as specified by ``x``.
    For example, ``${L1}`` means ``['a']`` and ``${L3}`` means
    ``['a', 'b', 'c']``.

    Dictionary keywords use similar ``${Dx}`` variables. For example, ``${D1}``
    means ``{'a': 1}`` and ``${D3}`` means ``{'a': 1, 'b': 2, 'c': 3}``.

    = Ignore case =

    It is possible to ignore the case for elements in both dictionaries and lists.
    In lists, this can be done by adding ``ignore_case=True``. For dictionaries,
    there are additional options since they employ both keys and values, using
    ignore_case equal to ``key``, ``value`` or ``both``. Ignoring case means that the
    values to compare are normalized by lowercasing strings before comparison.

    Be aware that dictionaries containing keys that would be equal after normalization,
    e.g. ``{'a': 1, 'A':2}`` can not be used, as this would result in equal keys within
    the same dictionary.

    Additionally, be aware that list-like objects are converted to lists, and
    dictionary-like objects to dictionaries, for ease of comparison

    List Examples:
    | `Lists should be equal` | ${list1} | ${list} | ignore_case=True   | # String ``true`` is True.   |
    | `Lists should be equal` | ${list1} | ${list} | ignore_case=False  | # String ``false`` is False. |

    Dictionary Examples:
    | `Dictionaries should be equal` | ${dict1} | ${dict2} | ignore_case=True   | # String ``true`` is True.   |
    | `Dictionaries should be equal` | ${dict1} | ${dict2} | ignore_case=both   | # Case will be ignored on keys and values    |
    | `Dictionaries should be equal` | ${dict1} | ${dict2} | ignore_case=key    | # Case will be ignored on keys, not values   |
    | `Dictionaries should be equal` | ${dict1} | ${dict2} | ignore_case=value  | # Case will be ignored on values, not keys   |
    | `Dictionaries should be equal` | ${dict1} | ${dict2} | ignore_case=False  | # String ``false`` is False. |
    """

    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    ROBOT_LIBRARY_VERSION = get_version()

    def should_contain_match(self, list, pattern, msg=None,
                             case_insensitive=False,
                             whitespace_insensitive=False):
        """Fails if ``pattern`` is not found in ``list``.

        By default, pattern matching is similar to matching files in a shell
        and is case-sensitive and whitespace-sensitive. In the pattern syntax,
        ``*`` matches to anything and ``?`` matches to any single character. You
        can also prepend ``glob=`` to your pattern to explicitly use this pattern
        matching behavior.

        If you prepend ``regexp=`` to your pattern, your pattern will be used
        according to the Python
        [http://docs.python.org/library/re.html|re module] regular expression
        syntax. Important note: Backslashes are an escape character, and must
        be escaped with another backslash (e.g. ``regexp=\\\\d{6}`` to search for
        ``\\d{6}``). See `BuiltIn.Should Match Regexp` for more details.

        If ``case_insensitive`` is given a true value (see `Boolean arguments`),
        the pattern matching will ignore case.

        If ``whitespace_insensitive`` is given a true value (see `Boolean
        arguments`), the pattern matching will ignore whitespace.

        Non-string values in lists are ignored when matching patterns.

        Use the ``msg`` argument to override the default error message.

        See also ``Should Not Contain Match``.

        Examples:
        | Should Contain Match | ${list} | a*              | | | # Match strings beginning with 'a'. |
        | Should Contain Match | ${list} | regexp=a.*      | | | # Same as the above but with regexp. |
        | Should Contain Match | ${list} | regexp=\\\\d{6} | | | # Match strings containing six digits. |
        | Should Contain Match | ${list} | a*  | case_insensitive=True       | | # Match strings beginning with 'a' or 'A'. |
        | Should Contain Match | ${list} | ab* | whitespace_insensitive=yes  | | # Match strings beginning with 'ab' with possible whitespace ignored. |
        | Should Contain Match | ${list} | ab* | whitespace_insensitive=true | case_insensitive=true | # Same as the above but also ignore case. |
        """
        _List._validate_list(self, list)
        matches = _get_matches_in_iterable(list, pattern, case_insensitive,
                                           whitespace_insensitive)
        default = f"{seq2str2(list)} does not contain match for pattern '{pattern}'."
        _verify_condition(matches, default, msg)

    def should_not_contain_match(self, list, pattern, msg=None,
                                 case_insensitive=False,
                                 whitespace_insensitive=False):
        """Fails if ``pattern`` is found in ``list``.

        Exact opposite of `Should Contain Match` keyword. See that keyword
        for information about arguments and usage in general.
        """
        _List._validate_list(self, list)
        matches = _get_matches_in_iterable(list, pattern, case_insensitive,
                                           whitespace_insensitive)
        default = f"{seq2str2(list)} contains match for pattern '{pattern}'."
        _verify_condition(not matches, default, msg)

    def get_matches(self, list, pattern, case_insensitive=False,
                    whitespace_insensitive=False):
        """Returns a list of matches to ``pattern`` in ``list``.

        For more information on ``pattern``, ``case_insensitive``, and
        ``whitespace_insensitive``, see `Should Contain Match`.

        Examples:
        | ${matches}= | Get Matches | ${list} | a* | # ${matches} will contain any string beginning with 'a' |
        | ${matches}= | Get Matches | ${list} | regexp=a.* | # ${matches} will contain any string beginning with 'a' (regexp version) |
        | ${matches}= | Get Matches | ${list} | a* | case_insensitive=${True} | # ${matches} will contain any string beginning with 'a' or 'A' |
        """
        _List._validate_list(self, list)
        return _get_matches_in_iterable(list, pattern, case_insensitive,
                                        whitespace_insensitive)

    def get_match_count(self, list, pattern, case_insensitive=False,
                        whitespace_insensitive=False):
        """Returns the count of matches to ``pattern`` in ``list``.

        For more information on ``pattern``, ``case_insensitive``, and
        ``whitespace_insensitive``, see `Should Contain Match`.

        Examples:
        | ${count}= | Get Match Count | ${list} | a* | # ${count} will be the count of strings beginning with 'a' |
        | ${count}= | Get Match Count | ${list} | regexp=a.* | # ${matches} will be the count of strings beginning with 'a' (regexp version) |
        | ${count}= | Get Match Count | ${list} | a* | case_insensitive=${True} | # ${matches} will be the count of strings beginning with 'a' or 'A' |
        """
        _List._validate_list(self, list)
        return len(self.get_matches(list, pattern, case_insensitive,
                                    whitespace_insensitive))


def _verify_condition(condition, default_msg, msg, values=False):
    if condition:
        return
    if not msg:
        msg = default_msg
    elif is_truthy(values) and str(values).upper() != 'NO VALUES':
        msg += '\n' + default_msg
    raise AssertionError(msg)


def _get_matches_in_iterable(iterable, pattern, case_insensitive=False,
                             whitespace_insensitive=False):
    if not isinstance(pattern, str):
        raise TypeError(f"Pattern must be string, got '{type_name(pattern)}'.")
    regexp = False
    if pattern.startswith('regexp='):
        pattern = pattern[7:]
        regexp = True
    elif pattern.startswith('glob='):
        pattern = pattern[5:]
    matcher = Matcher(pattern,
                      caseless=is_truthy(case_insensitive),
                      spaceless=is_truthy(whitespace_insensitive),
                      regexp=regexp)
    return [item for item in iterable if isinstance(item, str) and matcher.match(item)]

class Normalizer:
    def __init__(self, ignore_case=False):
        self.ignore_case = ignore_case

    def normalize(self, value):
        if not self.ignore_case:
            return value
        normalize = self.normalize
        if is_dict_like(value):
            if normalize(self.ignore_case)=="key":
                return {normalize(k): value[k] for k in value}
            elif normalize(self.ignore_case)=="value":
                return {k: normalize(value[k]) for k in value}
            elif normalize(self.ignore_case)=="both" or self.ignore_case is True:
                return {normalize(k): normalize(value[k]) for k in value}
        if is_list_like(value):
            return [normalize(v) for v in value]
        if is_string(value):
            return value.lower()
        return value
