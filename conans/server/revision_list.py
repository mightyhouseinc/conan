import json
from collections import namedtuple

from conans.util.dates import revision_timestamp_now

_RevisionEntry = namedtuple("RevisionEntry", "revision time")


class RevisionList(object):

    def __init__(self):
        self._data = []

    @staticmethod
    def loads(contents):
        ret = RevisionList()
        ret._data = [_RevisionEntry(e["revision"], e["time"])
                     for e in json.loads(contents)["revisions"]]
        return ret

    def dumps(self):
        return json.dumps({"revisions": [{"revision": e.revision,
                                          "time": e.time} for e in self._data]})

    def add_revision(self, revision_id):
        lt = self.latest_revision()
        if lt and lt.revision == revision_id:
            # Each uploaded file calls to update the revision
            return
        if index := self._find_revision_index(revision_id):
            self._data.pop(index)

        self._data.append(_RevisionEntry(revision_id, self._now()))

    @staticmethod
    def _now():
        return revision_timestamp_now()

    def latest_revision(self):
        return None if not self._data else self._data[-1]

    def get_time(self, revision):
        tmp = self._find_revision_index(revision)
        return None if tmp is None else self._data[tmp].time

    def as_list(self):
        return list(reversed(self._data))

    def remove_revision(self, revision_id):
        index = self._find_revision_index(revision_id)
        if index is None:
            return
        self._data.pop(index)

    def _find_revision_index(self, revision_id):
        return next(
            (i for i, rev in enumerate(self._data) if rev.revision == revision_id),
            None,
        )

    def __eq__(self, other):
        return self.dumps() == other.dumps()
