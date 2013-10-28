pyash
=====

A simple tool to manage simple accounting from a plain text file.

Purpose
-------

The purpose of this tool is to manage accounting for the French speaking Python User Group (www.afpy.org).

We just wanted to manage accounting in a plain text file (just like `ledger <http://www.ledger-cli.org/>`_ does, but without double entry accounting).

This project is just a set of tool we use in order to achieve that.

Dependencies
------------

Pyash is written for Python3.

The only dependency is `Jinja2 <http://jinja.pocoo.org/>`_, used to format text output.

.. code-block:: shell

  $ pip install jinja2
  $ pip install .

Or use buildout::

  $ python bootsrap.py
  $ bin/buildout

How to
------

.. code-block:: shell

  pyash -h

Format
------

Our data file is made of money moves.

A money move is composed of a date, an amount, a category and a description.

Here is an example :

.. code-block:: text

  2013/07/04 -100.00€ Check Category X
      Description
      Comment

The first line is composed of a date (formatted with '%Y/%m/%d'), a space, an amount (signed float and an € symbol), and a category.

The description is a single line.

The comment is a block beginning with 4 spaces, it can be on multiple lines.
