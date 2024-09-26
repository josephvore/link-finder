from setuptools import setup, find_packages

setup(
    name='link-finder',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'hrequests==0.8.2',
        'ultimate-sitemap-parser==0.5',
        'courlan==1.3.0',
    ],
    entry_points={
        'console_scripts': [
            'gather_urls = gather_urls.gather_urls:main',
        ],
    },
    description='A tool to crawl websites and gather all valid Internal URLs.',
    author='Joseph Vore',
    author_email='joseph@connectmodern.com',
    url='https://github.com/josephvore/gather_urls',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
    ],
)
