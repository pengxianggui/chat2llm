from server.db.models.client_model import ClientModel
from server.db.session import with_session


@with_session
def add_client(session, client_id, client_key, client_secret, description):
    client = session.query(ClientModel).filter_by(id=client_id).first()
    if not client:
        client = ClientModel(id=client_id, client_key=client_key, client_secret=client_secret, description=description)
        session.add(client)
    else:
        if not client_key and not client_secret:
            client.client_key = client_key
            client.client_secret = client_secret
        if not description:
            client.description = description

    return ClientModel(id=client_id, client_key=client_key, client_secret=client_secret, description=description)


@with_session
def get_client(session, client_id):
    client = session.query(ClientModel).filter_by(id=client_id).first()
    if not client:
        return None
    else:
        return ClientModel(id=client.id, client_key=client.client_key, client_secret="***",
                           description=client.description, enable=client.enable, create_time=client.create_time)


@with_session
def get_client_secret(session, client_id):
    client = session.query(ClientModel).filter_by(id=client_id).first()
    if not client:
        return None
    else:
        return client.client_key, client.client_secret, client.enable


@with_session
def delete_client(session, client_id):
    # TODO
    return True
