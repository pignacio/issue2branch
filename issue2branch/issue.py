from .format import colorize
from .color import green

class Issue(object):
    def __init__(self, issue_id, title, tag=None, parent=None, priority=None,
                 status=None, assignee=None):
        self.issue_id = issue_id
        self.title = title
        self.tag = tag
        self.parent = parent
        self.childs = {}
        self.priority = priority
        self.status = status
        self.assignee = assignee

    def text(self):
        if self.priority or self.status:
            texts = [colorize(t) for t in (self.priority, self.status, ) if t]
            status = "[{}] - ".format("/".join(texts))
        else:
            status = ""
        tag = colorize("{}: ".format(self.tag), self.tag)
        if self.assignee:
            assignee = green("({})".format(self.assignee))
            assignee = " - {}".format(assignee)
        else:
            assignee = ""
        return "{} - {}{}{}{}".format(self.issue_id, status, tag, self.title,
                                    assignee)

    def branch(self):
        return "{}-{}-{}".format(self.tag, self.issue_id, self.title)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag or "Issue"

