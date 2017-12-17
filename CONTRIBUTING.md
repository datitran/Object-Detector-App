## Style Guide

The primary goal is to produce readable code.
This means being consistent with patterns used by many people, except when the "crowd" favors less readable layout or syntax.


### [PEP8](https://www.python.org/dev/peps/pep-0008/) with these exceptions

Follow the [Hettinger interpretation of PEP8](https://www.youtube.com/watch?v=wf-BqAjZb8M) for beautiful, readable code.

* max line length is "about" 120 chars
* max complexity: mccabe_threshold": 12,  # threshold limit for McCabe complexity checker.
* type hints are encouraged but not required

Here's my Sublime Anaconda plugin configuration.


```json
{
    // Maximum McCabe complexity (number of conditional branches within a function).
    "mccabe_threshold": 7,

    // Maximum line length
    "pep8_max_line_length": 120
}
```


### Documentation

Markdown README.md files in any folder containing significant code.

Use [Google/Numpy/Napolean/Markdown](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html) docstring syntax, **not** the original ReST dosctring format.


#### Example Dosstring


```python
def add(value, num=0)
    """ Add a float to an integer

    Args:
        value (float): first number in the sum
        num (int): the integer to be added

    Returns:
        float: the sum of `value + num`

    >>> add(1., 2)
    3.0
    """
```


### Workflow

* branch off master whenever you begin a new feature/task
* commit often, mentioning the Jira ticket number in the comment, where possible (e.g. NSF-4)
* brief active voice comments, with optional Jira transition commands: `git commit -am 'NSF-4 #start-review integrate location and color vectors'`)
