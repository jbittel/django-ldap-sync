import logging

import ldap
from ldap.ldapobject import LDAPObject
from ldap.controls import SimplePagedResultsControl


logger = logging.getLogger(__name__)


class LDAPSearch(object):
    _ldap = None

    def __init__(self, settings):
        self.settings = settings

    def _get_ldap(self):
        if self._ldap is None:
            self._ldap = self.bind()
        return self._ldap
    ldap = property(_get_ldap)

    def bind(self):
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(self.settings.URI)
        l.protocol_version = 3
        try:
            l.simple_bind_s(self.settings.BASE_USER, self.settings.BASE_PASS)
        except ldap.LDAPError as e:
            logger.error("Error connecting to %s: %s" % (self.uri, e))
            raise
        return l

    def unbind(self):
        self.ldap.unbind_s()
        self._ldap = None

    def search(self, filterstr, attrlist):
        """Query the configured LDAP server."""
        return self.ldap.paged_search_ext_s(self.settings.BASE, ldap.SCOPE_SUBTREE, filterstr=filterstr,
                                            attrlist=attrlist, page_size=self.settings.PAGE_SIZE)


class PagedResultsSearchObject:
    """
    Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
    the paged results control: https://bitbucket.org/jaraco/python-ldap/
    """
    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0,
                           serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0, page_size=10):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        """
        req_ctrl = SimplePagedResultsControl(True, size=page_size, cookie='')

        # Send first search request
        msgid = self.search_ext(base, scope, filterstr=filterstr, attrlist=attrlist, attrsonly=attrsonly,
                                serverctrls=(serverctrls or []) + [req_ctrl], clientctrls=clientctrls,
                                timeout=timeout, sizelimit=sizelimit)
        results = []

        while True:
            rtype, rdata, rmsgid, rctrls = self.result3(msgid)
            results.extend(rdata)
            # Extract the simple paged results response control
            pctrls = [c for c in rctrls if c.controlType == SimplePagedResultsControl.controlType]

            if pctrls:
                if pctrls[0].cookie:
                    # Copy cookie from response control to request control
                    req_ctrl.cookie = pctrls[0].cookie
                    msgid = self.search_ext(base, scope, filterstr=filterstr, attrlist=attrlist, attrsonly=attrsonly,
                                            serverctrls=(serverctrls or []) + [req_ctrl], clientctrls=clientctrls,
                                            timeout=timeout, sizelimit=sizelimit)
                else:
                    break

        return results


class PagedLDAPObject(LDAPObject, PagedResultsSearchObject):
    pass
