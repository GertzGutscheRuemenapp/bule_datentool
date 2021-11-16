from django.http import HttpRequest

from rest_framework_gis.fields import GeoJsonDict
from django.utils.encoding import force_text
from rest_framework import status

from datentool_backend.user.factories import ProfileFactory
from django.contrib.auth.models import Permission
from datentool_backend.rest_urls import router


class CompareAbsURIMixin:
    """
    Mixin thats provide a method
    to compare lists of relative with absolute url
    """
    @property
    def build_absolute_uri(self):
        """return the absolute_uri-method"""
        request = HttpRequest()
        request.META = self.client._base_environ()
        return request.build_absolute_uri

    def assertURLEqual(self, url1, url2, msg=None):
        """Assert that two urls are equal, if they were absolute urls"""
        absurl1 = self.build_absolute_uri(url1)
        absurl2 = self.build_absolute_uri(url2)
        self.assertEqual(absurl1, absurl2, msg)

    def assertURLsEqual(self, urllist1, urllist2, msg=None):
        """
        Assert that two lists of urls are equal, if they were absolute urls
        the order does not matter
        """
        absurlset1 = {self.build_absolute_uri(url) for url in urllist1}
        absurlset2 = {self.build_absolute_uri(url) for url in urllist2}
        self.assertSetEqual(absurlset1, absurlset2, msg)


class LoginTestCase:

    user = 99
    permissions = Permission.objects.all()

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.profile = ProfileFactory(id=cls.user,
                                    user__id=cls.user,
                                    user__username='Anonymus User')

    def setUp(self):
        self.client.force_login(user=self.profile.user)
        super().setUp()

    def tearDown(self):
        self.client.logout()
        super().tearDown()

    @classmethod
    def tearDownClass(cls):
        user = cls.profile.user
        user.delete()
        cls.profile.delete()
        del cls.profile
        super().tearDownClass()


class BasicModelReadTest(LoginTestCase, CompareAbsURIMixin):
    baseurl = 'http://testserver'
    url_key = ""
    sub_urls = []
    url_pks = dict()
    url_pk = dict()
    do_not_check = []

    def test_list(self):
        """Test that the list view can be returned successfully"""
        self.get_check_200(self.url_key + '-list', **self.url_pks)

    def test_detail(self):
        """Test get, put, patch methods for the detail-view"""
        url = self.url_key + '-detail'
        kwargs = {**self.url_pks, 'pk': self.obj.pk}

        # test get
        response = self.get_check_200(url, **kwargs)
        assert response.data['id'] == self.obj.pk

    def assert_response_equals_expected(self, response_value, expected):
        """
        Assert that response_value equals expected
        If response_value is a GeoJson, then compare the texts
        """
        if isinstance(response_value, GeoJsonDict):
            self.assertJSONEqual(force_text(response_value), expected)
        else:
            self.assertEqual(force_text(response_value), force_text(expected))

    def test_get_urls(self):
        """get all sub-elements of a list of urls"""
        url = self.url_key + '-detail'
        response = self.get_check_200(url, pk=self.obj.pk, **self.url_pks)
        for key in self.sub_urls:
            key_response = self.get_check_200(response.data[key])

    def get_check_200(self, url, **kwargs):
        assert url in [r.name for r in router.urls], f'URL {url} not in routes'
        response = self.get(url, **kwargs)
        self.response_200(response, msg=response.content)
        return response


class BasicModelTest(BasicModelReadTest):
    post_urls = []
    post_data = dict()
    put_data = dict()
    patch_data = dict()

    def test_delete(self):
        """Test delete method for the detail-view"""
        kwargs = {**self.url_pks, 'pk': self.obj.pk, }
        url = self.url_key + '-detail'
        response = self.get_check_200(url, **kwargs)

        response = self.delete(url, **kwargs)
        self.response_204(msg=response.content)

        # it should be deleted and raise 404
        response = self.get(url, **kwargs)
        self.response_404(msg=response.content)

    def test_post(self):
        """Test post method for the detail-view"""
        url = self.url_key + '-list'
        # post
        response = self.post(url, **self.url_pks, data=self.post_data,
                             extra={'format': 'json'})
        self.response_201(msg=response.content)
        for key in self.post_data:
            if key not in response.data.keys() or key in self.do_not_check:
                continue
            response_value = response.data[key]
            expected = self.post_data[key]
            self.assert_response_equals_expected(response_value, expected)

        # get the created object
        new_id = response.data['id']
        url = self.url_key + '-detail'
        self.get_check_200(url, pk=new_id, **self.url_pks)

    def test_post_url_exist(self):
        """post all sub-elements of a list of urls"""
        url = self.url_key + '-detail'
        response = self.get_check_200(url, pk=self.obj.pk, **self.url_pks)
        for url in self.post_urls:
            response = self.get_check_200(url)

    def test_put_patch(self):
        """Test get, put, patch methods for the detail-view"""
        url = self.url_key + '-detail'
        kwargs = {**self.url_pks, 'pk': self.obj.pk, }
        formatjson = dict(format='json')

        # test get
        response = self.get_check_200(url, **kwargs)
        assert response.data['id'] == self.obj.pk

        # check status code for put
        response = self.put(url, **kwargs,
                            data=self.put_data,
                            extra=formatjson)
        self.response_200(msg=response.content)
        assert response.status_code == status.HTTP_200_OK
        # check if values have changed
        response = self.get_check_200(url, **kwargs)
        for key in self.put_data:
            if key not in response.data.keys() or key in self.do_not_check:
                continue
            response_value = response.data[key]
            expected = self.put_data[key]
            self.assert_response_equals_expected(response_value, expected)

        # check status code for patch
        response = self.patch(url, **kwargs,
                              data=self.patch_data, extra=formatjson)
        self.response_200(msg=response.content)

        # check if name has changed
        response = self.get_check_200(url, **kwargs)
        for key in self.patch_data:
            if key not in response.data.keys() or key in self.do_not_check:
                continue
            response_value = response.data[key]
            expected = self.patch_data[key]
            self.assert_response_equals_expected(response_value, expected)


class BasicModelReadPermissionTest(BasicModelReadTest):
    def test_list_permission(self):
        self.profile.user.user_permissions.clear()
        response = self.get(self.url_key + '-list', **self.url_pks)
        self.response_403(msg=response.content)

    def test_get_permission(self):
        self.profile.user.user_permissions.clear()
        url = self.url_key + '-detail'
        kwargs = {**self.url_pks, 'pk': self.obj.pk, }
        response = self.get(url, **kwargs)
        self.response_403(msg=response.content)


class BasicModelWritePermissionTest(BasicModelTest):

    def test_post_permission(self):
        """
        Test if user can post without permission
        """
        self.profile.user.user_permissions.clear()
        url = self.url_key + '-list'
        # post
        response = self.post(url, **self.url_pks, data=self.post_data,
                             extra={'format': 'json'})
        self.response_403(msg=response.content)

    def test_delete_permission(self):
        """
        Test if user can delete without permission
        """
        self.profile.user.user_permissions.clear()
        kwargs = {**self.url_pks, 'pk': self.obj.pk, }
        url = self.url_key + '-detail'
        response = self.delete(url, **kwargs)
        self.response_403(msg=response.content)

    def test_put_permission(self):
        self.profile.user.user_permissions.clear()
        url = self.url_key + '-detail'
        kwargs = {**self.url_pks, 'pk': self.obj.pk, }
        formatjson = dict(format='json')
        response = self.put(url, **kwargs, data=self.put_data,
                            extra=formatjson)
        self.response_403(msg=response.content)


class BasicModelPermissionTest(BasicModelReadPermissionTest,
                               BasicModelWritePermissionTest):
    """
    Test of read and write permissions
    """
