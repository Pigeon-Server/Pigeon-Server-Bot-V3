import sys
from unittest import TestCase

from src.module.permission_node import PermissionManager


class TestPermissionManager(TestCase):
    def test_permission_del_normal_1(self):
        expect_result: list = ["test.test2", "test.test3", "test.test4"]
        permission: list = ["-test.test", "test.test", "test.test2", "test.test3", "test.test4"]
        res = PermissionManager._permission_del(permission)
        print(f"{'-' * 10}\n"
              f"Expect result: {expect_result}\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertListEqual(expect_result, res)

    def test_permission_del_normal_2(self):
        expect_result: list = ["test.test2", "test.test4", "test.test.test2"]
        permission: list = ["-test.test", "-test.test3", "-test.test6",
                            "test.test", "test.test2", "test.test3",
                            "test.test4", "test.test.test", "test.test.test2",
                            "-test.test.test"]
        res = PermissionManager._permission_del(permission)
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: {expect_result}\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertListEqual(expect_result, res)

    def test_permission_del_all_1(self):
        expect_result: list = ["test1.test"]
        permission: list = ["-test.*", "test.test", "test.test2", "test.test3", "test1.test"]
        res = PermissionManager._permission_del(permission)
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: {expect_result}\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertListEqual(expect_result, res)

    def test_permission_del_all_2(self):
        expect_result: list = []
        permission: list = ["-*.*", "test.test", "test.test2", "test.test3"]
        res = PermissionManager._permission_del(permission)
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: {expect_result}\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertListEqual(expect_result, res)

    def test_check_permission_exist(self):
        permission: list = ["test.test", "test.test2", "test.test3"]
        res = PermissionManager._check_permission(permission, "test.test")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: True\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertTrue(res)

    def test_check_permission_not_exist(self):
        permission: list = ["test.test", "test.test2", "test.test3"]
        res = PermissionManager._check_permission(permission, "test.test4")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: False\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertFalse(res)

    def test_check_permission_with_asterisk_exist(self):
        permission: list = ["test.*"]
        res = PermissionManager._check_permission(permission, "test.test4")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: True\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertTrue(res)

    def test_check_permission_with_asterisk_not_exist(self):
        permission: list = ["test.*"]
        res = PermissionManager._check_permission(permission, "test2.test4")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: False\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertFalse(res)

    def test_check_permission_all_exist(self):
        permission: list = ["*.*"]
        res = PermissionManager._check_permission(permission, "test2.test4")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: True\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertTrue(res)

    def test_check_permission_multistage_exist(self):
        permission: list = ["test.*", "test.test", "test.test2", "test.test3"]
        res = PermissionManager._check_permission(permission, "test.test.test.test.test")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: True\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertTrue(res)

    def test_check_permission_multistage_not_exist(self):
        permission: list = ["test.test", "test.test2", "test.test3"]
        res = PermissionManager._check_permission(permission, "test.test.test.test.test")
        print(f"{'-' * 10}\n"
              f"Function: {sys._getframe().f_code.co_name}\n"
              f"Expect result: False\n"
              f"Actual result: {res}\n"
              f"{'-' * 10}")
        self.assertFalse(res)

    def test_check_permission_exception(self):
        permission: list = ["test.test", "test.test2", "test.test3"]
        try:
            PermissionManager._check_permission(permission, "test.*.test.test.test")
        except Exception as e:
            print(f"{'-' * 10}\n"
                  f"Function: {sys._getframe().f_code.co_name}\n"
                  f"Expect result: {ValueError("test.*.test.test.test")}\n"
                  f"Actual result: {e}\n"
                  f"{'-' * 10}")
            self.assertIsInstance(e, ValueError)
