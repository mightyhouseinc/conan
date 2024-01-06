from conans.errors import ConanException


def users_list(localdb, remotes):
    if not remotes:
        raise ConanException("No remotes defined")

    remotes_info = []
    for remote in remotes:
        user, token, _ = localdb.get_login(remote.url)
        user_info = {
            "name": remote.name,
            "user_name": user,
            "authenticated": bool(token),
        }
        remotes_info.append(user_info)
    return remotes_info


def users_clean(localdb, remote_url=None):
    localdb.clean(remote_url=remote_url)


def user_set(localdb, user, remote_name=None):
    if user == "":
        user = None
    return update_localdb(localdb, user, token=None, refresh_token=None, remote=remote_name)


def update_localdb(localdb, user, token, refresh_token, remote):
    previous_user = localdb.get_username(remote.url)
    localdb.store(user, token, refresh_token, remote.url)
    return remote.name, previous_user, user
