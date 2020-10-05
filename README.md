# Investr

Back end of the investment simulator project for COMP9900

## Getting Started
[comment]: <> (TODO)
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
[comment]: <> (TODO: expand on this as we go)
Currently we only need Flask and FlaskSQLAlchemy. 


### Dev Setup
[comment]: <> (TODO: check that this procedure works on CSE/team pcs)
First, setup your virtual environment. You can use conda or venv.

####```conda```
```
path_to_app $ conda create -n "investr" python=3.7.0 flask flask_sqlalchemy
path_to_app $ conda activate investr
(investr) path_to_app $ 
```

####  ```pip``` 
You must have the correct python version installed (python3.7) when using the pip method
```
path_to_app $ python3.7 -m venv .investr
```

##### Activating venv

OSX or Linux:

```
path_to_app $ source .investr/bin/activate
(.investr) path_to_app $ 
```

Windows:

```
path_to_app>.\investr\Scripts\activate
(.investr) path_to_app>
```

Now ```pip``` install the dependencies:

```
(.investr) ($ or >) pip install flask flask_sqlalchemy
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using it for a little demo

### Installation as package

If you git clone the repo it can also be installed as a package in your virtual environment.

```
pip install -e .
```

This will access the [setup.py](setup.py) file and run setuptools.

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

## Built With
[comment]: <> (TODO)
* [Dropwizard](http://www.dropwizard.io/1.0.2/docs/) - The web framework used
* [Maven](https://maven.apache.org/) - Dependency Management
* [ROME](https://rometools.github.io/rome/) - Used to generate RSS Feeds

## Contributing
[comment]: <> (TODO)
Please read [CONTRIBUTING.md](https://gist.github.com/PurpleBooth/b24679402957c63ec426) for details on our code of conduct, and the process for submitting pull requests to us.

## Versioning
[comment]: <> (TODO)
We use [SemVer](http://semver.org/) for versioning. For the versions available, see the [tags on this repository](https://github.com/your/project/tags). 

## Authors
[comment]: <> (TODO)
* **Billie Thompson** - *Initial work* - [PurpleBooth](https://github.com/PurpleBooth)

See also the list of [contributors](https://github.com/your/project/contributors) who participated in this project.

## License
[comment]: <> (TODO)
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments
[comment]: <> (TODO)
* Hat tip to anyone whose code was used
* Inspiration
* etc

