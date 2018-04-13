## Style Guide

The primary goal is to produce readable code.
This means being consistent with patterns and style prefered by most python developers at corporations that build great stuff with python.


### [PEP8](https://www.python.org/dev/peps/pep-0008/) with these exceptions

Follow the [Hettinger interpretation of PEP8](https://www.youtube.com/watch?v=wf-BqAjZb8M) for beautiful, readable code.

* max line length is "about" 120 chars (if you go a little over, don't worry about it)
* max complexity: "mccabe_threshold": 12,  # McCabe complexity checker limits the number of conditional branches
* type hints are a good idea on conditional branches that are rarely run, but duck-typing is preferred for mainline code

Here's my Sublime Anaconda plugin configuration.


```javascript
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
def add(value, num=0):
    """ Add a float to an integer

    Args:
        value (float): first number in the sum
        num (int): the integer to be added

    Returns:
        float: the sum of `value + num`

    >>> add(1., 2)
    3.0
    """
    pass
```


### Workflow

#### Branch off master

whenever you begin a new feature/task:

`git checkout master -b feature/my-awesome-new-feature`

#### Commit often

Mentioning the Jira ticket number in your, brief, active verb-tense comment (message)

`git commit -am 'NSF-4 #start-review integrate location into description'`

#### Transition your Jira Tickets

Whenever you can, so save yourself the Jira GUI shuffle. But send it to "#start-review" (the QA stage) rather than #done:

`git commit -am 'NSF-4 #start-review add color vectors'`

