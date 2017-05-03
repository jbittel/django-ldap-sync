import logging

import ldap
from ldap.controls import SimplePagedResultsControl


logger = logging.getLogger(__name__)


class LDAPSearch(object):
    _ldap = None

    def __init__(self, settings):
        self.settings = settings

    def __del__(self):
        self._unbind()

    @property
    def ldap(self):
        if self._ldap is None:
            self._ldap = self._bind()
        return self._ldap

    def _bind(self):
        ldap.set_option(ldap.OPT_REFERRALS, 0)
        l = ldap.initialize(self.settings.URI)
        l.protocol_version = ldap.VERSION3
        try:
            l.simple_bind_s(self.settings.BASE_USER, self.settings.BASE_PASS)
        except ldap.LDAPError as e:
            logger.error("Error connecting to %s: %s" % (self.settings.URI, e))
            raise
        return l

    def _unbind(self):
        if self._ldap is not None:
            self.ldap.unbind_s()
            self._ldap = None

    def search(self, filterstr, attrlist):
        """Query the configured LDAP server."""
        return self._paged_search_ext_s(self.settings.BASE, ldap.SCOPE_SUBTREE, filterstr=filterstr,
                                        attrlist=attrlist, page_size=self.settings.PAGE_SIZE)

    def _paged_search_ext_s(self, base, scope, filterstr='(objectClass=*)', attrlist=None, attrsonly=0,
                            serverctrls=None, clientctrls=None, timeout=-1, sizelimit=0, page_size=10):
        """
        Behaves similarly to LDAPObject.search_ext_s() but internally uses the
        simple paged results control to retrieve search results in chunks.

        Taken from the python-ldap paged_search_ext_s.py demo, showing how to use
        the paged results control: https://bitbucket.org/jaraco/python-ldap/
        """
        request_ctrl = SimplePagedResultsControl(True, size=page_size, cookie='')

        # Send first search request
        msgid = self.ldap.search_ext(base, scope, filterstr=filterstr, attrlist=attrlist, attrsonly=attrsonly,
                                     serverctrls=(serverctrls or []) + [request_ctrl], clientctrls=clientctrls,
                                     timeout=timeout, sizelimit=sizelimit)
        results = []

        while True:
            result_type, result_data, result_msgid, result_ctrls = self.ldap.result3(msgid)
            results.extend(result_data)

            # Extract the simple paged results response control
            paged_ctrls = [c for c in result_ctrls if c.controlType == SimplePagedResultsControl.controlType]

            if paged_ctrls and paged_ctrls[0].cookie:
                # Copy cookie from response control to request control
                request_ctrl.cookie = paged_ctrls[0].cookie
                msgid = self.ldap.search_ext(base, scope, filterstr=filterstr, attrlist=attrlist,
                                             attrsonly=attrsonly, serverctrls=(serverctrls or []) + [request_ctrl],
                                             clientctrls=clientctrls, timeout=timeout, sizelimit=sizelimit)
            else:
                break

        return results
