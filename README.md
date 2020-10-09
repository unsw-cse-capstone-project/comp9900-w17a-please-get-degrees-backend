# Investr

Back end of the investment simulator project for COMP9900

## Getting Started
[comment]: <> (TODO)
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
[comment]: <> (TODO: expand on this as we go)
All pre-requisites are listed in [requirements.txt](requirements.txt). They have also been packaged in the distribution if that is teh prefered method for building.


### Dev Setup
[comment]: <> (TODO: check that this procedure works on CSE/team pcs)
First, setup your virtual environment. You can use conda or venv.

#### ```conda```
```
path_to_app $ conda create -n "simvestr" python=3.7.0 flask flask_sqlalchemy
path_to_app $ conda activate simvestr
(simvestr) path_to_app $ 
```

#### ```pip``` 
You must have the correct python version installed (python3.7) when using the pip method
```
path_to_app $ python3.7 -m venv .simvestr
```

##### Activating venv

OSX or Linux:

```
path_to_app $ source .simvestr/bin/activate
(.simvestr) path_to_app $ 
```

Windows:

```
path_to_app>.\simvestr\Scripts\activate
(.simvestr) path_to_app>
```

Now either ```pip``` or ```conda``` install the dependencies:

```
(.simvestr) ($ or >) pip install -r pip_requirments.txt
```

```
(.simvestr) ($ or >) conda install --file conda_requirments.txt
```


### Installation as package

If you git clone the repo it can also be installed as a package in your virtual environment.

```
pip install -e .
```

or you can build from the distribution if you are unable to download packages from pip or conda.

```
pip install dist\simvestr-0.0.1.tar.gz
```

## Running the app

Running the app is as simple as running the [run.py](run.py) file.
```
chmod -x run.py
python run.py
```

## Packaging new versions

To package simply run the [package.py](package.py) file. This will package the app into build and dist directories. Only [dist](dist) is maintained on github.

```
python package.py
```

Note: any additional packages that are required to the app must be added to the requirements files and to the [setup.py](setup.py) file.

## Running the tests
[comment]: <> (TODO)
Explain how to run the automated tests for this system

### Break down into end to end tests

Explain what these tests test and why

```
Give an example
```

### And coding style tests
[comment]: <> (TODO)
Explain what these tests test and why

```
Give an example
```

## Deployment
[comment]: <> (TODO)
Add additional notes about how to deploy this on a live system

## Versioning
[comment]: <> (TODO)
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors
[comment]: <> (TODO)
|Name | zID | Email|
| --- | --- | ---- |
| Jihad Meraachli | z5156156 | j.meraachli@student.unsw.edu.au | 
| Khan Schroder-Turner | z5020362 | k.schroder-turner@student.unsw.edu.au | 
| Kovid Sharma | z5240067 | k.sharma.1@student.unsw.edu.au | 
| Simon Garrod | z3264122 | s.garrod@student.unsw.edu.au | 
| Timothy Brunette | z5233368 | t.brunette@student.unsw.edu.au | /project/contributors) who participated in this project.

## License
[comment]: <> (TODO)
This project is licensed under the GNU AFFERO GENERAL PUBLIC LICENSE v3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
[comment]: <> (TODO)
* Hat tip to anyone whose code was used
* Inspiration
* etc

