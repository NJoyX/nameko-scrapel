from setuptools import setup, find_packages

extras_secure = ["urllib3[secure]"]
extras_socks = ["urllib3[socks]"]
extras_all = extras_secure + extras_socks

setup(
    name='nameko-scrapel',
    version='0.1-rc',
    description='@TODO',
    long_description='@TODO',
    author='Fill Q',
    author_email='fill@njoyx.net',
    url='https://github.com/NJoyX/nameko-scrapel',
    license='Apache License, Version 2.0',
    packages=find_packages(exclude=('mock',)),
    install_requires=[
        "nameko",
        "marshmallow",
        "pytz",
        "six",
        "w3lib",
        "parsel",
        "urllib3",
        "lazy-object-proxy",
        "sortedcontainers"
    ],
    extras_require={
        'secure': extras_secure,
        'socks': extras_socks,
        'all': extras_all
    },
    include_package_data=True,
    zip_safe=True,
    keywords=['nameko', 'scrape', 'scrapy', 'distributed'],
    classifiers=[
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Intended Audience :: Developers",
    ]
)
