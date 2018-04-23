pyash
=====

A tool to manage simple accounting from a plain text file.


Purpose
-------

The purpose of this tool is to manage accounting for the French speaking Python
User Group (www.afpy.org).

We just wanted to manage accounting in a plain text file (just like `ledger
<http://www.ledger-cli.org/>`_ does, but without double entry accounting).

This project is just a set of tools we use in order to achieve that.


How to
------

The easiest way to use Pyash is to install it in a virtual environment using
`Pipenv <https://docs.pipenv.org/>`_.

.. code-block:: shell

  $ pipenv install -e .
  $ pipenv run pyash -h


Dependencies
------------

Pyash is written for Python3.

The only dependencies are `Jinja2 <http://jinja.pocoo.org/>`_ used to format
text output, and `chut <https://pypi.org/project/chut/>`_ used to build
the CLI.


Format
------

Our data file is made of money moves.

A money move is composed of a date, an amount, a kind, a category, a status, a
description and a comment.

Here is an example :

.. code-block:: text

  2013/07/04 -100.00€ Check Category X
      Description
      Comment

The first line is composed of a date (formatted with '%Y/%m/%d'), an amount
(signed float and an € symbol), a move kind (check, order, etc.), a category
(used as a grouper in reports) and a status (X for executed, P for pending).

The description is a single line.

The comment is a block beginning with 4 spaces, it can be on multiple lines.


Tests
-----

.. code-block:: shell

  $ pipenv run python setup.py test
