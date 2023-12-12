from server.db.models.user_model import UserModel
from server.db.session import with_session


@with_session
def add_user(session, client_id, user_id, username):
    user = session.query(UserModel).filter_by(client_id=client_id, user_id=user_id).first()
    if not user:
        user = UserModel(client_id=client_id, user_id=user_id, username=username)
        session.add(user)
    return UserModel(client_id=user.client_id, user_id=user.user_id, username=user.username, enable=user.enable,
                     create_time=user.create_time)


@with_session
def get_user(session, client_id, user_id):
    user = session.query(UserModel).filter_by(client_id=client_id, user_id=user_id).first()
    if user is None:
        return None

    return UserModel(user_id=user.user_id, client_id=user.client_id, username=user.username, enable=user.enable,
                     create_time=user.create_time)
