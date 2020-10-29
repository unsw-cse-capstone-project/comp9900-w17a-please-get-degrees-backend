from werkzeug.security import generate_password_hash

from simvestr.models import User, Portfolio, PortfolioPrice, db
from simvestr.helpers.db import make_salt


def change_password(user: User, password: str):
    user.salt = make_salt()
    user.password = generate_password_hash(password + user.salt, method="sha256")
    db.session.commit()


def create_new_user(email_id, first_name, last_name, password):
    salt = make_salt()
    pw = "".join([password, salt])
    new_user = User(
        email_id=email_id,
        first_name=first_name,
        last_name=last_name,
        role="user",
        salt=salt,
        password=generate_password_hash(pw, method="sha256")
    )
    db.session.add(new_user)
    db.session.commit()

    new_portfolio = Portfolio(
        portfolio_name=first_name + "'s Portfolio"  # make a portfolio for new user
    )
    new_user.portfolio = new_portfolio
    db.session.add(new_portfolio)
    db.session.commit()

    new_portfolioprice = PortfolioPrice(
        portfolio_id=new_user.portfolio.id,
        close_balance=100000  # give dummy amount of 100k to new user. Value should be imported from a config file.
    )
    new_user.portfolio.portfolioprice.append(new_portfolioprice)
    db.session.add(new_portfolioprice)
    db.session.commit()
    return new_user
