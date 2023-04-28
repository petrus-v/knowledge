# Copyright 2022-2023 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo.tests import new_test_user, HttpCase, SavepointCase
from odoo.exceptions import AccessError


def create_attachment(env, user, name, model=False, res_id=False):
    return (
        env["ir.attachment"]
        .with_user(user)
        .create(
            {
                "name": name,
                "datas": base64.b64encode(b"\xff data"),
                "res_model": model,
                "res_id": res_id,
            }
        )
    )


class TestAttachmentZippedDownload(HttpCase):
    def setUp(self):
        super().setUp()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        self.user = new_test_user(
            self.env,
            login="test-user",
            password="test-user",
            context=ctx,
        )
        test_1 = create_attachment(self.user, "test1.txt")
        test_2 = create_attachment(self.user, "test2.txt")
        self.attachments = test_1 + test_2 + test_3


    def test_action_attachments_download(self):
        self.authenticate("test-user", "test-user")
        res = self.attachments.action_attachments_download()
        response = self.url_open(res["url"], timeout=20)
        self.assertEqual(response.status_code, 200)


class TestAttachmentZippedDownload(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ctx = {
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "mail_notrack": True,
            "no_reset_password": True,
        }
        cls.user = new_test_user(
            cls.env,
            login="test-user",
            password="test-user",
            groups="base.group_user,base.group_partner_manager",
            context=ctx,
        )
        test_1 = create_attachment(cls.env, cls.user, "test1.txt")
        test_2 = create_attachment(cls.env, cls.user, "test2.txt")
        test_3 = create_attachment(cls.env, cls.user, "test3.txt", model="res.partner", res_id=cls.user.partner_id.id)
        cls.attachments = test_1 + test_2 + test_3


    def test_create_temp_zip(self):
        res = self.attachments._create_temp_zip()
        self.assertTrue(res)

    def test_create_temp_zip_access_denined(self):
        attachments = self.attachments | create_attachment(
            self.env, self.uid, "test4.txt", model="ir.ui.view", res_id=self.env.ref("base.view_view_form").id
        )
        with self.assertRaises(AccessError):
            attachments._create_temp_zip()