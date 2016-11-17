import logging

import ldap
from ldap.ldapobject import LDAPObject
from ldap.controls import SimplePagedResultsControl

from .utils import get_setting


logger = logging.getLogger(__name__)


class LDAPSearch(object):
    _ldap = None

    def __init__(self):
        self.uri = get_setting('LDAP_SYNC_URI', strict=True)
        self.base_user = get_setting('LDAP_SYNC_BASE_USER', strict=True)
        self.base_pass = get_setting('LDAP_SYNC_BASE_PASS', strict=True)
        self.base = get_setting('LDAP_SYNC_BASE', strict=True)

    def _get_ldap(self):
        if self._ldap is None:
            self._ldap = self.connect()
        return self._ldap
    ldap = property(_get_ldap)

    def connect(self):
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = PagedLDAPObject(self.uri)
        l.protocol_version = 3
        try:
            l.simple_bind_s(self.base_user, self.base_pass)
        except ldap.LDAPError as e:
            logger.error("Error connecting to %s: %s" % (self.uri, e))
            raise
        return l

    def disconnect(self):
        self.ldap.unbind_s()
        self._ldap = None

    def search(self, filterstr, attrlist):
        """
        Query the configured LDAP server with the provided search filter and
        attribute list.
        """
        return self.ldap.paged_search_ext_s(self.base, ldap.SCOPE_SUBTREE, filterstr, attrlist)


class PagedResultsSearchObject:
    """
    Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
    the paged results control: https://bitbucket.org/jaraco/python-ldap/
    """
    page_size = get_setting('LDAP_SYNC_PAGE_SIZE', default=100)

    def paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0,
                           serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0):
        """
        Behaves exactly like LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.
        """
        req_ctrl = SimplePagedResultsControl(True, size=self.page_size, cookie='')

        # Send first search request
        msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr, attrlist=attrlist,
                                serverctrls=(serverctrls or []) + [req_ctrl])
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
                    msgid = self.search_ext(base, ldap.SCOPE_SUBTREE, filterstr, attrlist=attrlist,
                                            serverctrls=(serverctrls or []) + [req_ctrl])
                else:
                    break

        return results


class PagedLDAPObject(LDAPObject, PagedResultsSearchObject):
    pass
