# PyBind11 + Scikit Build example


## Building

To build, you must have pip 10 or greater, *or* you need to manually install
`scikit-build` and `cmake`. Once you create a wheel, that wheel can be used in
earlier versions of pip.

Example build and install sequence:

```bash
pip install .
python -c "import hello; hello.hello()"
```

This should print "Hello, World!".

```
