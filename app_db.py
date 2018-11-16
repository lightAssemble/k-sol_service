from pony.orm import Database


def _parse(cs: str):
    user_pass, host_port_dbname = cs.replace("postgres://", "").split("@")
    host_port, db_name = host_port_dbname.split("/")
    user, passw = user_pass.split(":")
    host, port = host_port.split(":")
    return dict(
        user=user,
        password=passw,
        host=host,
        port=port,
        database=db_name,
    )


def get(connection_string) -> Database:
    db = Database()
    if connection_string:
        db.bind(provider='postgres', **_parse(connection_string))
    else:
        db.bind(provider='sqlite', filename='./db.sqlite', create_db=True)
    return db
