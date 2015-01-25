from .format import colorize
from .color import green, magenta

class Issue(object):
    def __init__(self, issue_id, title, tag=None, parent=None, priority=None,
                 status=None, assignee=None, project=None):
        self.issue_id = issue_id
        self.title = title
        self._tag = None
        self.tag = tag
        self.parent = parent
        self.childs = {}
        self.priority = priority
        self.status = status
        self.assignee = assignee
        self.project = project

    def text(self):
        if self.priority or self.status:
            texts = [colorize(t) for t in (self.priority, self.status, ) if t]
            status = " [{}] -".format("/".join(texts))
        else:
            status = ""
        tag = colorize(" {}: ".format(self.tag), self.tag)
        if self.assignee:
            assignee = green("({})".format(self.assignee))
            assignee = " - {}".format(assignee)
        else:
            assignee = ""
        if self.project:
            project = magenta(" {{{}}}".format(self.project))
        else:
            project = ''

        return "{} -{}{}{}{}{}".format(self.issue_id, status, project, tag,
                                       self.title, assignee)

    def branch(self):
        return "{}-{}-{}".format(self.tag, self.issue_id, self.title)

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, tag):
        self._tag = tag or "Issue"

