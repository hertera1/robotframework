*** Settings ***
Test Setup        Create Dictionaries For Testing
Resource          collections_resources.robot
Library           CollectionsHelperLibrary.py

*** Test Cases ***
Convert To Dictionary
    ${dotted} =    Create Dictionary    a=1    b=2
    Should Be True    type($dotted) is not dict
    ${normal} =    Convert To Dictionary    ${dotted}
    Should Be True    type($normal) is dict
    Should Be Equal    ${dotted}    ${normal}

Set To Dictionary
    Set To Dictionary    ${D0}    a    ${1}
    Should Be Equal    ${D0}    ${D1}
    Set To Dictionary    ${D0}    b    ${2}    ${3}    ${None}
    Should Be Equal    ${D0}    ${D3}

Set To Dictionary With wrong number of arguments
    [Documentation]    FAIL ValueError: Adding data to a dictionary failed. There should be even number of key-value-pairs.
    Set To Dictionary    ${D0}    a

Set To Dictionary With **kwargs
    Set To Dictionary    ${D0}    k1    ${1}    over    write    k2=${2}    over=written
    Compare To Expected String    ${D0}    {'k1': 1, 'k2': 2, 'over': 'written'}

Remove From Dictionary
    Remove From Dictionary    ${D3}    b    x    ${2}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}
    Remove From Dictionary    ${D3}    ${TUPLE}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}

Keep In Dictionary
    Keep In Dictionary    ${D3}    a    x    ${2}    ${3}
    Compare To Expected String    ${D3}    {'a': 1, 3: None}

Copy Dictionary
    ${copy} =    Copy Dictionary    ${D3}
    Remove From Dictionary    ${copy}    a    ${3}
    Compare To Expected String    ${copy}    {'b':2}
    Compare To Expected String    ${D3}    {'a': 1, 'b': 2, 3: None}

Shallow Copy Dictionary
    ${x2} =    Create Dictionary    x2    1
    ${a} =    Create Dictionary    x1    ${x2}
    ${b} =    Copy Dictionary    ${a}
    Set To Dictionary    ${a['x1']}    x2    2
    Should Be Equal    ${a['x1']['x2']}    2
    Should Be Equal    ${b['x1']['x2']}    2

Deep Copy Dictionary
    ${x2} =    Create Dictionary    x2    1
    ${a} =    Create Dictionary    x1    ${x2}
    ${b} =    Copy Dictionary    ${a}    deepcopy=True
    Set To Dictionary    ${a['x1']}    x2    2
    Set To Dictionary    ${b['x1']}    x2    3
    Should Be Equal    ${a['x1']['x2']}    2
    Should Be Equal    ${b['x1']['x2']}    3

Get Dictionary Keys Sorted
    ${keys} =    Get Dictionary Keys    ${D3B}
    Compare To Expected String    ${keys}    ['a', 'b', 'c']

Get Dictionary Keys Unsorted
    ${keys} =    Get Dictionary Keys    ${D3B}    sort_keys=${False}
    Compare To Expected String    ${keys}    ['b', 'a', 'c']

Get Dictionary Values Sorted
    ${values} =    Get Dictionary Values    ${D3B}
    Compare To Expected String    ${values}    [1, 2, '']

Get Dictionary Values Unsorted
    ${values} =    Get Dictionary Values    ${D3B}  sort_keys=False
    Compare To Expected String    ${values}    [2, 1, '']

Get Dictionary Items Sorted
    ${items} =    Get Dictionary Items    ${D3B}
    Compare To Expected String    ${items}    ['a', 1, 'b', 2, 'c', '']

Get Dictionary Items Unsorted
    ${items} =    Get Dictionary Items    ${D3B}    sort_keys=NO
    Compare To Expected String    ${items}    ['b', 2, 'a', 1, 'c', '']

Get Dictionary Keys/Values/Items When Keys Are Unorderable
    ${unorderable} =    Evaluate    {complex(1): 1, complex(2): 2, complex(3): 3}
    ${keys} =    Get Dictionary Keys    ${unorderable}
    Compare To Expected String    ${keys}    list(d)    d=${unorderable}
    ${values} =    Get Dictionary Values    ${unorderable}
    Compare To Expected String    ${values}    list(d.values())    d=${unorderable}
    ${items} =    Get Dictionary Items    ${unorderable}
    Compare To Expected String    ${items}    [i for item in d.items() for i in item]    d=${unorderable}

Get From Dictionary
    ${value} =    Get From Dictionary    ${D3}    b
    Should Be Equal As Integers    ${value}    2

Get From Dictionary With Invalid Key 1
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Get From Dictionary    ${D3}    x

Get From Dictionary With Invalid Key 2
    [Documentation]    FAIL Dictionary does not contain key '(1, 2)'.
    Get From Dictionary    ${D3}    ${TUPLE}

Get From Dictionary With Default
    ${dict} =    Create Dictionary    a=a    b=b
    ${value} =    Get From Dictionary    ${dict}    x     default_value
    Should Be Equal    ${value}    default_value
    ${value} =    Get From Dictionary    ${dict}    a     default_value
    Should Be Equal    ${value}    a

Dictionary Should Contain Key
    Dictionary Should Contain Key    ${D3}    a

Dictionary Should Contain Key With Missing Key 1
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Dictionary Should Contain Key    ${D3}    x

Dictionary Should Contain Key With Missing Key 2
    [Documentation]    FAIL Dictionary does not contain key '(1, 2)'.
    Dictionary Should Contain Key    ${D3}    ${TUPLE}

Dictionary Should Contain Item
    Dictionary Should Contain Item    ${D3}    a    ${1}

Dictionary Should Contain Item With Missing Key
    [Documentation]    FAIL Dictionary does not contain key 'x'.
    Dictionary Should Contain Item    ${D3}    x    1

Dictionary Should Contain Item With Wrong Value
    [Documentation]    FAIL Value of dictionary key 'a' does not match: 1 != 2
    Dictionary Should Contain Item    ${D3}    a    2

Dictionary Should Contain Item With Value Looking Same But With Different Type
    [Documentation]    FAIL Value of dictionary key 'a' does not match: 1 (integer) != 1 (string)
    Dictionary Should Contain Item    ${D3}    a    1

Dictionary Should Contain Item With Custom Message
    [Documentation]    FAIL Custom message
    Dictionary Should Contain Item    ${D3}    a    1    Custom message

Dictionary Should Not Contain Key
    Dictionary Should Not Contain Key    ${D3}    x
    Dictionary Should Not Contain Key    ${D3}    ${TUPLE}

Dictionary Should Not Contain Key With Existing Key
    [Documentation]    FAIL Dictionary contains key 'b'.
    Dictionary Should Not Contain Key    ${D3}    b

Dictionary Should (Not) Contain Key Does Not Require `has_key`
    ${dict} =    Get Dict Without Has Key    name=value
    Dictionary Should Contain Key    ${dict}    name
    Dictionary Should Not Contain Key    ${dict}    nonex

Dictionary Should Contain Value
    Dictionary Should Contain Value    ${D3}    ${2}

Dictionary Should Contain Value With Missing Value 1
    [Documentation]    FAIL Dictionary does not contain value 'x'.
    Dictionary Should Contain Value    ${D3}    x

Dictionary Should Contain Value With Missing Value 2
    [Documentation]    FAIL Dictionary does not contain value '(1, 2)'.
    Dictionary Should Contain Value    ${D3}    ${TUPLE}

Dictionary Should Not Contain Value
    Dictionary Should Not Contain Value    ${D3}    x
    Dictionary Should Not Contain Value    ${D3}    ${TUPLE}

Dictionary Should Not Contain Value With Existing Value
    [Documentation]    FAIL Dictionary contains value '2'.
    Dictionary Should Not Contain Value    ${D3}    ${2}

Dictionaries Should Be Equal
    Dictionaries Should Be Equal    ${D0}    ${D0}
    Dictionaries Should Be Equal    ${D3}    ${D3}
    Dictionaries Should Be Equal    ${BIG}    ${BIG}

Dictionaries Should Be Equal With Keys In Different Order
    [Setup]  Create Dictionaries For Testing
    Dictionaries Should Be Equal    ${D4}    ${D4B}

Dictionaries Of Different Type Should Be Equal
    ${big2}=    Evaluate    collections.OrderedDict($BIG)    modules=collections
    Dictionaries Should Be Equal    ${BIG}    ${big2}

Dictionaries Should Equal With First Dictionary Missing Keys
    [Documentation]    FAIL Following keys missing from first dictionary: 3
    Dictionaries Should Be Equal    ${D2}    ${D3}

Dictionaries Should Equal With Second Dictionary Missing Keys
    [Documentation]    FAIL Following keys missing from second dictionary: a, b
    Dictionaries Should Be Equal    ${D2}    ${D0}

Dictionaries Should Equal With Both Dictionaries Missing Keys
    [Documentation]    FAIL
    ...    Following keys missing from first dictionary: c, d
    ...    Following keys missing from second dictionary: b
    ${x}    ${y} =    Evaluate    dict(a=1, b=2), dict(a=0, c=3, d=4)
    Dictionaries Should Be Equal    ${x}    ${y}

Dictionaries Should Be Equal With Different Keys And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionaries Should Be Equal    ${D2}    ${D3}    My error message!    NO values

Dictionaries Should Be Equal With Different Keys And Own And Default Error Messages
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys missing from first dictionary: 3
    Dictionaries Should Be Equal    ${D2}    ${D3}    My error message!    values=yes

Dictionaries Should Be Equal With Different Values
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionaries Should Be Equal    ${D2}    ${D2B}

Dictionaries Should Be Equal With Different Values And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionaries Should Be Equal    ${D2}    ${D2B}    My error message!    False

Dictionaries Should Be Equal With Different Values And Own And Default Error Messages
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionaries Should Be Equal    ${D2}    ${D2B}    My error message!

Dictionaries Should Equal With Ignored Keys
    ${x}    ${y}     ${z} =    Evaluate    dict(a=1, b=2), dict(a=1, b=2, d=4), list('d')
    Dictionaries Should Be Equal    ${x}    ${y}    ignore_keys=${z}

Dictionaries Should Equal With Ignored Keys And Missing Key
    [Documentation]    FAIL
    ...    Following keys missing from first dictionary: c
    ${x}    ${y}     ${z} =    Evaluate    dict(a=1, b=2), dict(a=1, b=2, c=3, d=4), list('d')
    Dictionaries Should Be Equal    ${x}    ${y}    ignore_keys=${z}

Dictionaries Should Equal With Ignored Keys And Missing Key And Own Error Message
    [Documentation]    FAIL My error message!
    ...    Following keys missing from first dictionary: c
    ${x}    ${y}     ${z} =    Evaluate    dict(a=1, b=2), dict(a=1, b=2, c=3, d=4), list('d')
    Dictionaries Should Be Equal    ${x}    ${y}    My error message!    ignore_keys=${z}

Dictionaries Should Equal with non-list ignored keys
    [Documentation]    FAIL ValueError: 'ignore_keys' must be list-like, got integer.
    ${x}    ${y} =    Evaluate    dict(a=1, b=2), dict(a=1, b=2, d=4)
    Dictionaries Should Be Equal    ${x}    ${y}    ignore_keys=42

Dictionaries Should Equal with invalid ignored keys
    [Documentation]    FAIL STARTS: ValueError: Converting 'ignore_keys' to a list failed: SyntaxError:
    ${x}    ${y} =    Evaluate    dict(a=1, b=2), dict(a=1, b=2, d=4)
    Dictionaries Should Be Equal    ${x}    ${y}    ignore_keys=!?#

Dictionary Should Contain Sub Dictionary
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2}
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D0}

Dictionary Should Contain Sub Dictionary With Missing Keys
    [Documentation]    FAIL Following keys missing from first dictionary: 3
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}

Dictionary Should Contain Sub Dictionary With Missing Keys And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}    My error message!    False

Dictionary Should Contain Sub Dictionary With Missing Keys And Own And Default Error Message
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys missing from first dictionary: 3
    Dictionary Should Contain Sub Dictionary    ${D2}    ${D3}    My error message!

Dictionary Should Contain Sub Dictionary With Different Value
    [Documentation]    FAIL
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}

Dictionary Should Contain Sub Dictionary With Different Value And Own Error Message
    [Documentation]    FAIL My error message!
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}    My error message!    False

Dictionary Should Contain Sub Dictionary With Different Value And Own And Default Error Message
    [Documentation]    FAIL
    ...    My error message!
    ...    Following keys have different values:
    ...    Key a: 1 (integer) != 1 (string)
    ...    Key b: 2 != x
    Dictionary Should Contain Sub Dictionary    ${D3}    ${D2B}    My error message!

Log Dictionary With Different Log Levels
    Log Dictionary    ${D3B}
    Log Dictionary    ${D3B}    tRAce
    Log Dictionary    ${D3B}    warn
    Log Dictionary    ${D3B}    DEbug
    Log Dictionary    ${D3B}    INFO

Log Dictionary With Different Dictionaries
    Log Dictionary    ${D0}
    Log Dictionary    ${D1}
    ${dict} =    Evaluate    collections.OrderedDict(((True, 'xxx'), ('foo', []), ((1, 2, 3), 3.14)))   modules=collections
    Log Dictionary    ${dict}

Pop From Dictionary Without Default
    [Documentation]   FAIL Dictionary does not contain key 'a'.
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a
    Should be equal    ${a}    val
    Should be True   $dict == {'b': 'val2'}
    Pop From Dictionary    ${dict}    a

Pop From Dictionary With Default
    ${dict} =    Create Dictionary    a=val    b=val2
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should be equal    ${a}    val
    Should be True   $dict == {'b': 'val2'}
    ${a} =    Pop From Dictionary    ${dict}    a   foo
    Should be equal    ${a}    foo
    Should be True   $dict == {'b': 'val2'}

Check invalid dictionary argument errors
    [Template]    Validate invalid argument error
    Copy dictionary
    Dictionary Should Contain Item             I'm not a dict, I'm string.    a    b
    Dictionaries Should Be Equal               I'm not a dict, I'm string.    ${D2}
    Dictionaries Should Be Equal               ${D2}    I'm not a dict, I'm string.    position=2
    Dictionary Should Contain Key              I'm not a dict, I'm string.    a
    Dictionary Should Contain Sub Dictionary   I'm not a dict, I'm string.    ${D2}
    Dictionary Should Contain Sub Dictionary   ${D2}    I'm not a dict, I'm string.    position=2
    Dictionary Should Contain Value            I'm not a dict, I'm string.    a
    Dictionary Should Not Contain Key          I'm not a dict, I'm string.    a
    Dictionary Should Not Contain Value        I'm not a dict, I'm string.    a
    Get Dictionary Items
    Get Dictionary Keys
    Get Dictionary Values
    Get from dictionary                        I'm not a dict, I'm string.    a
    Keep in dictionary                         I'm not a dict, I'm string.    a
    Log Dictionary
    Pop From Dictionary                        I'm not a dict, I'm string.    a
    Remove From Dictionary                     I'm not a dict, I'm string.    a
    Set To Dictionary                          I'm not a dict, I'm string.    a    b

Dictionaries Should Be Equal With Ignore Case
    [Template]    Dictionaries Should Be Equal
    [Setup]    Create Dictionaries For Testing Ignore Case
    dict1=${D0}    dict2=${D1}    ignore_case=${True}
    dict1=${D0}    dict2=${D1}    ignore_case=both
    dict1=${D0}    dict2=${D2}    ignore_case=key
    dict1=${D0}    dict2=${D3}    ignore_case=value

Dictionaries Should Be Equal Without Ignoring Wrong Case
    [Documentation]  FAIL Following keys missing from first dictionary: A, B, C
    ...   Following keys missing from second dictionary: a, b, c
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionaries Should Be Equal    dict1=${D0}    dict2=${D1}

Dictionary Should Contain Item With Ignore Case
    [Template]    Dictionary Should Contain Item
    [Setup]    Create Dictionaries For Testing Ignore Case
    dictionary=${D0}    key=A    value=x    ignore_case=${True}
    dictionary=${D0}    key=A    value=x    ignore_case=BOTH
    dictionary=${D0}    key=A    value=X    ignore_case=keY
    dictionary=${D0}    key=a    value=x    ignore_case=VAlue

Dictionary Should Contain Item Without Ignoring Wrong Case
    [Documentation]  FAIL Dictionary does not contain key 'A'.
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionary Should Contain Item    dictionary=${D0}    key=A    value=x

Dictionary Should Contain Key With Ignore Case
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionary Should Contain Key    dictionary=${D0}    key=A    ignore_case=${True}

Dictionary Should Contain Key Without Ignoring Wrong Case
    [Documentation]  FAIL Dictionary does not contain key 'A'.
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionary Should Contain Key    dictionary=${D0}    key=A

Dictionary Should Not Contain Key With Ignore Case Does Contain Key
    [Setup]    Create Dictionaries For Testing Ignore Case
    [Documentation]  FAIL Dictionary contains key 'A'.
    Dictionary Should Not Contain Key    dictionary=${D0}    key=A    ignore_case=${True}

Dictionary Should Contain Value With Ignore Case
    [Template]    Dictionary Should Contain Value
    [Setup]    Create Dictionaries For Testing Ignore Case
    dictionary=${D0}    value=x    ignore_case=${True}
    dictionary=${D7}  value=${D1_lower}    ignore_case=${True}

Dictionary Should Contain Value Without Ignoring Wrong Case
    [Documentation]  FAIL Dictionary does not contain value 'x'.
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionary Should Contain Value  dictionary=${D0}    value=x

Dictionary Should Not Contain Value With Ignore Case Does Contain Value
    [Setup]    Create Dictionaries For Testing Ignore Case
    [Documentation]  FAIL Dictionary contains value 'x'.
    Dictionary Should Not Contain Value    dictionary=${D0}    value=x    ignore_case=${True}

Dictionary Should Contain Sub Dictionary With Ignore Case
    [Template]    Dictionary Should Contain Sub Dictionary
    [Setup]    Create Dictionaries For Testing Ignore Case
    dict1=${D0}    dict2=${D4}    ignore_case=${True}
    dict1=${D0}    dict2=${D4}    ignore_case=both
    dict1=${D0}    dict2=${D5}    ignore_case=key
    dict1=${D0}    dict2=${D6}    ignore_case=value

Dictionary Should Contain Sub Dictionary Without Ignoring Wrong Case
    [Setup]    Create Dictionaries For Testing Ignore Case
    [Documentation]  FAIL Following keys missing from first dictionary: A
    Dictionary Should Contain Sub Dictionary   dict1=${D0}    dict2=${D4}

Dictionary Should Contain Value With Ignore Case And Nested List and Dictionary
    [Setup]    Create Dictionaries For Testing Ignore Case
    Dictionary Should Contain Value  ${D7}  value=d    ignore_case=${True}

Dictionaries Should Be Equal With Keys In Different Order And Ignore Case
    [Setup]  Create Dictionaries For Testing Ignore Case
    Dictionaries Should Be Equal    ${D8}    ${D8B}  ignore_case=both
    Dictionaries Should Be Equal    ${D8}    ${D8B}  ignore_case=key
    Dictionaries Should Be Equal    ${D8B}   ${D8C}  ignore_case=value

Dictionaries With Equally Named Keys After Normalizing Cannot Ignore Case
    [Documentation]  FAIL  	First dictionary contains duplicate keys after normalizing.
    ...   Second dictionary contains duplicate keys after normalizing.
    [Setup]  Create Dictionaries For Testing Ignore Case
    Dictionaries Should Be Equal    ${D9}    ${D9B}  ignore_case=both

*** Keywords ***
Validate invalid argument error
    [Arguments]  ${keyword}    ${argument}=I'm not a dict, I'm a string.    @{args}    ${type}=string    ${position}=1
    Run keyword and expect error
    ...    TypeError: Expected argument ${position} to be a dictionary or dictionary-like, got ${type} instead.
    ...    ${keyword}    ${argument}    @{args}

Create Dictionaries For Testing
    ${D0}    Create Dictionary
    Set Test Variable    \${D0}
    ${D1} =    Create Dictionary    a=${1}
    Set Test Variable    \${D1}
    ${D2} =    Create Dictionary    a=${1}    b=${2}
    Set Test Variable    \${D2}
    ${D2B} =    Create Dictionary    a=1    b=x
    Set Test Variable    \${D2B}
    ${D3}    Create Dictionary    a=${1}    b=${2}    ${3}=${None}
    Set Test Variable    \${D3}
    ${D3B}    Create Dictionary    b=${2}    a=${1}    c=
    Set Test Variable    \${D3B}
    ${BIG} =    Evaluate    {'a': 1, 'B': 2, 3: [42], 'd': '', '': 'e', (): {}}
    Set Test Variable    \${BIG}
    ${TUPLE} =    Evaluate    (1, 2)
    Set Test Variable    \${TUPLE}
    ${D4} =    Create Dictionary    a=1    b=2    c=3    d=4    e=5
    Set Test Variable    \${D4}
    ${D4B} =    Create Dictionary    d=4    b=2    e=5    a=1    c=3
    Set Test Variable    \${D4B}

Create Dictionaries For Testing Ignore Case
    ${D0}    Create Dictionary    a=X    b=Y    c=Z
    Set Test Variable    \${D0}
    ${D1}    Create Dictionary    A=x    B=y    C=z
    Set Test Variable    \${D1}
    ${D1_lower}    Create Dictionary    a=x    b=y    c=z
    Set Test Variable    \${D1_lower}
    ${D2}    Create Dictionary    A=X    B=Y    C=Z
    Set Test Variable    \${D2}
    ${D3}    Create Dictionary    a=x    b=y    c=z
    Set Test Variable    \${D3}
    ${D4}    Create Dictionary    A=x    b=Y
    Set Test Variable    \${D4}
    ${D5}    Create Dictionary    A=X    b=Y
    Set Test Variable    \${D5}
    ${D6}    Create Dictionary    a=x    b=Y
    Set Test Variable    \${D6}
    ${L0}    Create List  1  2  3
    ${D7}    Create Dictionary    1=${D0}  2=D  c=${L0}  d=3
    Set Test Variable    \${D7}
    ${D8} =    Create Dictionary     A=1    b=2    c=3    d=4    E=5
    Set Test Variable    \${D8}
    ${D8B} =    Create Dictionary    D=4    b=2    E=5    a=1    C=3
    Set Test Variable    \${D8B}
    ${D8C} =    Create Dictionary    E=5    D=4    C=3    b=2    a=1
    Set Test Variable    \${D8C}
    ${D9} =    Create Dictionary    A=1  a=2
    Set Test Variable    \${D9}
    ${D9B} =    Create Dictionary    A=1  a=2
    Set Test Variable    \${D9B}