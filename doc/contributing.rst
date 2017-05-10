============
Contributing
============

Setting up
----------

To install the dependencies, run::

    $ pip install -r requirements.txt

while you have a `virtual environment <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_
activated.

You are recommended to use `pyenv <https://github.com/yyuu/pyenv>`_ to handle
virtual environments and Python versions. That way, you can easily test and
debug problems that are specific to one version of Python.

Testing
-------

You can perform an integration test by running ``podgen/__main__.py``::

    $ python -m podgen

When working on this project, you should run the unit tests as well as the
integration test, like this::

    $ make test

The unit tests reside in ``podgen/tests`` and are written using the
:mod:`unittest` module.


Values
------

Read :doc:`/user/introduction` and :doc:`/user/fork` for a run-down on what
values/principles lay the foundation for this project. In short, it is important
to keep the API as simple as possible.

You must also write unittests as you code, ideally using **test-driven
development** (that is, write a test, observe that the test fails, write code
so the test works, observe that the test succeeds, write a new test and so on).
That way, you know that the tests actually contribute and you get to think
about how the API will look before you tackle the problem head-on.

Make sure you update ``podgen/__main__.py`` so it still works, and use your new
functionality there if it makes sense.

You must also make sure you **update any relevant documentation**. Remember that
the documentation includes lots of examples and also describes the API
independently from docstring comments in the code itself.

Pull requests in which the unittests and documentation are NOT up to date
with the code will NOT be accepted.

Lastly, a single **commit** shouldn't include more changes than it needs. It's better to do a big
change in small steps, each of which is one commit. Explain the impact of your
changes in the commit message.

The Workflow
------------

#. Check out `waffle.io <https://waffle.io/tobinus/python-podgen>`_ or
   `GitHub Issues <https://github.com/tobinus/python-podgen/issues>`_.

   * Find the issue you wish to work on.
   * Add your issue if it's not already there.
   * Discuss the issue and get feedback on your proposed solution. Don't waste
     time on a solution that might not be accepted!

#. Work on the issue in a separate branch which follows the name scheme
   ``tobinus/python-podgen#<issue-number>-<brief-description>`` in your own fork. To be honest, I
   don't know if Waffle.io will notice that, but it doesn't hurt to try, I
   guess! You might want to read up on `Waffle.io's recommended workflow <https://github.com/waffleio/waffle.io/wiki/Recommended-Workflow-Using-Pull-Requests-&-Automatic-Work-Tracking>`_.

#. Push the branch.

#. Do the work.

#. When you're done and you've updated the documentation and tests (see above),
   create a pull request which references the issue.

#. Wait for me or some other team member to review the pull request. Keep an
   eye on your inbox or your GitHub notifications, since we may have some
   objections or feedback that you must take into consideration. **It'd be a
   shame if your work never led to anything because you didn't notice a
   comment!**

#. Consider making the same changes to `python-feedgen <https://github.com/lkiesow/python-feedgen>`_
   as well.
