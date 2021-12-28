"""
MWE for issue
"""
from skbuild import setup

if __name__ == '__main__':
    setup(
        package_dir={
            '': 'src/python/',
        },
        name='my_skb_mod',
        version='0.1.0',
        # develop mode doesnt work without this hack
        # packages=['', 'my_skb_mod', 'my_skb_mod.submod'],  # sort of works? but also warns?
        packages=['my_skb_mod', 'my_skb_mod.submod'],  # works for wheel install
        # packages=['my_skb_mod'],  # works for develop install

        # This package data seems like it is not respected.
        package_data={
            'my_skb_mod.submod': [
                'module_resouce.json'
            ],
        },
    )
